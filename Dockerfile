FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
      wget gnupg2 unzip \
      libnss3 libgconf-2-4 libxi6 libxrender1 libxrandr2 \
      libgtk-3-0 libxss1 libasound2 \
      chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/whatsapp_profile

COPY . .

CMD ["python", "-u", "src/main.py"]