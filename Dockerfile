FROM python:3.11

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ffmpeg opus-tools && \
    apt-get clean

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
