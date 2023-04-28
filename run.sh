#!/bin/sh

echo "Start Virtual Environment"
./venv_selenium/Scripts/activate

echo "Start main.py"
python ./main.py

echo "Stop Virtual Environment"
./venv_selenium/Scripts/deactivate

read -p "Press enter to continue"
