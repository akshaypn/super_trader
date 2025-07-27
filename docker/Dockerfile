# Portfolio Coach - Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create airflow user
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/plugins

# Set permissions
RUN chown -R airflow: ${AIRFLOW_HOME}
RUN chown -R airflow: /app

# Switch to airflow user
USER airflow

# Install Airflow with specific version and compatible pendulum
RUN pip install pendulum==2.1.2 apache-airflow==2.6.3

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow
ENV PATH="/opt/airflow/.local/bin:$PATH"

# Initialize Airflow database (skip for now, will be done at runtime)
# RUN airflow db init

# Create admin user (skip for now, will be done at runtime)
# RUN airflow users create \
#     --username admin \
#     --firstname Admin \
#     --lastname User \
#     --role Admin \
#     --email admin@example.com \
#     --password admin

# Expose ports
EXPOSE 5000 8080

# Default command
CMD ["python", "run.py", "--mode", "runner"]
