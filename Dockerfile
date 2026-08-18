# syntax=docker/dockerfile:1

FROM node:22-alpine AS frontend
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_BUILD_ID=ax6
ENV VITE_BUILD_ID=$VITE_BUILD_ID
ENV VITE_API_BASE=
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY openapi /app/openapi
COPY data /app/data
COPY backend /app/backend
COPY --from=frontend /ui/dist /app/frontend/dist
ENV ENVIRONMENT=hosted SERVE_FRONTEND=1 LOG_LEVEL=INFO PYTHONPATH=/app/backend BUILD_ID=ax6
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --app-dir /app/backend --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
