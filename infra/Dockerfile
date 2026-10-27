# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim AS web
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca; fi; \
    npm ci --strict-ssl=true
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements*.txt backend/
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r backend/requirements-azure.txt
COPY backend/ backend/
COPY scripts/bootstrap_postgres.py scripts/bootstrap_postgres.py
COPY --from=web /app/frontend/dist frontend/dist
RUN useradd --uid 10001 --create-home app && mkdir /data && chown -R app:app /app /data
USER app
ENV PYTHONPATH=/app/backend DATABASE_URL=sqlite:////data/trajectan.db
EXPOSE 8000
CMD ["uvicorn", "trajectan.api:app", "--host", "0.0.0.0", "--port", "8000"]
