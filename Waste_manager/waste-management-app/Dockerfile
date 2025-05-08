FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/
COPY notebooks/ ./notebooks/

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "src/app.py"]