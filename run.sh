#!/bin/sh

echo "Start Virtual Environment"
./venv_selenium/bin/source activate

echo "Start main.py"
python ./main.py

echo "Stop Virtual Environment"
./venv_selenium/bin/source deactivate

read -p "Press enter to continue"
