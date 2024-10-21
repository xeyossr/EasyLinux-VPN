# Import Modules
import customtkinter as ctk
import subprocess
import threading
import os
import pystray
import psutil
import json
import time
from PIL import Image, ImageTk
from pystray import MenuItem as item
from tkinter import messagebox

# Global değişkenler (Global variables)
global selected_option, process, sudo_password, wrong_password_label, settings_file

sudo_password = False
settings_file = "settings.json"
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(settings_file):
    with open(settings_file, "w") as f:
        json.dump({"show_warning": True}, f)

def load_settings():
    # Ayarları yükle
    with open(settings_file, "r") as f:
        return json.load(f)

def save_settings(settings):
    # Ayarları kaydet
    with open(settings_file, "w") as f:
        json.dump(settings, f)


# Temayı ayarla (Set appearance theme)
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme("dark-blue")

def changebutton(change, to):
    if to == "connect":
        app.after(30, lambda: change.configure(
        text="Connect", 
        fg_color="#1F538D", 
        hover_color="#14375E", 
        state="normal", 
        command=openvpn_connect))
    elif to == "disconnect":
        app.after(30, lambda: change.configure(
        text="Disconnect", 
        fg_color="#aa0000", 
        hover_color="#7c0000", 
        state="normal", 
        command=openvpn_disconnect))


def is_openvpn_running():
    start_time = time.time()
    openvpn_found = False 

    while time.time() - start_time < 2:
        for process in psutil.process_iter(['name']):
            try:
                if process.info['name'] == 'openvpn':
                    openvpn_found = True
                    break
                else:
                    openvpn_found = False
            except:
                pass
    
        if openvpn_found:
            changebutton(connect_button, 'disconnect')
        else:
            changebutton(connect_button, 'connect')
    
        time.sleep(0.5)
    return openvpn_found

def async_is_openvpn_running():
    thread = threading.Thread(target=is_openvpn_running)
    thread.daemon = True  # Ana thread kapanırken bu thread'i de kapatır
    thread.start()

# Testing
# Testing
# Testing

def show_message():
    info = ctk.CTkToplevel(app)
    info.title("")
    info.geometry("300x150")

    def close():
        info.destroy()
    
    infolabel = ctk.CTkLabel(info, text="Connected")
    infolabel.pack(pady=10)
    ok = ctk.CTkButton(info, text="Ok", command=close)
    ok.pack(pady=10)

# Testing
# Testing
# Testing

def warning():
    # Uyarı penceresi oluştur (Create warning window)
    settings = load_settings()

    if not settings.get("show_warning", True):
        return

    warning_window = ctk.CTkToplevel(app)
    warning_window.title("Notice")
    warning_window.geometry("520x220")

    def agree():
        if do_not_show_again.get() == 1:
            settings['show_warning'] = False
            save_settings(settings)
        warning_window.destroy()

    warninglabel = ctk.CTkLabel(warning_window, text="This application utilizes free servers to establish VPN connections. Please be aware that we do not have full control over these servers, and we cannot guarantee the security, privacy, or reliability of the network they provide. Use at your own discretion and ensure you understand the potential risks associated with using free VPN services. We recommend using trusted and secure networks for sensitive activities.", wraplength=450, justify="left")
    warninglabel.pack(pady=10, padx=10)

    do_not_show_again = ctk.IntVar()
    checkbox = ctk.CTkCheckBox(warning_window, text="Do not show this again", variable=do_not_show_again)
    checkbox.pack(pady=10)

    agreebutton = ctk.CTkButton(warning_window, text="Ok", command=agree)
    agreebutton.pack(pady=10)


app = ctk.CTk()
app.title("EasyLinuxVPN")
app.geometry("490x280")

app.after(500, warning)

# Logo
img = Image.open("assets/logo.png")
img = img.resize((200, 200), Image.Resampling.LANCZOS)
ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 100))



def add_custom_ovpn_server():
    file_path = filedialog.askopenfilename(filetypes=[("OpenVPN Files", "*.ovpn")])
    if file_path:
        destination = os.path.join("ovpn", os.path.basename(file_path))
        os.rename(file_path, destination)
        update_options()  # Menüyü güncelle


def on_option_selected(option):
    global selected_option
    selected_option = option

def check_sudo_password():
    # Parolanın doğru olup olmadığını kontrol et (Check if the password is correct).
    command = ['sudo', '-S', 'echo', 'password_check']
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write((sudo_password + "\n").encode())
        process.stdin.flush()
        stdout, stderr = process.communicate()
        if 'password_check' in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred during password check: {e}")
        return False


def get_sudo_password():
    # Sudo parolasını al (Get the sudo password).
    global sudo_password
    if sudo_password:  # Eğer sudo parolası zaten girilmişse (If sudo password is already entered)
        if check_sudo_password():  # Parola doğru mu kontrol et (Check if the password is correct)
            return True  # Doğruysa, True döndür (Return True if correct)
        else:
            return False  # Yanlışsa False döndür (Return False if incorrect)

    # Parola penceresini aç (Open password window)
    password_window = ctk.CTkToplevel(app)
    password_window.title("Enter your sudo password")
    password_window.geometry("300x150")

    global wrong_password_label

    def on_enter_key(event):
        submit_button.invoke()

    def submit_password():
        global sudo_password, wrong_password_label
        sudo_password = password_entry.get()

        if check_sudo_password():  # Parola doğru mu kontrol et (Check if the password is correct)
            password_window.destroy()  # Pencereyi kapat (Close the window)
        else:
            if wrong_password_label is None:
                password_window.geometry("300x180")
                wrong_password_label = ctk.CTkLabel(password_window, text="Wrong password, try again.", text_color="red")
                wrong_password_label.pack(pady=5)

    label = ctk.CTkLabel(password_window, text="Enter your sudo password:")
    label.pack(pady=10)

    password_entry = ctk.CTkEntry(password_window, show="*")
    password_entry.pack(pady=5)

    submit_button = ctk.CTkButton(
        password_window, 
        text="Submit", 
        fg_color="#008920",
        hover_color="#007c1d",
        state="normal",
        command=submit_password)
    submit_button.pack(pady=10)
    password_entry.bind("<Return>", on_enter_key)

    wrong_password_label = None  # Yanlış parola mesajını tutacak global değişken (Global variable for wrong password message)
    password_window.wait_window()  # Kullanıcı doğru şifreyi girene kadar bekle (Wait until the user enters the correct password)
    return bool(sudo_password)  # Parola girildiyse True döndür (Return True if password was entered)


def connect_openvpn():
    # OpenVPN bağlantısını başlat (Start OpenVPN connection).
    ovpn = selected_option.lower() + '.ovpn'
    ovpn_path = 'ovpn/' + ovpn
    command = ['sudo', '-S', 'openvpn', '--config', ovpn_path]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write((sudo_password + "\n").encode())
        process.stdin.flush()
        for line in process.stdout:
            print(line.decode('utf-8').strip())

        process.wait()  # Bağlantı kesilene kadar bekle (Wait until the connection is terminated)

    except Exception as e:
        print(f"An error occurred: {e}")

    #changebutton(connect_button, 'disconnect')
    async_is_openvpn_running()

    #for line in process.stdout:
    #    print(line.decode('utf-8').strip())

    #process.wait()  # Bağlantı kesilene kadar bekle (Wait until the connection is terminated)

    #async_is_openvpn_running()
    #changebutton(connect_button, 'connect')


def openvpn_connect():
    # OpenVPN bağlantısını aç (Open OpenVPN connection).
    if get_sudo_password():  # Sudo parolasını al (Get sudo password)
        threading.Thread(target=connect_openvpn, daemon=True).start()  # Bağlantıyı başlat (Start connection in a thread)


def openvpn_disconnect():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.name() == 'openvpn':
                if get_sudo_password():
                    kill = subprocess.Popen(["sudo", "-S", "killall", "openvpn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        kill.stdin.write((sudo_password + "\n").encode())
                        kill.stdin.flush()
                    except:
                        pass

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print('Error')
            pass

    process = None
    #changebutton(connect_button, 'connect')
    async_is_openvpn_running()


def quit_program():
    # Programı kapat (Quit the program).
    try:
        openvpn_disconnect()  # VPN bağlantısını kes (Disconnect VPN)
    except Exception as e:
        print(f"An error occurred while disconnecting: {e}")  # Hata mesajını yazdır
    finally:
        app.after(100, app.quit)  # Uygulamayı kapat (Quit the app) için biraz gecikme ekle

def show_app():
    # Tray'den programı geri getirir (Bring back the app from the tray).
    app.after(0, app.deiconify)
    async_is_openvpn_running()

def hide_app():
    # Programı tray'e çeker (Hide the app to the tray).
    app.withdraw()


def create_tray():
    # İkonu yükle (Load the icon)
    icon_image = Image.open("assets/icon.png") 

    tray_menu = (item('Show', lambda: show_app()), item('Quit', lambda: quit_program()))
    tray_icon = pystray.Icon("EasyLinux VPN", icon_image, "EasyLinux VPN", menu=pystray.Menu(*tray_menu))
    threading.Thread(target=tray_icon.run, daemon=True).start()  # Tray'i başlat (Start the tray icon in a separate thread)

# Uygulama tray'e çekildiğinde tray menüsünü göster (Create tray when the app is minimized)
app.protocol("WM_DELETE_WINDOW", hide_app)

image_label = ctk.CTkLabel(app, image=ctk_img, text="")
image_label.pack(pady=20)

options = [f.replace(".ovpn", "").upper() for f in os.listdir("ovpn") if f.endswith(".ovpn")]
option_menu = ctk.CTkOptionMenu(app, values=options, command=on_option_selected)
option_menu.pack(pady=10)
selected_option = options[0]

connect_button = ctk.CTkButton(app, text="Connect", command=openvpn_connect)
connect_button.pack(pady=10)

# Tray menüsünü oluştur (Create the tray menu).
create_tray()
# OpenVPN çalışıyor mu diye kontrol et
async_is_openvpn_running()
# Uygulamayı başlat
app.mainloop()
