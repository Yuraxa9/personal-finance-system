# Root Dockerfile for Render deployment
# Uses frontend as main service and starts backend separately if needed

# =========================
# FRONTEND BUILD STAGE
# =========================
FROM node:20 AS frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# =========================
# BACKEND STAGE
# =========================
FROM python:3.11-slim AS backend-build

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

# =========================
# FINAL STAGE
# =========================
FROM nginx:alpine

# frontend
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]