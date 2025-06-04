# modewindow.py

import tkinter as tk
from config import AppState

# Ngôn ngữ cho cửa sổ Chọn chế độ
LANG = {
    "vi": {"mode_title": "Chọn chế độ", "pvp": "Người vs Người", "pvai": "Người vs Máy", "exit": "Thoát"},
    "en": {"mode_title": "Choose Mode", "pvp": "Player vs Player", "pvai": "Player vs AI", "exit": "Exit"},
}
import sys, os

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file khi dùng PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class ModeWindow:
    def __init__(self, root, language=None, parent=None):
        self.root = root
        self.language = language or AppState.language
        self.parent = parent

        # Thiết lập window
        try:
            self.root.iconbitmap(resource_path("game/icongame.ico"))
        except Exception:
            pass
        self.root.title(LANG[self.language]["mode_title"])
        self.root.configure(bg="beige")

        # Fullscreen / Zoom (Windows) hoặc Fullscreen attribute
        try:
            self.root.state("zoomed")
        except Exception:
            try:
                self.root.attributes("-fullscreen", True)
            except Exception:
                pass

        # Khung chứa nội dung
        frame = tk.Frame(self.root, bg="beige")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        tk.Label(
            frame,
            text=LANG[self.language]["mode_title"],
            font=("Arial", 24, "bold"),
            bg="beige"
        ).pack(pady=(0,15))

        btn_cfg = {
        "font": ("Arial", 18),
        "width": 30,
        "height": 2
}
        # Nút Người vs Người
        tk.Button(
            frame,
            text=LANG[self.language]["pvp"],
            command=self.select_pvp,
            **btn_cfg
        ).pack(pady=20)

        # Nút Người vs Máy
        tk.Button(
            frame,
            text=LANG[self.language]["pvai"],
            command=self.select_pvai,
            **btn_cfg
        ).pack(pady=20)

        # Nút Thoát về StartWindow
        tk.Button(
            frame,
            text=LANG[self.language]["exit"],
            command=self.back_to_start,
            **btn_cfg
        ).pack(pady=(20, 0))

    def select_pvp(self):
        AppState.mode = "human"
        self.root.destroy()
        if self.parent and hasattr(self.parent, 'launch_game'):
            self.parent.launch_game("human")
    def select_pvai(self):
        AppState.mode = "ai"
        self.root.destroy()
        if self.parent and hasattr(self.parent, 'launch_game'):
            self.parent.launch_game("ai")



    def back_to_start(self):
        # Đóng và trả về StartWindow
        self.root.destroy()
        if self.parent and hasattr(self.parent, 'root'):
            # Hiện lại StartWindow
            self.parent.root.deiconify()
            # Khôi phục fullscreen
            try:
                self.parent.root.state("zoomed")           # Windows
            except Exception:
                self.parent.root.attributes("-fullscreen", True)

    def _finish_selection(self, mode):
        # Đóng và gọi phương thức từ StartWindow
        self.root.destroy()
        if self.parent and hasattr(self.parent, 'launch_game'):
            self.parent.launch_game(mode)
