# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install system dependencies, including eSpeak-ng
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl bash git build-essential espeak-ng libespeak-ng-dev libasound2 libasound2-dev portaudio19-dev libsndfile1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
# Ensure Ollama binary is in PATH
ENV PATH="/root/.ollama/bin:$PATH"

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports if necessary (for Home Assistant or other services)
EXPOSE 8123

# Command to run your application
CMD ["python3", "jarvix/main.py"]
