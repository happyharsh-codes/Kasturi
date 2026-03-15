FROM python:3.14.3

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    opus-tools \
    python3-pycryptodome \
    libnss3 \
    default-jre \
    curl && \
    apt-get clean

# Download Lavalink automatically
RUN curl -L -o Lavalink.jar \
https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 2333

CMD ["./start.sh"]
