#pip install opencv-python pillow
import tkinter as tk
import pygame
import sys, os
from tkinter import Label, Button
from PIL import Image, ImageTk
from config import LANG,AppState # đây là file main.py chứa class GoGame
from setting import Setting
from modewindow import ModeWindow

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file khi dùng PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class StartWindow:
    def __init__(self, root):
        self.root = root
        # icon, title, background
        root.iconbitmap(resource_path("game/icongame.ico"))
        self.root.title(LANG[AppState.language]["title"])
        self.root.configure(bg="beige")
        # full screen
        self.root.state("zoomed")
        # tiêu đề chính
        Label(self.root,
              text=LANG[AppState.language]["title"],
              font=("Arial", 30, "bold"),
              bg="beige").pack(pady=20)

        # banner image
        self.load_image()

        # nút âm thanh
        self.sound_button = Button(self.root,
                                   text="🔊",
                                   font=("Arial", 14),
                                   command=self.toggle_sound)
        self.sound_button.place(x=10, y=10)

        # cấu hình chung cho các nút chính
        btn_cfg = {
            "font": ("Arial", 28),
            "width": 20,
            "height": 2
        }
        # nút Bắt đầu
        Button(
            self.root,
            text=LANG[AppState.language]["start"],
            command=self.start_game,
            **btn_cfg
        ).pack(pady=20)
        
        # nút Cài đặt
        Button(
            self.root,
            text=LANG[AppState.language]["setting"],
            command=self.open_settings,
            **btn_cfg
        ).pack(pady=20)
        

        # nút Thoát
        Button(
            self.root,
            text=LANG[AppState.language]["exit"],
            command=self.quit_app,
            **btn_cfg
        ).pack(pady=20)

        # khởi pygame mixer
        pygame.mixer.init()
        self.bg_music = pygame.mixer.Sound(resource_path("game/Re.wav"))
        self.channel = self.bg_music.play(loops=-1)
        self.update_sound_state(True)
        self.root.bind("<Map>", self.on_map)

    
    def quit_app(self):
        pygame.mixer.quit()
        self.root.destroy()
        import sys
        sys.exit()

    def load_image(self):
        
        try:
            img = Image.open(resource_path("game/startwindow.jpg"))
            # Lấy kích thước màn hình để scale ảnh
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w = int(sw * 0.5)
            h = int(sh * 0.3)
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            Label(self.root, image=self.photo, bg="beige").pack(pady=20)
        except Exception as e:
            print("Không thể tải ảnh start:", e)

    def update_sound_state(self, sound_on):
        AppState.sound_on = sound_on
        self.sound_button.config(text="🔊" if sound_on else "🔇")
        if not sound_on:
            pygame.mixer.stop()
        else:
            if self.channel is None or not self.channel.get_busy():
                self.channel = self.bg_music.play(loops=-1)

    def toggle_sound(self):
        self.update_sound_state(not AppState.sound_on)
        if AppState.sound_on:
            self.sound_button.config(text="🔊")
            if not self.channel.get_busy():
                self.channel = self.bg_music.play(loops=-1)
        else:
            self.sound_button.config(text="🔇")
            pygame.mixer.stop()

    def on_map(self, event):
        # khi window được hiện lại
        if AppState.sound_on and not self.channel.get_busy():
            self.channel = self.bg_music.play(loops=-1)

    def start_game(self):
    # dừng nhạc, ẩn launcher
        pygame.mixer.stop()
        self.root.withdraw()
    # Mở cửa sổ chọn chế độ
        mode_win = tk.Toplevel(self.root)
        ModeWindow(mode_win, language=AppState.language, parent=self)


    def open_settings(self):
        # Dừng nhạc và ẩn launcher
        pygame.mixer.stop()
        self.root.withdraw()
        # Mở cửa sổ Setting
        setting_win = tk.Toplevel(self.root)
        # Truyền parent để Setting có thể quay lại đây
        Setting(setting_win, parent=self)

    def launch_game(self, mode):
        self.root.destroy()
        
        if mode == "human":
            # khởi PvP
            from main_pvp import PvPGame
            new_root = tk.Tk()
            try:
                new_root.state("zoomed")                # Windows
            except:
                new_root.attributes("-fullscreen", True)  # macOS/Linux
            PvPGame(new_root, language=AppState.language)
            new_root.mainloop()
        else:
            # khởi AI
            from main13 import GoGame
            new_root = tk.Tk()
            try:
                new_root.state("zoomed")                # Windows
            except:
                new_root.attributes("-fullscreen", True)  # macOS/Linux
            GoGame(new_root)
            new_root.mainloop()

if __name__ == "__main__":
    import pygame
    pygame.init()
    root = tk.Tk()
    StartWindow(root)
    root.mainloop()
