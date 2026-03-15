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

RUN chmod +x start.sh

EXPOSE 2333

CMD ["./start.sh"]
