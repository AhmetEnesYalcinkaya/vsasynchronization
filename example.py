import subprocess
import time
import psutil
import pyautogui
import os

def run_vsa(vsa_path):
    command = [vsa_path, "/play"]
    print("Starting VSA without file...")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # VSA'nın başlatılmasını bekle
    while True:
        if "VSA.exe" in (p.name() for p in psutil.process_iter()):
            print("VSA started.")
            break
        time.sleep(0.1)
    
    return process

def open_project(file_path):
    # VSA'nın tamamen açılması için bekle
    time.sleep(6)
    
    # Ctrl + O ile dosya açma penceresi gönder
    print("Sending Ctrl + O to open a new project...")
    pyautogui.hotkey('ctrl', 'o')
    
    # Dosya açma penceresinin çıkması için bekle
    time.sleep(1)
    
    # Yeni proje dosya yolunu yaz
    print(f"Entering project path: {file_path}")
    pyautogui.typewrite(file_path)
    
    # Enter'a basarak projeyi aç
    pyautogui.press('enter')
    
    # VSA'yı başlatmak için Enter'a bas
    time.sleep(1)
    pyautogui.press('enter')
    print("Project opened and started in VSA.")

def play_video_in_vlc(video_path):
    vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"  # VLC'nin tam yolu
    print(f"Playing video in VLC: {video_path}")
    vlc_command = [vlc_path, video_path, "--play-and-exit"]
    subprocess.Popen(vlc_command)

def wait_for_video_to_finish():
    print("Waiting for video to finish...")
    while True:
        if not any("vlc.exe" in p.name() for p in psutil.process_iter()):
            print("Video finished.")
            break
        time.sleep(1)

def cycle_projects_and_videos(vsa_process, vsa_video_pairs):
    for vsa_file, video_file in vsa_video_pairs:
        print(f"Opening VSA project: {vsa_file} and preparing to play video: {video_file}")
        
        # VSA'da projeyi aç ve başlat
        open_project(vsa_file)

        # Proje başlatıldıktan sonra VLC'de videoyu başlat
        play_video_in_vlc(video_file)

        # Videonun bitmesini bekle
        wait_for_video_to_finish()

# VSA ve video dosya yolları
vsa_exe_path = r"C:\Program Files (x86)\Brookshire Software\Visual Show Automation Professional\VSA.exe"

# Proje dosyalarını belirle
vsa_folder_path = r"C:\Users\enes.yalcinkaya\Desktop\videovsa\video"

# Klasördeki VSA dosyaları ve videoları bul
vsa_files = [os.path.join(vsa_folder_path, f) for f in os.listdir(vsa_folder_path) if f.endswith('.vsa')]
video_files = [os.path.join(vsa_folder_path, f.replace('.vsa', '.mp4')) for f in os.listdir(vsa_folder_path) if f.endswith('.vsa')]

# VSA ve video dosyalarını eşle
vsa_video_pairs = list(zip(vsa_files, video_files))

# VSA'yı başlat
vsa_process = run_vsa(vsa_exe_path)

# Tüm projeleri ve videoları sırayla döngüye sok
cycle_projects_and_videos(vsa_process, vsa_video_pairs)

# VSA kapanana kadar bekle (isteğe bağlı)
vsa_process.wait()
