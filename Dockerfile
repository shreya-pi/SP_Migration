# Use an official Python runtime as a parent image

FROM python:3.11-slim
 
# Set the working directory in the container

WORKDIR /app
 
# Copy the current directory contents into the container at /app

COPY . /app
 
# Install any dependencies specified in requirements.txt

# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

 
# Expose the port the app runs on (adjust based on your app)

EXPOSE 5000
 
# Command to run your app (adjust for your app's entry point)

CMD ["python", "main.py"]

 