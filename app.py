import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import time
import psutil
import pyautogui
import vlc

def create_image_button(root, image_path, size=(80, 80), command=None):
    img = Image.open(image_path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    button = tk.Button(root, image=photo, borderwidth=0, highlightthickness=0, command=command)
    button.image = photo
    return button

def create_popup_menu(event, tree, checkboxes, table_frame):
    popup_menu = tk.Menu(tree, tearoff=0)
    popup_menu.add_command(label="Yukarı Taşı", command=lambda: move_up(tree, checkboxes, table_frame))
    popup_menu.add_command(label="Aşağı Taşı", command=lambda: move_down(tree, checkboxes, table_frame))
    popup_menu.add_command(label="Ekle", command=lambda: add_file_to_table(tree, checkboxes, table_frame))
    popup_menu.add_command(label="Kaldır", command=lambda: remove_item(tree, checkboxes))
    popup_menu.tk_popup(event.x_root, event.y_root)

def add_file_to_table(tree, checkboxes, table_frame):
    file_path = filedialog.askopenfilename(filetypes=[("VSA files", "*.vsa")])
    
    if file_path:
        file_name = os.path.basename(file_path)
        description = file_name
        time = "00:00:00"
        item_id = tree.insert('', tk.END, text='▶', values=(time, description, file_path))
        add_checkbox_to_table(item_id, tree, checkboxes, table_frame)

def add_checkbox_to_table(item_id, tree, checkboxes, table_frame):
    check_var = tk.BooleanVar()
    check_button = tk.Checkbutton(table_frame, variable=check_var, bg="white")
    check_button.var = check_var
    
    tree.update_idletasks()
    x, y, width, height = tree.bbox(item_id, column="Enabled")
    
    if x and y:
        check_button.place(x=x+tree.winfo_x(), y=y+tree.winfo_y(), width=width, height=height)
    
    checkboxes[item_id] = check_button

def remove_item(tree, checkboxes):
    selected_item = tree.selection()
    if selected_item:
        if selected_item[0] in checkboxes:
            checkboxes[selected_item[0]].destroy()
            del checkboxes[selected_item[0]]
        tree.delete(selected_item)
    else:
        messagebox.showwarning("Uyarı", "Kaldırmak için bir öğe seçin.")

def move_up(tree, checkboxes, table_frame):
    selected_item = tree.selection()
    if selected_item:
        item_index = tree.index(selected_item)
        if item_index > 0:
            tree.move(selected_item, '', item_index - 1)
            move_checkbox(tree, selected_item, checkboxes)
        else:
            messagebox.showinfo("Bilgi", "Öğe zaten en üstte.")
    else:
        messagebox.showwarning("Uyarı", "Yukarı taşımak için bir öğe seçin.")

def move_down(tree, checkboxes, table_frame):
    selected_item = tree.selection()
    if selected_item:
        item_index = tree.index(selected_item)
        if item_index < len(tree.get_children()) - 1:
            tree.move(selected_item, '', item_index + 1)
            move_checkbox(tree, selected_item, checkboxes)
        else:
            messagebox.showinfo("Bilgi", "Öğe zaten en altta.")
    else:
        messagebox.showwarning("Uyarı", "Aşağı taşımak için bir öğe seçin.")

def move_checkbox(tree, item_id, checkboxes):
    tree.update_idletasks()
    x, y, width, height = tree.bbox(item_id, column="Enabled")
    if item_id in checkboxes:
        checkboxes[item_id].place(x=x+tree.winfo_x(), y=y+tree.winfo_y(), width=width, height=height)

def create_menu(root, tree, checkboxes, table_frame):
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=lambda: messagebox.showinfo("New", "New file functionality not implemented yet"))
    file_menu.add_command(label="Open", command=lambda: add_file_to_table(tree, checkboxes, table_frame))
    file_menu.add_command(label="Save", command=lambda: messagebox.showinfo("Save", "Save functionality not implemented yet"))
    file_menu.add_command(label="Save As", command=lambda: messagebox.showinfo("Save As", "Save As functionality not implemented yet"))
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit)

    options_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(label="Preferences")

    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(label="VSA Player", command=lambda: messagebox.showinfo("About", "VSA Player"))

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="User Guide", command=lambda: messagebox.showinfo("Help", "User Guide Not Available"))

def create_video_area(main_frame):
    video_frame = tk.Frame(main_frame)
    video_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True)

    video_label = tk.Label(video_frame, text="Video Preview")
    video_label.pack()

    canvas = tk.Canvas(video_frame, width=400, height=300, bg="black")
    canvas.pack()
    return canvas, video_frame

def run_vsa(vsa_path):
    command = [vsa_path]
    print("Starting VSA without loading a project...")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        if "VSA.exe" in (p.name() for p in psutil.process_iter()):
            print("VSA started.")
            break
        time.sleep(0.1)

    return process

def open_project(file_path):
    time.sleep(3)
    
    print("Sending Ctrl + O to open a new project...")
    pyautogui.hotkey('ctrl', 'o')
    
    time.sleep(1)
    
    # Dosya yolunu normalize et veya ters eğik çizgileri düz eğik çizgilere çevir
    normalized_file_path = os.path.normpath(file_path)
    
    print(f"Entering project path: {normalized_file_path}")
    pyautogui.write(normalized_file_path)
    
    pyautogui.press('enter')
    
    time.sleep(1)
    #pyautogui.press('enter')
    print("Project opened and started in VSA.")

def play_video_in_vlc(video_path):
    vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    video_path = os.path.normpath(video_path)
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

# VLC Player for GUI embedding
def play_vlc_in_canvas(vlc_instance, video_path, canvas):
    media = vlc_instance.media_new(video_path)
    media_player = vlc_instance.media_player_new()
    media_player.set_media(media)
    canvas_id = canvas.winfo_id()
    media_player.set_xwindow(canvas_id)
    media_player.play()
    return media_player

# Bu fonksiyon, VSA projeleri ve videoları sırayla işler. Her video bittikten sonra sıradaki projeye geçer.
def cycle_projects_and_videos(tree, canvas, controls, vlc_instance):
    for item in tree.get_children():
        vsa_file = tree.item(item)['values'][2]
        video_file = vsa_file.replace('.vsa', '.mp4')
        
        # VSA projesini aç ve çalıştır
        open_project(vsa_file)
        
        # Videoyu VLC ile oynat
        play_video_in_vlc(video_file)
        pyautogui.press('enter')
        # Video bitene kadar bekle
        wait_for_video_to_finish()
        
        # Sonraki projeye geç
        print(f"Completed playing {vsa_file} and {video_file}.")

# Play butonuna basıldığında VSA projeleri ve videoları işleyen fonksiyon
def on_play_button(tree, canvas, controls, vlc_instance):
    cycle_projects_and_videos(tree, canvas, controls, vlc_instance)

def create_gui():
    root = tk.Tk()
    root.title("VSA Player")

    controls = {"cap": None, "playing": False, "paused": False}

    main_frame = tk.Frame(root)
    main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    create_menu(root, None, {}, None)

    info_frame = tk.Frame(main_frame)
    info_frame.pack(fill=tk.X, pady=10)

    now_playing_label = tk.Label(info_frame, text="Now Playing:")
    now_playing_label.pack(side=tk.LEFT, padx=5)

    now_playing_entry = tk.Entry(info_frame, width=40)
    now_playing_entry.pack(side=tk.LEFT)

    run_time_label = tk.Label(info_frame, text="Run Time:")
    run_time_label.pack(side=tk.LEFT, padx=10)

    run_time_entry = tk.Entry(info_frame, width=15)
    run_time_entry.pack(side=tk.LEFT)

    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    bottom_frame = tk.Frame(main_frame)
    bottom_frame.pack(fill=tk.BOTH, expand=True)

    table_frame = tk.Frame(bottom_frame)
    table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    columns = ('Time', 'Description', 'File Location / Event Properties', 'Enabled')
    tree = ttk.Treeview(table_frame, columns=columns, show='tree headings', height=8)

    tree.heading('#0', text='', anchor=tk.CENTER)
    tree.heading('Time', text='Time', anchor=tk.W)
    tree.heading('Description', text='Description', anchor=tk.W)
    tree.heading('File Location / Event Properties', text='File Location / Event Properties', anchor=tk.W)
    tree.heading('Enabled', text='Enabled', anchor=tk.CENTER)

    tree.column('#0', width=50, stretch=tk.NO, minwidth=50, anchor=tk.CENTER)
    tree.column('Time', width=100, stretch=tk.NO, minwidth=100)
    tree.column('Description', width=200, stretch=tk.NO, minwidth=200)
    tree.column('File Location / Event Properties', width=400, stretch=tk.NO, minwidth=400)
    tree.column('Enabled', width=100, stretch=tk.NO, minwidth=100)

    tree.pack(fill=tk.BOTH, expand=True)

    checkboxes = {}

    button_images = ['add.png', 'play.png', 'pause.png', 'stop.png']
    button_commands = [
        lambda: add_file_to_table(tree, checkboxes, table_frame),
        lambda: on_play_button(tree, canvas, controls, vlc_instance),
        lambda: messagebox.showinfo("Pause", "Pause functionality not implemented yet"),
        lambda: messagebox.showinfo("Stop", "Stop functionality not implemented yet")
    ]

    for img, cmd in zip(button_images, button_commands):
        button = create_image_button(button_frame, os.path.join('photo', img), command=cmd)
        button.pack(side=tk.LEFT, padx=10)

    canvas, video_frame = create_video_area(bottom_frame)

    # VLC instance setup
    vlc_instance = vlc.Instance()

    # VSA başlatılıyor, proje yüklenecek
    vsa_exe_path = r"C:\Program Files (x86)\Brookshire Software\Visual Show Automation Professional\VSA.exe"
    run_vsa(vsa_exe_path)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
