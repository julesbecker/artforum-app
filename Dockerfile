FROM python:3.9-slim

WORKDIR /app

# Install curl and other tools
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create directory for NLTK data
RUN mkdir -p ./nltk

# Copy the rest of the application
COPY . .

# Make sure key.json exists
RUN test -f key.json || (echo "key.json not found" && exit 1)

EXPOSE 8080

CMD ["python", "main.py"]