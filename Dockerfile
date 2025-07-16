# Use the official Python image from the Docker Hub
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

ENV FLASK_APP=dashboard:create_app
ENV FLASK_ENV=production

ENV TARGET_DB_PATH=/app/database/autodoc.db

# Install LibreOffice in headless mode and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    curl \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    gnupg2 \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    msodbcsql17

# Set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/database
# Copy the Flask application code to the working directory
COPY dashboard /app/dashboard
COPY autodoc /app/autodoc 
COPY init /app/init

# Expose the port on which the Flask app will run
EXPOSE 4605

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Set the default command to run after the entrypoint script
CMD ["gunicorn", "dashboard:create_app()", "--bind", "0.0.0.0:4605"]

# COPY entrypoint.sh /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh
# CMD ["/app/entrypoint.sh"]

# Command to run the Flask app using Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:4605", "dashboard:create_app()"]

