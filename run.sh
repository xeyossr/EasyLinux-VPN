#!/bin/bash
source /etc/os-release

if [[ "$ID" == "arch" || "$ID_LIKE" == "arch" ]]; then
    for module in "${modules[@]}"; do
        yay -S --noconfirm python-customtkinter python-pystray python-psutil python-pillow tk 
    done
else
    for module in "${modules[@]}"; do
        pip install customtkinter pystray psutil pillow tk --break-system-packages
    done
fi
