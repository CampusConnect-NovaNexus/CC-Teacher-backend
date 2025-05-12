FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Flask CLI
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
