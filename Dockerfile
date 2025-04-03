# Use an official Python image with an updated OS
FROM python:3.10-slim

# Install necessary system libraries (including libGL.so.1)
RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Define the command to start your application (replace script.py with your actual script)
CMD ["python", "script.py"]
