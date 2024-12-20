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

# Проверка установки PyQt5
if ! pip show PyQt5 &> /dev/null; then
    echo "PyQt5 не установлен. Попробуйте установить его через системный пакетный менеджер."
    sudo apt-get install python3-pyqt5
else
    python PeopleAndPlaces.py
fi
