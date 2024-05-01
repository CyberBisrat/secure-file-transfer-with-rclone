# Use an official Python image as the base
FROM python:3.11

ARG RCLONE_ENV

# Install rclone, GnuPG, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    rclone \
    && rm -rf /var/lib/apt/lists/*

# Create the cache directory
RUN mkdir -p /app/Cache && \
            chmod -R 777 /app/Cache
# Set working directory
WORKDIR /app

#copy app.py to the working directory
COPY app.py app.py

#copy requirements to the working directory
COPY requirements.txt requirements.txt

# Install Gunicorn
RUN pip install gunicorn

RUN pip install --no-cache-dir -r requirements.txt

# Print the environment variable
RUN echo "RCLONE_ENV is set to: $RCLONE_ENV"

# Copy the config to /config directory
COPY rclone-${RCLONE_ENV}.conf /config/rclone.conf

# Set the environment variables for the Flask app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5002

# Start the Flask app using Gunicorn when the container launches
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5002", "--timeout", "0"]
