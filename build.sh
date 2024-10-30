#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies for OpenCV
apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files and apply migrations
python manage.py collectstatic --no-input
# python manage.py migrate
