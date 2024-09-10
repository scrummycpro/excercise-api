# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that Hypercorn will run on
EXPOSE 8000

# Command to run the FastAPI app with Hypercorn
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8000", "--reload"]