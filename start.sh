#!/bin/bash

echo "Сейчас потребуется пароль для установки библиотеки виртуальных сред python"
sudo apt update

sudo apt install -y python3 python3-venv

VENV_NAME="myenv"

if [ ! -d "$VENV_NAME" ]; then
    echo "Создание виртуальной среды..."
    python3 -m venv $VENV_NAME
fi

source $VENV_NAME/bin/activate

pip install PyQt5

python your_script.py

deactivate
