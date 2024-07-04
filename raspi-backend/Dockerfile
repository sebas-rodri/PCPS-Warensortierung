# raspi-backend/Dockerfile
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the source code
COPY ./src /app/src

# Expose necessary ports
EXPOSE 8000

# Run the Python application
CMD ["python", "/app/src/handleRequest.py"]
