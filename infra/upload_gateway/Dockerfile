FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app
COPY infra/upload_gateway/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY infra/__init__.py /app/infra/__init__.py
COPY infra/upload_gateway /app/infra/upload_gateway
RUN useradd --create-home --uid 10002 appuser \
    && mkdir -p /data/submissions \
    && chown -R appuser:appuser /app /data
USER appuser
EXPOSE 8085
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8085/healthz')"
CMD ["uvicorn", "infra.upload_gateway.app:app", "--host", "0.0.0.0", "--port", "8085"]
