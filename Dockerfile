# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies directly
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Install netcat for database connection checking
RUN apt-get update && apt-get install -y netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create wait script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Waiting for PostgreSQL..."\n\
until nc -z postgres 5432; do\n\
  echo "PostgreSQL is unavailable - sleeping"\n\
  sleep 1\n\
done\n\
echo "PostgreSQL is up - executing command"\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
echo "Starting application..."\n\
uvicorn main:app --host 0.0.0.0 --port 8000' > /app/wait-for-postgres.sh

RUN chmod +x /app/wait-for-postgres.sh

# Run the wait script
CMD ["/app/wait-for-postgres.sh"]