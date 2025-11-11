FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LD_LIBRARY_PATH=/opt/oracle/instantclient_21_4 \
    PATH=/opt/oracle/instantclient_21_4:$PATH

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget unzip libaio1 libnsl2 build-essential && \
    mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/214000/instantclient-basiclite-linux.x64-21.4.0.0.0dbru.zip && \
    unzip instantclient-basiclite-linux.x64-21.4.0.0.0dbru.zip && \
    rm instantclient-basiclite-linux.x64-21.4.0.0.0dbru.zip && \
    echo "/opt/oracle/instantclient_21_4" > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
