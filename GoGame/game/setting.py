import tkinter as tk
import pygame
from tkinter import Label, Button

from config import LANG, AppState
import sys, os

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file khi dùng PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
LANG = {
    "vi": {
        # StartWindow
        "title":            "Cờ Vây 9x9",
        "start":            "Bắt đầu",
        "setting":          "Cài đặt",
        "exit":             "Thoát",
        # GoGame
        "turn_black":       "Lượt đi của Đen",
        "turn_white":       "Lượt đi của Trắng",
        "pass":             "PASS LƯỢT",
        "restart":          "RESTART",
        "score_black":      "Điểm Đen: {}",
        "score_white":      "Điểm Trắng: {}",
        "time_black":       "Đen: {} (s)",
        "time_white":       "Trắng: {} (s)",
    },
    "en": {
        # StartWindow
        "title":            "Go Game 9x9",
        "start":            "Start",
        "setting":          "Settings",
        "exit":             "Exit",
        # GoGame
        "turn_black":       "Black's Turn",
        "turn_white":       "White's Turn",
        "pass":             "PASS",
        "restart":          "RESTART",
        "score_black":      "Black Score: {}",
        "score_white":      "White Score: {}",
        "time_black":       "Black: {} (s)",
        "time_white":       "White: {} (s)",
    }
}



class Setting:
    def __init__(self, root, language="vi", sound_on=True, parent=0):
        self.root = root
        self.L = LANG[AppState.language]
        self.sound_on = sound_on
       
        self.parent = parent
        self.root.title("Cài đặt")
        self.root.configure(bg="beige")
        root.iconbitmap(resource_path("game/icongame.ico"))
        self.root.state("zoomed")

        Label(self.root,
              text=self.L["setting"],
              font=("Arial",24,"bold"),
              bg="beige").pack(pady=10)
        btn_cfg = {
        "font": ("Arial", 18),
        "width": 30,
        "height": 2
        }
        Button(
            self.root,
            text="Tiếng Việt" if AppState.language == "vi" else "Vietnamese",
            command=lambda: self.change_language("vi"),
            **btn_cfg
        ).pack(pady=20)

        Button(
            self.root,
            text="Tiếng Anh" if AppState.language == "vi" else "English",
            command=lambda: self.change_language("en"),
            **btn_cfg
        ).pack(pady=20)

        Button(
            self.root,
            text=self.L["exit"],
            command=self.back_to_start,
            **btn_cfg
        ).pack(pady=20)

    def change_language(self, lang):
    
        pygame.mixer.stop()
        AppState.language = lang
        

        if hasattr(self.root.master, "background_music"):
            self.root.master.background_music.stop()

        self.root.destroy()
        if self.parent:
            self.parent.root.destroy()
            import tkinter as tk
            from startgame import StartWindow  # NHÉT VÀO ĐÂY ĐỂ TRÁNH VÒNG LẶP IMPORT
            new_root = tk.Tk()
            StartWindow(new_root)
            new_root.mainloop()

    def back_to_start(self):
        pygame.mixer.stop()
        self.root.destroy()

        if self.parent and hasattr(self.parent, 'root'):
            self.parent.root.deiconify()
            try:
                self.parent.root.state("zoomed")
            except Exception:
                self.parent.root.attributes("-fullscreen", True)
