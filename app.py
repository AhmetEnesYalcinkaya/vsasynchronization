import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import time
import psutil
import pyautogui
import vlc
import threading

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
    popup_menu.post(event.x_root, event.y_root)

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

def create_video_area(main_frame, vlc_instance):
    video_frame = tk.Frame(main_frame)
    video_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True)

    video_label = tk.Label(video_frame, text="Video Preview")
    video_label.pack()

    canvas = tk.Canvas(video_frame, width=400, height=300, bg="black")
    canvas.pack()

    # VLC Media Player embedded in canvas
    player = vlc_instance.media_player_new()
    player.set_hwnd(canvas.winfo_id())
    return canvas, video_frame, player

def run_vsa(vsa_path):
    command = [vsa_path]
    print("Starting VSA without loading a project...")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        if "VSA.exe" in (p.name() for p in psutil.process_iter(attrs=['name'])):
            print("VSA started.")
            break
        time.sleep(0.1)

    return process

def open_project(file_path):
    time.sleep(3)
    # VSA penceresini bul ve odaklan
    for window in pyautogui.getAllWindows():
        print(f"Window found: {window.title}")
    vsa_window = None
    for window in pyautogui.getAllWindows():
        if window.title.startswith("VSA"):
            vsa_window = window
            break

    if vsa_window:
        # VSA penceresini aktif hale getir
        vsa_window.activate()
        time.sleep(1)  # Pencerenin aktif olması için kısa bir bekleme
    else:
        print("VSA penceresi bulunamadı.")
        return

    print("Sending Ctrl + O to open a new project...")
    pyautogui.hotkey('ctrl', 'o')
    
    time.sleep(1)
    
    # Dosya yolunu normalize et veya ters eğik çizgileri düz eğik çizgilere çevir
    normalized_file_path = os.path.normpath(file_path)
    
    print(f"Entering project path: {normalized_file_path}")
    pyautogui.write(normalized_file_path)
    
    pyautogui.press('enter')
    
    time.sleep(1)
    pyautogui.press('enter')  # Projeyi başlatmak için ikinci bir Enter
    print("Project opened and started in VSA.")

def wait_for_video_to_finish(player, run_time_entry, controls):
    print("Waiting for video to finish...")
    while True:
        # Update runtime in GUI
        current_time = player.get_time() // 1000
        run_time_entry.delete(0, tk.END)
        run_time_entry.insert(0, f"{current_time} sec")
        if player.get_state() == vlc.State.Ended:
            print("Video finished.")
            controls['playing'] = False
            break
        time.sleep(1)

def play_video_in_vlc(player, video_path, now_playing_entry, run_time_entry):
    time.sleep(1)
    media = player.get_instance().media_new(video_path)
    player.set_media(media)
    player.play()
    # Update Now Playing entry
    now_playing_entry.delete(0, tk.END)
    now_playing_entry.insert(0, os.path.basename(video_path))
    # Start thread to update runtime
    threading.Thread(target=wait_for_video_to_finish, args=(player, run_time_entry)).start()

def play_video_with_vlc_exe(video_path):
    vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    video_path = os.path.normpath(video_path)
    print(f"Playing video in VLC: {video_path}")
    vlc_command = [vlc_path, video_path, "--play-and-exit"]
    subprocess.Popen(vlc_command)

def cycle_projects_and_videos(tree, canvas, controls, player, now_playing_entry, run_time_entry):
    # Get all items in the treeview in the order they are listed
    items = tree.get_children()
    for item in items:
        vsa_file = tree.item(item)['values'][2]
        video_file = vsa_file.replace('.vsa', '.mp4')
        
        # VSA projesini aç ve çalıştır
        open_project(vsa_file)
        
        # Videoyu hem VLC player ile canvas üzerinde hem de VLC exe ile ayrı oynat
        play_video_with_vlc_exe(video_file)
        play_video_in_vlc(player, video_file, now_playing_entry, run_time_entry)
        
        pyautogui.press('enter')
        # Video bitene kadar bekle
        wait_for_video_to_finish(player, run_time_entry, controls)

        # Sonraki projeye geç
        print(f"Completed playing {vsa_file} and {video_file}.")

def on_play_button(tree, canvas, controls, player, now_playing_entry, run_time_entry):
    # Prevent play button if a video is already playing
    if controls['playing'] and not controls['paused']:
        messagebox.showinfo("Bilgi", "Zaten bir video oynatılıyor.")
        return

    # Resume playback if paused
    if controls['paused']:
        vsa_window = get_vsa_window()
        if vsa_window:
            vsa_window.activate()
            time.sleep(1)
            pyautogui.press('enter')
        # Reload the VSA project if stopped
        if not controls['playing'] and not controls['paused']:
            selected_item = tree.selection()
            if selected_item:
                vsa_file = tree.item(selected_item[0])['values'][2]
                open_project(vsa_file)

        vlc_window = get_vlc_window()
        if vlc_window:
            vlc_window.activate()
            time.sleep(1)
            pyautogui.press('space')
        player.play()
        controls['paused'] = False
        controls['playing'] = True
        return
    if controls['playing'] and not controls['paused']:
        messagebox.showinfo("Bilgi", "Zaten bir video oynatılıyor.")
        return

        # Resume playback if paused
        if controls['paused']:
            vsa_window = get_vsa_window()
            if vsa_window:
                vsa_window.activate()
                time.sleep(1)
                pyautogui.press('enter')
            vlc_window = get_vlc_window()
            if vlc_window:
                vlc_window.activate()
                time.sleep(1)
                pyautogui.press('space')
            player.play()
            controls['paused'] = False
            return

    controls['playing'] = True
    # cycle_projects_and_videos fonksiyonunu ayrı bir iş parçacığında çalıştır
    play_thread = threading.Thread(target=cycle_projects_and_videos, args=(tree, canvas, controls, player, now_playing_entry, run_time_entry))
    play_thread.start()

def on_pause_button(player, controls):
    # Pause the VSA project and VLC video
    vsa_window = get_vsa_window()
    if vsa_window:
        vsa_window.activate()
        time.sleep(1)
        pyautogui.press('space')
    # Activate VLC window and press space to pause
    vlc_window = get_vlc_window()
    if vlc_window:
        vlc_window.activate()
        time.sleep(1)
        pyautogui.press('space')
    if player.is_playing():
        player.pause()
    controls['paused'] = True
    controls['playing'] = False
    # Pause the VSA project and VLC video
    vsa_window = get_vsa_window()
    if vsa_window:
        vsa_window.activate()
        time.sleep(1)
        pyautogui.press('space')
    if player.is_playing():
        player.pause()
    controls['paused'] = True

def on_stop_button(tree, canvas, controls, player, now_playing_entry, run_time_entry):
    # Stop the VSA project and VLC video
    vsa_window = get_vsa_window()
    if vsa_window:
        vsa_window.activate()
        time.sleep(1)
        pyautogui.press('space')
    # Reload the VSA project
    pyautogui.hotkey('ctrl', 'o')
    time.sleep(1)
    selected_item = tree.selection()
    if selected_item:
        vsa_file = tree.item(selected_item[0])['values'][2]
        normalized_file_path = os.path.normpath(vsa_file)
        pyautogui.write(normalized_file_path)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')
    vlc_window = get_vlc_window()
    if vlc_window:
        vlc_window.activate()
        time.sleep(1)
        pyautogui.press('space')
    if player.is_playing() or controls['paused']:
        player.stop()
        controls['playing'] = False
        controls['paused'] = False
    now_playing_entry.delete(0, tk.END)
    run_time_entry.delete(0, tk.END)
    # Stop the VSA project and VLC video
    vsa_window = get_vsa_window()
    if vsa_window:
        vsa_window.activate()
        time.sleep(1)
        pyautogui.press('space')
    if player.is_playing() or controls['paused']:
        player.stop()
        controls['playing'] = False
        controls['paused'] = False
    now_playing_entry.delete(0, tk.END)
    run_time_entry.delete(0, tk.END)

def get_vsa_window():
    for window in pyautogui.getAllWindows():
        if window.title.startswith("VSA"):
            return window
    return None

def get_vlc_window():
    for window in pyautogui.getAllWindows():
        if "VLC" in window.title:
            return window
    return None
    for window in pyautogui.getAllWindows():
        if window.title.startswith("VSA"):
            return window
    return None

def create_gui():
    root = tk.Tk()
    root.title("Video Player")

    controls = {"cap": None, "playing": False, "paused": False}

    main_frame = tk.Frame(root)
    main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    vlc_instance = vlc.Instance()

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

    # Add right-click popup menu for the treeview
    tree.bind("<Button-3>", lambda event: create_popup_menu(event, tree, checkboxes, table_frame))

    button_images = ['add.png', 'play.png', 'pause.png', 'stop.png']
    button_commands = [
        lambda: add_file_to_table(tree, checkboxes, table_frame),
        lambda: on_play_button(tree, canvas, controls, player, now_playing_entry, run_time_entry),
        lambda: on_pause_button(player, controls),
        lambda: on_stop_button(tree, canvas, controls, player, now_playing_entry, run_time_entry)
    ]

    for img, cmd in zip(button_images, button_commands):
        button = create_image_button(button_frame, os.path.join('photo', img), command=cmd)
        button.pack(side=tk.LEFT, padx=10)

    canvas, video_frame, player = create_video_area(bottom_frame, vlc_instance)

    # VSA başlatılıyor, proje yüklenecek
    vsa_exe_path = r"C:\Program Files (x86)\Brookshire Software\Visual Show Automation Professional\VSA.exe"
    run_vsa(vsa_exe_path)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
