# Base image for Python
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the server
CMD ["python", "assignment_project/manage.py", "runserver", "0.0.0.0:8000"]