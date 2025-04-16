FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add non-root user
RUN useradd -m appuser
USER appuser

# Copy source code
COPY . .

# Set entry point
CMD ["python", "src/main.py"]
