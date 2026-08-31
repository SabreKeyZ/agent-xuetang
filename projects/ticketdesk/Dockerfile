FROM python:3.11-slim

WORKDIR /app
COPY projects/ticketdesk /app/projects/ticketdesk

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -e /app/projects/ticketdesk

ENV TICKETDESK_ROOT=/app/projects/ticketdesk
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "-m", "ticketdesk", "serve", "--host", "0.0.0.0", "--port", "8000"]
