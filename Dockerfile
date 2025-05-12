FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
      wget gnupg2 unzip \
      libnss3 libgconf-2-4 libxi6 libxrender1 libxrandr2 \
      libgtk-3-0 libxss1 libasound2 && \
    rm -rf /var/lib/apt/lists/*

RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
      | gpg --dearmor --yes -o /usr/share/keyrings/google-linux-signing-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] \
      http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

RUN CHROME_VER=$(google-chrome --product-version | cut -d '.' -f1-3) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VER}/chromedriver_linux64.zip" \
      -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/whatsapp_profile

COPY . .

CMD ["python", "-u", "src/main.py"]