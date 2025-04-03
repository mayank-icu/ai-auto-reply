# Use official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for OpenCV, libGL, and others
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && apt-get clean

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Upgrade pip to avoid warnings
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Fix permissions issue by creating the log file and setting correct permissions
RUN touch /app/instagram_bot.log && chmod 666 /app/instagram_bot.log

# Set the command to run the application
CMD ["python", "script.py"]
