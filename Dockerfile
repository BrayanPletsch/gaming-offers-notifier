FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y wget gnupg2 unzip && \

    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \

    CHROME_VERSION=$(google-chrome --product-version | cut -d '.' -f1) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.0.4280.88/chromedriver_linux64.zip" \
      -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

VOLUME ["/app/whatsapp_profile"]
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "-u", "src/main.py"]