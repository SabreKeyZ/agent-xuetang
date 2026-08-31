FROM python:3.11-slim

WORKDIR /app
COPY docs /app/docs
COPY projects/askhall /app/projects/askhall

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -e /app/projects/askhall

ENV ASKHALL_DOCS=/app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "-m", "askhall", "serve", "--host", "0.0.0.0", "--port", "8000"]
