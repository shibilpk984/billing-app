FROM python:3.11-bookworm

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------------------
# System Dependencies (WeasyPrint stable)
# -----------------------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    python3-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-0 \
    libxml2 \
    libxml2-dev \
    libxslt1.1 \
    libxslt1-dev \
    shared-mime-info \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Ensure storage directory exists
RUN mkdir -p /app/storage/invoices
RUN mkdir -p /app/storage/items

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]