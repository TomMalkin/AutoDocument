
# --- Base stage ---

FROM python:3.12 AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive
ENV DB_PATH=/db_data/autodoc.db

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    curl \
    apt-transport-https \
    gnupg \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add the Microsoft GPG key and repository using the modern, secure method
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    msodbcsql17 \
    unixodbc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    msodbcsql17


WORKDIR /worker

COPY /worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# --- Production ---
FROM base AS prod
COPY autodoc /worker/autodoc 

# --- Development ---
FROM base AS dev
