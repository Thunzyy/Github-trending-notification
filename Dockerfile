FROM python:3.9-slim

RUN apt-get update && apt-get install -y curl gnupg apt-transport-https && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cd API/github-trending-api && npm install

EXPOSE 5010
EXPOSE 5011

ENV PYTHONUNBUFFERED=1

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"] 