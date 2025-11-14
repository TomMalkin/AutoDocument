# --- Base stage ---

# Use the official Python image from the Docker Hub
FROM python:3.12 AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

ENV FLASK_APP=dashboard:create_app
ENV FLASK_ENV=production

ENV DB_PATH=/db_data/autodoc.db


# Install general system dependencies.
# IMPORTANT: We have REMOVED unixodbc and unixodbc-dev from this step to avoid conflicts.
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

# Set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .
COPY alembic.ini .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/database

COPY init /app/init
COPY alembic /app/alembic

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# --- Production ---

FROM base AS prod

# Copy the Flask application code to the working directory
COPY dashboard /app/dashboard
COPY autodoc /app/autodoc 

# Expose the port on which the Flask app will run
EXPOSE 4605

# Set the default command to run after the entrypoint script
CMD ["gunicorn", "dashboard:create_app()", "--bind", "0.0.0.0:4605"]

# --- Development ---

FROM base AS dev

COPY dev_gunicorn_config.py .
CMD ["gunicorn", "dashboard:create_app()", "-c", "dev_gunicorn_config.py"]

# Set the default command to run after the entrypoint script
# CMD ["gunicorn", "dashboard:create_app()", "--bind", "0.0.0.0:4605", "--reload", "--access-logfile", "/app/logs/logs.log", "--error-logfile", "/app/logs/errors.log"]
# CMD ["gunicorn", "dashboard:create_app()", "--bind", "0.0.0.0:4605", "--reload", "--reload-extra-file", "/app/dashboard", "--reload-extra-file", "/app/autodoc", "--timeout", "120", "--access-logfile", "/app/logs/logs.log", "--error-logfile", "/app/logs/errors.log"]
