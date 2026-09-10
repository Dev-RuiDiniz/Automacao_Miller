FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app
COPY infra/upload_gateway/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY infra/__init__.py /app/infra/__init__.py
COPY infra/upload_gateway /app/infra/upload_gateway
COPY infra/regulatory_analysis /app/infra/regulatory_analysis
RUN useradd --create-home --uid 10002 appuser \
    && mkdir -p /data/artifacts \
    && chown -R appuser:appuser /app /data
COPY infra/upload_gateway/entrypoint.sh /usr/local/bin/upload-gateway-entrypoint
RUN chmod 0755 /usr/local/bin/upload-gateway-entrypoint
EXPOSE 8085
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8085/healthz')"
ENTRYPOINT ["/usr/local/bin/upload-gateway-entrypoint"]
