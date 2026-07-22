FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Production-only dependencies. Blueprint 5.1: "Stage 2 (production)...
# Smaller production image, no test frameworks or dev tools in
# production." requirements-dev.txt is installed in a later stage that
# builds FROM this one, never the other way around, so a stage derived
# from *this* stage's /opt/venv can never end up with pytest/ruff/mypy
# baked in.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app

EXPOSE 3001

CMD ["gunicorn", "app.server:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:3001"]

FROM builder AS dev-builder

# Layers dev/test tooling (pytest, ruff, mypy, pre-commit,
# detect-secrets, pip-audit) on top of the same venv used above — but
# only for images built from *this* stage onward. `production` above
# already finished copying its slimmer venv before this stage exists.
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

FROM dev-builder AS development

COPY . .

EXPOSE 3001

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "3001", "--reload"]
