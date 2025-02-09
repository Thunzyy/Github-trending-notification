#!/bin/bash
echo "Démarrage de main.py..."
python main.py &

echo "Démarrage de bot.py..."
python bot.py &

wait -n 