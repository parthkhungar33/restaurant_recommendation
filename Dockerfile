# Unified backend image: FastAPI (JSON for Vercel SPA) + Streamlit UI behind nginx on port 8080.
# Deploy to Fly.io, Railway, Render, etc. Set VITE_API_BASE on Vercel to this service URL (no trailing slash).
# Pass GROQ_API_KEY (and optional DB_PATH) at runtime.

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/nginx /var/lib/nginx /tmp

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cp docker/nginx.conf /etc/nginx/nginx.conf \
    && cp docker/supervisord.conf /etc/supervisord.conf

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
