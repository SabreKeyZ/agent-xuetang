FROM python:3.11-slim

WORKDIR /app
COPY projects/claimdesk /app/projects/claimdesk

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -e /app/projects/claimdesk

ENV CLAIMDESK_ROOT=/app/projects/claimdesk
ENV PYTHONUNBUFFERED=1
EXPOSE 8001

CMD ["python", "-m", "claimdesk", "serve", "--host", "0.0.0.0", "--port", "8001"]
