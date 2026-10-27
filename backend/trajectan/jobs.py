"""Durable database outbox with bounded workers and optional Service Bus delivery.
The database owns job state; Service Bus is an at-least-once notification channel.
"""

import asyncio
import os
import time
from sqlalchemy import Column, String, JSON, Float, select, update
from .persistence import Base


class Job(Base):
    __tablename__ = "jobs"
    key = Column(String, primary_key=True)
    request = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="queued")
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    lease_until = Column(Float, nullable=False, default=0)


class LocalQueue:
    mode = "local-durable-development"

    def __init__(self):
        self.queue = asyncio.Queue(maxsize=32)

    async def send(self, key):
        if not self.queue.full():
            await self.queue.put(key)

    async def receive(self):
        return await self.queue.get()

    async def close(self):
        pass


class ServiceBusQueue:
    mode = "azure-service-bus-configured-unverified"

    def __init__(self):
        from azure.servicebus.aio import ServiceBusClient
        from azure.identity.aio import DefaultAzureCredential

        self.credential = DefaultAzureCredential()
        self.client = ServiceBusClient(
            fully_qualified_namespace=os.environ["SERVICE_BUS_NAMESPACE"],
            credential=self.credential,
        )
        self.name = os.environ.get("SERVICE_BUS_QUEUE", "investigations")
        self.receiver = self.client.get_queue_receiver(
            queue_name=self.name, max_wait_time=5
        )

    async def send(self, key):
        from azure.servicebus import ServiceBusMessage

        async with self.client.get_queue_sender(queue_name=self.name) as sender:
            await sender.send_messages(ServiceBusMessage(key, message_id=key))
        self.mode = "azure-service-bus-send-exercised"

    async def receive(self):
        messages = await self.receiver.receive_messages(
            max_message_count=1, max_wait_time=5
        )
        if not messages:
            return None
        message = messages[0]
        key = str(message)
        # Ack delivery, not execution. The durable DB outbox re-sends unfinished work.
        await self.receiver.complete_message(message)
        self.mode = "azure-service-bus-send-receive-exercised"
        return key

    async def close(self):
        await self.receiver.close()
        await self.client.close()
        await self.credential.close()


class Jobs:
    def __init__(self, store, handler, queue=None):
        self.store = store
        self.handler = handler
        self.queue = queue or LocalQueue()
        self.tasks = []
        self.last_error = None
        Base.metadata.create_all(store.engine)

    def get(self, key):
        with self.store.session() as db:
            j = db.get(Job, key)
            return (
                dict(job_id=j.key, status=j.status, result=j.result, error=j.error)
                if j
                else None
            )

    def submit(self, key, request):
        existing = self.get(key)
        if existing:
            return existing
        with self.store.session() as db:
            pending = db.scalars(
                select(Job).where(Job.status.in_(["queued", "running"]))
            ).all()
            if len(pending) >= 8:
                raise ValueError("Work queue is full; retry shortly")
            from sqlalchemy.exc import IntegrityError

            try:
                db.add(Job(key=key, request=request, status="queued", lease_until=0))
                db.commit()
            except IntegrityError:
                db.rollback()
        return self.get(key)

    def pending(self):
        with self.store.session() as db:
            return list(
                db.scalars(
                    select(Job.key).where(
                        Job.status.in_(["queued", "running"]),
                        Job.lease_until < time.time(),
                    )
                )
            )

    def claim(self, key):
        with self.store.session() as db:
            changed = db.execute(
                update(Job)
                .where(
                    Job.key == key,
                    Job.status.in_(["queued", "running"]),
                    Job.lease_until < time.time(),
                )
                .values(status="running", lease_until=time.time() + 300)
            )
            db.commit()
            if changed.rowcount:
                return db.get(Job, key).request
        return None

    def finish(self, key, result=None, error=None):
        with self.store.session() as db:
            db.execute(
                update(Job)
                .where(Job.key == key)
                .values(
                    status="failed" if error else "completed",
                    result=result,
                    error=error,
                    lease_until=0,
                )
            )
            db.commit()

    async def relay(self):
        while True:
            try:
                for key in self.pending():
                    await self.queue.send(key)
                self.last_error = None
            except Exception as e:
                self.last_error = type(e).__name__
            await asyncio.sleep(2)

    async def worker(self):
        while True:
            try:
                key = await self.queue.receive()
                if not key:
                    continue
                request = self.claim(key)
                if not request:
                    continue
                try:
                    result = await asyncio.wait_for(self.handler(request), timeout=240)
                    self.finish(key, result=result)
                except Exception as e:
                    self.finish(
                        key,
                        error=str(e) if isinstance(e, ValueError) else type(e).__name__,
                    )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.last_error = type(e).__name__
                await asyncio.sleep(2)

    def start(self):
        self.tasks = [
            asyncio.create_task(self.relay()),
            *[
                asyncio.create_task(self.worker())
                for _ in range(2 if isinstance(self.queue, LocalQueue) else 1)
            ],
        ]

    async def close(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        await self.queue.close()
