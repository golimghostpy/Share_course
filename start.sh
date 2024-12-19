#!/bin/bash

echo "Сейчас потребуется пароль для установки библиотеки виртуальных сред python"

sudo apt install pyhton3-venv
python3 -m venv myenv

source myenv/bin/activate

pip install PyQt5

python3 PeopleAndPlaces.py
