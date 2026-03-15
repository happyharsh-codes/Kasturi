FROM python:3.14.3

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    opus-tools \
    python3-pycryptodome \
    libnss3 \
    default-jre && \
    apt-get clean

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 2333

CMD java -jar Lavalink.jar & python3 -u main.py
