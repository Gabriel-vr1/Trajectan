"""SQLite development fallback / PostgreSQL through the same SQLAlchemy contract."""

import os
import json
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    JSON,
    UniqueConstraint,
    select,
    update,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class InferenceBudget(Base):
    __tablename__ = "inference_budget"
    key = Column(String, primary_key=True)
    used = Column(Integer, nullable=False, default=0)


class Record(Base):
    __tablename__ = "artifacts"
    key = Column(String, primary_key=True)
    kind = Column(String, index=True, nullable=False)
    match_id = Column(String, index=True, nullable=False)
    sequence = Column(Integer, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint("kind", "match_id", "sequence", "key"),)


class Store:
    def __init__(self, url=None):
        self.url = url or os.getenv("DATABASE_URL", "sqlite:///trajectan.db")
        self.engine = create_engine(
            self.url,
            connect_args={"check_same_thread": False}
            if self.url.startswith("sqlite")
            else {},
            pool_pre_ping=True,
        )
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(self.engine)

    def reserve_inference(self, limit):
        """Persistent, atomic global admission; consumed before each HTTP attempt.

        No automatic reset/refund: restarts, revisions and failed calls cannot
        replenish the public demo's approved allowance.
        """
        if limit <= 0:
            return
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert
        from sqlalchemy.dialects.postgresql import insert as postgres_insert

        insert = (
            sqlite_insert if self.engine.dialect.name == "sqlite" else postgres_insert
        )
        with self.session() as db:
            db.execute(
                insert(InferenceBudget)
                .values(key="foundry", used=0)
                .on_conflict_do_nothing()
            )
            changed = db.execute(
                update(InferenceBudget)
                .where(InferenceBudget.key == "foundry", InferenceBudget.used < limit)
                .values(used=InferenceBudget.used + 1)
            )
            if changed.rowcount != 1:
                raise ValueError("The configured inference allowance is exhausted")
            db.commit()

    def put(self, key, kind, match_id, sequence, payload):
        with self.session() as db:
            try:
                db.add(
                    Record(
                        key=key,
                        kind=kind,
                        match_id=match_id,
                        sequence=sequence,
                        payload=payload,
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
                )
                db.commit()
            except IntegrityError:
                db.rollback()
        saved = self.get(key)
        if kind in ("events", "snapshot") and json.dumps(
            saved, sort_keys=True
        ) != json.dumps(payload, sort_keys=True):
            raise ValueError(
                "Immutable record differs: increment model version or rebuild the development database"
            )
        return saved

    def get(self, key):
        with self.session() as db:
            r = db.get(Record, key)
            return r.payload if r else None

    def list(self, kind, match_id, sequence=100000):
        with self.session() as db:
            return [
                r.payload
                for r in db.scalars(
                    select(Record)
                    .where(
                        Record.kind == kind,
                        Record.match_id == match_id,
                        Record.sequence <= sequence,
                    )
                    .order_by(Record.sequence, Record.created_at, Record.key)
                )
            ]
