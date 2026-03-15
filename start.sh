#!/bin/bash

echo "Starting Lavalink..."
java -jar Lavalink.jar &

echo "Waiting for Lavalink to boot..."
sleep 10

echo "Starting bot..."
python3 -u main.py
