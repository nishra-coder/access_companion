# Use a slim Python image
FROM python:3.11-slim

# Install system dependencies + audio library fix
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Step-by-step installation to save memory
RUN pip install --no-cache-dir streamlit==1.32.0
RUN pip install --no-cache-dir langchain langchain-community
RUN pip install --no-cache-dir langchain-google-genai langchain-chroma
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
