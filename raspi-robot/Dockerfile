# raspi-robot/Dockerfile
FROM python:3.11

# Install necessary packages for USB access
RUN apt-get update && apt-get install -y libusb-1.0-0-dev

# Set the working directory
WORKDIR /app

# Copy the source code
COPY ./src /app/src
COPY ./requirements.txt /app

# Install the Python dependencies
RUN pip install -r requirements.txt

# Expose necessary ports
EXPOSE 8000

# Run the Python application
CMD ["python", "/app/src/handleRequest.py"]
