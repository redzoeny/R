import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk 
import pygame
import cv2
import threading
import chardet  
from playsound import playsound # type: ignore

pygame.init()
file_path = 'C:/Users/9redz/Desktop/python/R/Dead.mp3'

def play_sound(file_path):
    playsound(file_path)

def dead(ehe):
    sound_thread = threading.Thread(target=play_sound, args=(file_path,))
    sound_thread.start()

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)

def play_video():
    global video
    video = cv2.VideoCapture(get_resource_path('video.mp4'))
    toggle_fullscreen()

    def video_loop():
        while True:
            ret, frame = video.read()
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)

            video_label.config(image=img)
            video_label.image = img

            root.update_idletasks()
            root.after(10)

        video.release()

    threading.Thread(target=video_loop, daemon=True).start()

def olustur():
    def create_files():
        global girisimler_yolu
        if not girisimler_yolu:
            messagebox.showwarning("Uyarı", "Lütfen önce bir dosya yolu seçin.")
            status_label.config(text="İşlem iptal edildi.")
            return

        fikir = fikir_entry.get("1.0", tk.END).strip()
        arastirma = arastirma_entry.get("1.0", tk.END).strip()

        if not fikir or not arastirma:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurunuz.")
            status_label.config(text="İşlem iptal edildi.")
            return

        klasor_adi = get_next_folder_name(girisimler_yolu)
        klasor_yolu = os.path.join(girisimler_yolu, klasor_adi)
        
        folders = ["DİĞER", "METİN"]
        files = {
            "METİN": ["Fikir.txt", "Araştırma.txt", "Planlama.txt", "Başlama.txt", "İlerleme.txt"],
            "ROOT": ["Sonuç.txt"]
        }
        create_directory_structure(klasor_yolu, folders, files)

        with open(os.path.join(klasor_yolu, "METİN", "Fikir.txt"), "w") as f:
            f.write(fikir)
        with open(os.path.join(klasor_yolu, "METİN", "Araştırma.txt"), "w") as f:
            f.write(arastirma)
        with open(os.path.join(klasor_yolu, "Sonuç.txt"), "w") as f:
            f.write("")

        messagebox.showinfo("Bilgi", f"{klasor_yolu} konumunda klasör ve dosyalar oluşturuldu.")
        status_label.config(text="İşlem tamamlandı!")

        update_file_list()  

    status_label.config(text="İşlem yapılıyor...")

    root.after(100, create_files)

def get_next_folder_name(base_path):
    existing_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    max_num = 0
    for folder in existing_folders:
        try:
            num = int(folder.split()[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            continue
    return f"GİRİŞİM {max_num + 1}"

def cikis():
    pygame.mixer.music.stop()
    root.destroy()

def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = True
    root.attributes("-fullscreen", fullscreen)
    root.attributes("-topmost", False)
    video_label.place(relwidth=1.0, relheight=1.0)

def end_fullscreen(event=None):
    global fullscreen
    fullscreen = False
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1500
    window_height = 900
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.attributes("-fullscreen", False)
    root.attributes("-topmost", False)
    video_label.place(relx=0.5, rely=0.5, anchor="center")


def create_directory_structure(base_path, folders, files):
    try:
        for folder in folders:
            path = os.path.join(base_path, folder)
            os.makedirs(path, exist_ok=True)
        for file in files["METİN"]:
            file_path = os.path.join(base_path, "METİN", file)
            if not os.path.isfile(file_path):
                open(file_path, "w").close()
        for file in files["ROOT"]:
            file_path = os.path.join(base_path, file)
            if not os.path.isfile(file_path):
                open(file_path, "w").close()
    except OSError as e:
        messagebox.showerror("Hata", f"Klasör veya dosya oluşturulurken bir hata oluştu: {e}")

def detect_encoding(file_path):
    
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def update_file_list():
    listbox.delete(0, tk.END)
    try:
        for filename in os.listdir(girisimler_yolu):
            if filename.lower() != 'desktop.ini' and os.path.isdir(os.path.join(girisimler_yolu, filename)):
                sonuc_path = os.path.join(girisimler_yolu, filename, "Sonuç.txt")
                if os.path.isfile(sonuc_path):
                    encoding = detect_encoding(sonuc_path)
                    try:
                        with open(sonuc_path, "r", encoding=encoding) as f:
                            content = f.read().strip().lower()
                            print(f"Dosya: {sonuc_path}, İçerik: '{content}'") 
                            if content == "başarılı":
                                listbox.insert(tk.END, f"{filename} - Başarılı")
                            elif content == "başarısız":
                                listbox.insert(tk.END, f"{filename} - Başarısız")
                            else:
                                listbox.insert(tk.END, f"{filename} - Devam Ediyor")
                    except UnicodeDecodeError:
                        messagebox.showerror("Hata", f"Dosya kodlaması okuma sırasında sorun yarattı: {sonuc_path}")
                else:
                    listbox.insert(tk.END, f"{filename} - Sonuç Dosyası Yok")
    except FileNotFoundError:
        messagebox.showerror("Hata", "Belirtilen dosya yolu bulunamadı.")
    except PermissionError:
        messagebox.showerror("Hata", "Dosya yoluna erişim izni yok.")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")


def dosya_yolu_sec():
    global girisimler_yolu
    girisimler_yolu = filedialog.askdirectory()
    if girisimler_yolu:
        update_file_list() 

def durum_guncelle(event):
    selected = listbox.curselection()
    if not selected:
        return

    selected_item = listbox.get(selected)
    selected_girisim = selected_item.split(" - ")[0]
    klasor_yolu = os.path.join(girisimler_yolu, selected_girisim)
    sonuc_path = os.path.join(klasor_yolu, "Sonuç.txt")

    def on_select(option):
        if option != "iptal":
            try:
                with open(sonuc_path, "w", encoding="utf-8") as f:
                    f.write(option.lower())  
                print(f"Güncellenen Dosya: {sonuc_path}, İçerik: {option.lower()}") 
                update_file_list() 
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya güncellenirken bir hata oluştu: {e}")

    durum_penceresi = tk.Toplevel(root)
    durum_penceresi.title("Durum Güncelle")
    durum_penceresi.geometry("400x200")
    durum_penceresi.grab_set()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (400/2))
    y_cordinate = int((screen_height/2) - (200/2))
    durum_penceresi.geometry(f"400x200+{x_cordinate}+{y_cordinate}")

    durum_penceresi.configure(bg="#333333")

    durum_penceresi.overrideredirect(True)

    tk.Label(durum_penceresi, text="Durum?", font=("Arial", 14), bg="#333333", fg="#ffffff").pack(pady=10)

    style = ttk.Style()
    style.configure('TButton', background='#444444', foreground='#ffffff', font=('Arial', 12))

    for option in ["Başarılı", "Başarısız", "iptal"]:
        ttk.Button(durum_penceresi, text=option, command=lambda opt=option: [durum_penceresi.destroy(), on_select(opt)]).pack(pady=5, padx=10, fill='x')

root = tk.Tk()
root.title("R")
fullscreen = False
girisimler_yolu = ""

style = ttk.Style()
style.theme_use("clam")  

root.configure(bg="#333333")

video_label = tk.Label(root)
video_label.place(relx=0.5, rely=0.5, anchor="center")

r_label = ttk.Label(root, text="R 2.3", font=("Arial", 24, "bold"), background="#333333", foreground="#ffffff")
r_label.place(relx=0.5, rely=0.05, anchor="center")

left_frame = ttk.Frame(root, padding=10)
left_frame.place(relx=0.05, rely=0.5, anchor="w")

listbox = tk.Listbox(left_frame, font=("Arial", 16, "bold"), background="#333333", foreground="#ffffff", width=40, height=20)
listbox.pack(padx=10, pady=10)
listbox.bind("<Double-Button-1>", durum_guncelle)

right_frame = ttk.Frame(root,padding=10)
right_frame.place(relx=0.95, rely=0.5, anchor="e")

fikir_label = ttk.Label(right_frame, text="Fikir", font=("Arial", 14), background="#dcdad5", foreground="#ffffff")
fikir_label.pack(pady=10)

fikir_entry = tk.Text(right_frame, font=("Arial", 14), width=40, height=5, bg="#333333", fg="#ffffff", bd=1, insertbackground='white')
fikir_entry.pack(pady=5, padx=5, fill=tk.X)

arastirma_label = ttk.Label(right_frame, text="Araştırma", font=("Arial", 14), background="#dcdad5", foreground="#ffffff")
arastirma_label.pack(pady=10)

arastirma_entry = tk.Text(right_frame, font=("Arial", 14), width=40, height=5, bg="#333333", fg="#ffffff", bd=1, insertbackground='white')
arastirma_entry.pack(pady=5, padx=5, fill=tk.X)

style.configure('TButton',
                background='#555555', 
                foreground='#ffffff', 
                bordercolor='#ffffff',
                relief='flat', 
                font=('Arial', 12), 
                padding=5)
style.map('TButton',
          background=[('active', '#666666')],  
          bordercolor=[('pressed', '#ffffff')])  

ttk.Button(right_frame, text="Oluştur", command=olustur).pack(pady=10, fill='x')
ttk.Button(right_frame, text="Dosya Yolu Seç", command=dosya_yolu_sec).pack(pady=10, fill='x')
ttk.Button(right_frame, text="Çıkış", command=cikis).pack(pady=10, fill='x')

status_label = tk.Label(root, text="", font=("Arial", 12), bg="#333333", fg="#ffffff")
status_label.place(relx=0.5, rely=0.95, anchor="center")

play_video()

root.bind("<Escape>", end_fullscreen)
root.bind("<F11>", toggle_fullscreen)
root.bind("<r>", dead)

root.mainloop()