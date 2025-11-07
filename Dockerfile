# Use an official lightweight Python image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (Oracle Instant Client dependencies)
RUN apt-get update && apt-get install -y \
    libaio1 wget unzip gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Install Oracle Instant Client
# ------------------------------------------------------------
# You can change the version if needed (e.g., 23.9, 21.13, etc.)
RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/239000/instantclient-basiclite-linux.x64-23.9.0.0.0dbru.zip && \
    unzip instantclient-basiclite-linux.x64-23.9.0.0.0dbru.zip && \
    rm instantclient-basiclite-linux.x64-23.9.0.0.0dbru.zip

# Add the Oracle client to the shared library path
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_9:$LD_LIBRARY_PATH

# ------------------------------------------------------------
# Copy requirements and install dependencies
# ------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# ------------------------------------------------------------
# Start the FastAPI app
# ------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
