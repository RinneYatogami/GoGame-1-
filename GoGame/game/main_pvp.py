import tkinter as tk
from tkinter import messagebox
from remenu import ReMenu
import copy, time
import pygame
from config import AppState
BOARD_SIZE = 9
STONE_RADIUS_RATIO = 0.45
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
        "title": "CỜ VÂY 9X9 – PvP",
        "turn_black": "Lượt đi của Đen",
        "turn_white": "Lượt đi của Trắng",
        "pass": "PASS LƯỢT",
        "restart": "RESTART",
        "score_black": "Điểm Đen: {}",
        "score_white": "Điểm Trắng: {}",
        "time_black": "Đen: {} (s)",
        "time_white": "Trắng: {} (s)",
    },
    "en": {
        "title": "GO GAME 9x9 – PvP",
        "turn_black": "Black's Turn",
        "turn_white": "White's Turn",
        "pass": "PASS",
        "restart": "RESTART",
        "score_black": "Black Score: {}",
        "score_white": "White Score: {}",
        "time_black": "Black: {} (s)",
        "time_white": "White: {} (s)",
    }
}


class PvPGame:
    def __init__(self, root, language="vi"):
        self.L = LANG[language]
        self.root = root
        root.iconbitmap(resource_path("game/icongame.ico"))
        root.title(self.L["title"])
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # --- khởi nhạc nền cho PvPGame ---
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path("game/Re2.wav"))
        pygame.mixer.music.play(loops=-1)
        self.sound_on = True

    # --- nút âm thanh ---
        self.sound_button = tk.Button(
        self.frame, text="🔊", font=("Arial",14),
        command=self.toggle_sound, width=2
    )
        self.sound_button.place(x=50, y=10)

        # --- directions for neighbor checks ---
        self.dirs = [(-1,0),(1,0),(0,-1),(0,1)]

        # --- timers ---
        self.last_time = time.time()
        self.black_time = 5*60
        self.white_time = 5*60
        self.black_timer = tk.Label(self.frame, text=self.L["time_black"].format(self._fmt(self.black_time)), font=("Arial",14))
        self.black_timer.pack(side=tk.LEFT, padx=10)
        self.white_timer = tk.Label(self.frame, text=self.L["time_white"].format(self._fmt(self.white_time)), font=("Arial",14))
        self.white_timer.pack(side=tk.RIGHT, padx=10)

        # prisoners count
        self.black_prisoners = 0
        self.white_prisoners = 0

        # turn
        self.turn = 1
        self.turn_label = tk.Label(self.frame, text="", font=("Arial",16))
        self.turn_label.pack(side=tk.TOP, pady=5)
        self._update_turn_label()

        # score
        self.score_label = tk.Label(self.frame, text=self.L["score_black"].format(0) + "   " + self.L["score_white"].format(0), font=("Arial",14))
        self.score_label.pack(side=tk.TOP, pady=2)

        #Huong dan choi
        self.help_button = tk.Button(self.frame, text="?", font=("Arial", 14, "bold"),
        command=self.show_help, width=2)
        self.help_button.place(x=10, y=10)  # Gắn ở góc trái trên cùng

        # ——— Nút menu ☰ ———
        self.menu_button = tk.Button(self.frame,
                                    text="☰",
                                    font=("Arial", 16),
                                    command=lambda: ReMenu(self.root))
        # đặt bên cạnh nút Help, bạn có thể chỉnh x/y cho phù hợp
        self.menu_button.place(relx=1.0, x=-10, y=10, anchor="ne")


        

        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        # canvas
        self.canvas = tk.Canvas(self.frame, bg="#F0D9B5")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        # control buttons
        tk.Button(self.frame, text=self.L["pass"], command=self._pass,    width=12).pack(side=tk.LEFT,  padx=10, pady=10)
        tk.Button(self.frame, text=self.L["restart"], command=self._restart, width=12).pack(side=tk.RIGHT, padx=10, pady=10)

        # board state
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous = None
        self.stones = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]

        # start clock updates
        self._update_clocks()

    def toggle_sound(self):
        if self.sound_on:
            pygame.mixer.music.pause()
            self.sound_button.config(text="🔇")
        else:
            pygame.mixer.music.unpause()
            self.sound_button.config(text="🔊")
        self.sound_on = not self.sound_on

    def _fmt(self, sec):
        m = int(sec//60); s = int(sec%60)
        return f"{m:02d}:{s:02d}"

    def _update_clocks(self):
        now = time.time(); delta = now - self.last_time; self.last_time = now
        if self.turn == 1:
            self.black_time = max(0, self.black_time - delta)
        else:
            self.white_time = max(0, self.white_time - delta)
        self.black_timer.config(text=self.L["time_black"].format(self._fmt(self.black_time)))
        self.white_timer.config(text=self.L["time_white"].format(self._fmt(self.white_time)))
        if self.black_time>0 and self.white_time>0:
            self.root.after(200, self._update_clocks)

    #Luat choi/Huong dan choi
    def show_help(self):
        # Tạo cửa sổ Help với scrollbar và font lớn hơn
        help_win = tk.Toplevel(self.root)
        help_win.iconbitmap(resource_path("game/icongame.ico"))
        help_win.title(self.L.get("help_title", "Hướng dẫn chơi"))
        help_win.geometry("400x300")  # Kích thước cửa sổ có thể điều chỉnh

        # Khung chứa Text và Scrollbar
        frame = tk.Frame(help_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar dọc
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Widget Text với wrap và font lớn
        text_widget = tk.Text(
            frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Arial", 14)
        )
        text_widget.insert(tk.END, (
            "🎯 Hướng dẫn chơi Cờ Vây 9x9:\n\n"
            "1. Quy tắc cơ bản\n\n"
            "Điều 1: Khi bắt đầu trận đấu, trên bàn cờ sẽ không có bất kỳ một quân nào và sau đó người cầm quân Đen được phép đi trước.\n"
            "Điều 2: Bạn có thể đặt quân cờ vào bất kỳ giao điểm nào mà bạn muốn. Tuy nhiên, tuyệt đối Không được đặt vào giữa hay trên cạnh của ô vuông và chỉ được đặt quân trong phạm vi của bàn cờ mà thôi.\n"
            "Điều 3: Quân cờ một khi đã đặt xuống bàn cờ là không được đi lại, bất di bất dịch (trừ trường hợp bị ăn quân).\n"
            "Điều 4: Sau khi đặt 1 quân cờ xuống bàn thì lượt của bạn sẽ kết thúc và đến lượt của đối thủ (hoặc ngược lại). Nếu bên nào vi phạm đặt từ 2 quân trở lên trong một lượt đi sẽ bị xử thua.\n"
            "Điều 5: Khi đến lượt của mình, người chơi có thể bỏ lượt không đi, khi cả 2 người chơi cùng bỏ lượt thì ván cờ sẽ kết thúc và thắng thua sẽ được định đoạt bằng cách đếm số quân cờ đã được đặt trên bàn cờ, người chơi nào có số quân cờ được đặt nhiều hơn là giành chiến thắng.\n\n"
            "2. Luật ăn quân\n\n"
            "*Đầu tiên, ta sẽ tìm hiểu về khái niệm Khí của mỗi quân cờ:\n" 
            "-Khi một quân cờ được đặt xuống tại vị trí bất kỳ trên bàn cờ thì tất cả các giao điểm nằm sát theo chiều ngang và dọc của quân cờ đó (không tính giao điểm nằm chéo) là khí của nó.\n"
            "-Đặc biệt: Bạn có thể đặt nhiều quân cờ sát vào nhau để mở rộng Khí. Tuy nhiên, những quân cờ nằm ở vị trí chéo (ví dụ A và B) thì sẽ không mở rộng khí cho nhau dù đang được đặt sát nhau.\n"
            "*Luật ăn quân:\n"
            "-Cứ mỗi một quân cờ của địch đặt vào ô khí của quân cờ của mình thì quân cờ của mình sẽ mất ô khí đó.\n"
            "-Bất kỳ quân cờ nào không còn ô khí sẽ lập tức bị loại khỏi ván đấu.\n"
            "-Như trong hình, nếu quân trắng đặt vào những vị trí x trên bản đồ thì sẽ ăn được những quân đen đã được đánh dấu.\n"
            "*Điểm hết khí:\n"
            "-Miễn là vị trí đó còn khí thì ta có thể đặt cờ vào.\n" 
            "-Nếu tại vị trí muốn đặt quân là điểm hết khí nhưng lại là điểm nối quân của mình thì vẫn được phép đặt quân.\n"
            "Ví dụ: Điểm tam giác là điểm hết khí của đen nên quân đen sẽ không được phép đặt vào. Nhưng đây lại là điểm nối quân của trắng nên quân trắng được phép đặt.\n"
            "*Ngoại lệ: Ta vẫn được phép đặt vào điểm hết khí trong trường hợp có thể ăn được quân đối phương. Ở minh họa bên dưới, khi quân đen đi vào các vị trí tam giác thì những quân trắng bị hết khí sẽ bị loại khỏi ván đấu.\n\n"
            "3. Đất - Mục tiêu của ván cờ\n\n"
            "Để có thể giành chiến thắng, bạn phải thu được càng nhiều Đất càng tốt:\n"
            "-Đất là số giao điểm trống trên bàn cờ mà quân mình bao vây được (có thể tính trong phạm vi giữa quân mình với các cạnh biên của bàn cờ).\n"
            "-Khi bản thân cảm thấy đã chiếm hết đất trong khả năng của mình thì người chơi có thể bỏ lượt. Khi cả 2 người chơi đều bỏ lượt thì ván đấu sẽ kết thúc và bắt đầu đếm đất để quyết định thắng thua.\n"
            "Lưu ý: Quân Trắng sẽ được cộng 5.5 đến 6.5 Đất tùy giao ước trước trận đấu vì bị chịu thiệt thòi là bắt đầu sau quân Đen.\n\n"
            "4. Tạo Mắt cho các quân cờ để đề phòng trường hợp bị bao vây\n\n"
            "-Mắt: là điểm hết khí (hay giao điểm) được quân ta bao vây xung quanh và cũng là nơi đối phương không được phép đặt quân vào.\n"
            "-Trường hợp có 1 mắt: Nếu bạn có thể bao vậy toàn bộ đám quân địch chỉ có một mắt như hình bên dưới thì có thể ăn tất cả bọn chúng.\n"
            "-Trong trường hợp có 2 mắt trở lên: Ví dụ như hình bên dưới, ta sẽ có 2 mắt là A và B thì dù trắng có bao vây hết đám quân của đen và đặt một quân vào một mắt bất kỳ (A hoặc B) thì quân đen vẫn còn một mắt để vận khí. Ngay lập tức quân trắng vừa đặt vào đó sẽ bị loại và quân đen vẫn sẽ sống.\n\n"
            "5. Thu Quan\n\n"
            "Thu Quan sẽ diễn khi mà ranh giới của mỗi quân đã được hình thành nhưng vẫn có thể đi tiếp (thường là giai đoạn giữa ván đấu trở về sau). 2 người chơi sẽ bắt đầu mở rộng hay chiếm thêm đất cho mình vì lúc này đã có phòng tuyến vững chắc phía sau.\n\n"
            "6. Kết thúc ván cờ\n\n"
            "Khi cả 2 người chơi đều từ bỏ lượt của mình thì ván cờ sẽ kết thúc. Lúc này thắng thua sẽ được định đoạt bằng cách đếm Đất của mỗi người. Người chơi nào giành được nhiều Đất hơn sẽ giành chiến thắng. Lưu ý: Trắng đi sau chịu nhiều bất lợi (vì phải đi sau) nên sẽ được cộng 5.5 đến 6.5 Đất tùy giao ước trước khi bắt đầu trận đấu.\n\n"


        ))
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Kết nối scrollbar
        scrollbar.config(command=text_widget.yview)

    def _update_turn_label(self):
        txt = self.L["turn_black"] if self.turn==1 else self.L["turn_white"]
        self.turn_label.config(text=txt)

    def _update_score(self):
        b,w = self._calc_score()
        self.score_label.config(text=self.L["score_black"].format(b) + "   " + self.L["score_white"].format(w))

    def _on_resize(self, event):
        self.canvas.delete("all")
        w,h = event.width, event.height
        self.cell = min(w,h)/(BOARD_SIZE+1)
        self.rad  = self.cell * STONE_RADIUS_RATIO
        self.x0 = (w - self.cell*(BOARD_SIZE-1))/2
        self.y0 = (h - self.cell*(BOARD_SIZE-1))/2
        self._draw_grid(); self._draw_stones()

    def _draw_grid(self):
        for i in range(BOARD_SIZE):
            x = self.x0 + i*self.cell
            y = self.y0 + i*self.cell
            self.canvas.create_line(x, self.y0, x, self.y0+(BOARD_SIZE-1)*self.cell)
            self.canvas.create_line(self.x0, y, self.x0+(BOARD_SIZE-1)*self.cell, y)

    def _draw_stones(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != 0:
                    fill = "black" if self.board[r][c]==1 else "white"
                    x = self.x0 + c*self.cell
                    y = self.y0 + r*self.cell
                    self.canvas.create_oval(x-self.rad, y-self.rad, x+self.rad, y+self.rad, fill=fill, outline="black")

    def _on_click(self, event):
        col = round((event.x - self.x0)/self.cell)
        row = round((event.y - self.y0)/self.cell)
        if 0<=row<BOARD_SIZE and 0<=col<BOARD_SIZE and self._is_legal(row,col,self.turn):
            self.previous = copy.deepcopy(self.board)
            self.board[row][col] = self.turn
            self._capture(row, col, 3-self.turn)
            self.turn = 3 - self.turn
            self._update_turn_label(); self._update_score()
            self.canvas.delete("all"); self._draw_grid(); self._draw_stones()

    def _pass(self):
        self.previous = copy.deepcopy(self.board)
        self.turn = 3 - self.turn
        self._update_turn_label(); self._update_score()

    def _restart(self):
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous = None; self.turn = 1
        self.black_time = self.white_time = 5*60
        self.black_prisoners=0
        self.white_prisoners=0
        self._update_turn_label(); self._update_score()
        self.canvas.delete("all"); self._draw_grid()

    def _group(self, board, r, c, col, visited=None):
        if visited is None: visited = set()
        if (r,c) in visited: return visited
        visited.add((r,c))
        for dr,dc in self.dirs:
            nr, nc = r+dr, c+dc
            if 0<=nr<BOARD_SIZE and 0<=nc<BOARD_SIZE and board[nr][nc]==col:
                self._group(board, nr, nc, col, visited)
        return visited

    def _has_lib(self, board, group):
        for r,c in group:
            for dr,dc in self.dirs:
                nr,nc = r+dr, c+dc
                if 0<=nr<BOARD_SIZE and 0<=nc<BOARD_SIZE and board[nr][nc]==0:
                    return True
        return False

    def _simulate(self, board, r, c, col):
        new = copy.deepcopy(board)
        new[r][c] = col
        opp = 3 - col
        for dr,dc in self.dirs:
            nr,nc = r+dr, c+dc
            if 0<=nr<BOARD_SIZE and 0<=nc<BOARD_SIZE and new[nr][nc]==opp:
                grp = self._group(new, nr, nc, opp)
                if not self._has_lib(new, grp):
                    for rr,cc in grp:
                        new[rr][cc] = 0
        return new

    def _is_legal(self, r, c, col):
        if self.board[r][c] != 0: return False
        new = self._simulate(self.board, r, c, col)
        grp = self._group(new, r, c, col)
        if not self._has_lib(new, grp): return False
        if self.previous and new == self.previous: return False
        return True

    def _capture(self, r, c, opp):
        to_remove = []
        for dr,dc in self.dirs:
            nr,nc = r+dr, c+dc
            if 0<=nr<BOARD_SIZE and 0<=nc<BOARD_SIZE and self.board[nr][nc]==opp:
                grp = self._group(self.board, nr, nc, opp)
                if not self._has_lib(self.board, grp):
                    to_remove += list(grp)
        for rr,cc in to_remove:
            self.board[rr][cc] = 0
            if opp == 1: self.white_prisoners += 1
            else:       self.black_prisoners += 1

    def _calc_score(self):
        b = self.black_prisoners; w = self.white_prisoners
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c]==1: b += 1
                elif self.board[r][c]==2: w += 1
        return b,w

if __name__ == "__main__":
    root = tk.Tk(); root.geometry("600x600")
    PvPGame(root, language="vi")
    root.mainloop()