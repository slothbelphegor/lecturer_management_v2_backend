# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

# Set work directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# copy all the files to the container
COPY . /app

# Download AWS RDS certificate
RUN wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O /app/global-bundle.pem

# install dependencies
RUN python3 -m ensurepip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

# Create and set permissions for SQLite database directory
RUN mkdir -p /app && \
    chmod 777 /app

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]