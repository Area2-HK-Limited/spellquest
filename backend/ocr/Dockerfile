FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 3002

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3002"]
