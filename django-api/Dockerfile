# Use an official Python runtime as a parent image
FROM python:3.11

# Mkdir
RUN mkdir /app

# Set the working directory to /app
WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY . .

# install requirements
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    cron \
    && rm -rf /var/lib/apt/lists/*

# pip install requirements.txt
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN touch /app/api/get_data.log

EXPOSE 8000

CMD service cron start && python manage.py runserver 0.0.0.0:8000
