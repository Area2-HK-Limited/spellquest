FROM python:3.11-slim

# Install Tesseract OCR + 中英文語言包
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

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
