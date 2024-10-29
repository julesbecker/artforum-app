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
EXPOSE 8080
# Use gunicorn instead of python directly
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "3", "main:app"]