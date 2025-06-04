import tkinter as tk
import pygame
from tkinter import messagebox
from config import LANG,AppState
import sys, os

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file khi dùng PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class ReMenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        # Xóa hoàn toàn title bar và border
        self.overrideredirect(True)

        self.configure(bg="#cccccc")  # nền ngoài cùng

        # Frame để tạo viền
        border_frame = tk.Frame(self, bg="white", bd=2, relief="solid")
        border_frame.place(relx=0.5, rely=0.5, anchor="center", width=260, height=160)

        # Nút trong frame
       
        # Kích thước cửa sổ
        width, height = 300, 200
        # Căn giữa so với cửa sổ cha
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        close_button = tk.Button(self, text="X", command=self.destroy,
                                 bg="black", fg="white", font=("Arial", 12, "bold"),
                                 width=5, height=1, relief="raised")
        close_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        # Nút Trở về Màn hình chính - đặt giữa
        # Nút Trở về Màn hình chính
        self.btn_return = tk.Button(
                                    self,
                                    text=LANG[AppState.language]["return_home"],
                                    command=self.on_return,
                                    font=("Arial", 14, "bold"),
                                    width=20,
                                    height=1
                                    )
        self.btn_return.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.btn_exit = tk.Button(
                                    self,
                                    text=LANG[AppState.language]["exit"],
                                    command=self.on_exit,
                                    font=("Arial", 14, "bold"),
                                    width=10,
                                    height=1
                                    )
        self.btn_exit.place(relx=0.5, rely=0.6, anchor=tk.CENTER)



    def update_language(self):
        self.btn_return.config(text=LANG[AppState.language]["return_home"])
        self.btn_exit.config(text=LANG[AppState.language]["exit"])

    def on_return(self):
        self.destroy()
        pygame.mixer.music.stop()
        self.master.destroy()  # đóng cửa sổ game hiện tại

    # Mở lại StartWindow
        import startgame
        new_root = tk.Tk()
        startgame.StartWindow(new_root)
        new_root.mainloop()

    def on_exit(self):
        # Thoát khỏi trò chơi
        pygame.mixer.music.stop()
        self.master.destroy()

def create_main_window():
    root = tk.Tk()
    root.title("Game với Menu")
    root.geometry("400x400")

    # Nút Menu ☰
    menu_button = tk.Button(root, text="☰", font=("Arial", 16), command=lambda: ReMenu(root))
    menu_button.place(x=10, y=10)

    return root

if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()
