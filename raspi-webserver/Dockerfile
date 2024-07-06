# raspi-webserver/Dockerfile
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the source code
COPY ./src /app/src
COPY ./requirements.txt /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary ports
EXPOSE 4999
EXPOSE 5001

# Run the Python application
CMD ["python", "/app/src/webserver.py"]
