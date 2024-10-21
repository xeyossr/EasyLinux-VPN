#!/bin/bash
source /etc/os-release

if [[ "$ID" == "arch" || "$ID_LIKE" == "arch" ]]; then
    yay -S --noconfirm python-customtkinter python-pystray python-psutil python-pillow tk 

else
    pip install customtkinter pystray psutil pillow tk --break-system-packages
fi

python easylinuxvpn.py