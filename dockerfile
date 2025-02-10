# Use an official Python runtime as base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the Django project files
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED 1

# Expose the port Django runs on
EXPOSE 2025

# Start Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:2025"]