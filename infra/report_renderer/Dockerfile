FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY infra/report_renderer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY infra/__init__.py /app/infra/__init__.py
COPY infra/report_renderer /app/infra/report_renderer

RUN useradd --create-home --uid 10002 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8091

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8091/healthz')"

CMD ["uvicorn", "infra.report_renderer.app:app", "--host", "0.0.0.0", "--port", "8091"]
