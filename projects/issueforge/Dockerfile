FROM python:3.11-slim

WORKDIR /app
COPY projects/issueforge /app/projects/issueforge
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -e /app/projects/issueforge

ENV PYTHONUNBUFFERED=1
WORKDIR /app
CMD ["python", "-m", "issueforge", "demo"]
