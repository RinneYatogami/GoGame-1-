import tkinter as tk
import pygame
from tkinter import messagebox
import threading
from remenu import ReMenu
from config import LANG,AppState
import ai

import copy
import math
import time

end=False
BOARD_SIZE = 9
STONE_RADIUS_RATIO = 0.45
TIME_LIMIT = 0.3
MAX_DEPTH = 3
import sys, os

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file khi dùng PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class GoGame:
    def __init__(self, root ,language="vi"):
        self.L = LANG[AppState.language]
        self.root = root
        self.root.iconbitmap(resource_path("game/icongame.ico"))
        root.title(self.L["title"])
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

         # --- khởi nhạc nền cho GoGame ---
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path("game/Re2.wav"))
        pygame.mixer.music.play(loops=-1)
        self.sound_on = True

        # --- tạo nút âm thanh ---
        self.sound_button = tk.Button(
        self.frame, text="🔊", font=("Arial", 14),
        command=self.toggle_sound, width=2
    )
        self.sound_button.place(x=50, y=10) 

        self.last_time = time.time()

        # --- thiết lập thời gian (tính bằng giây) ---
        self.black_time = 5 * 60
        self.white_time = 5 * 60

         # --- labels đếm giờ ---
        self.black_timer_label = tk.Label(
            self.frame,
            text=self.L["time_black"].format(self.format_time(self.black_time)),
            font=("Arial",14)
        )
        self.black_timer_label.pack(side=tk.LEFT, padx=10)

        self.white_timer_label = tk.Label(
            self.frame,
            text=self.L["time_white"].format(self.format_time(self.white_time)),
            font=("Arial",14)
        )
        self.white_timer_label.pack(side=tk.RIGHT, padx=10)

        self.black_prisoners = 0
        self.white_prisoners = 0

         # Khởi tạo lượt đi trước khi cập nhật Label
        self.turn = 1
        #Label thong bao luot di
        self.turn_label = tk.Label(self.frame, text="", font=("Arial", 16))
        self.turn_label.pack(side=tk.TOP, pady=5)
        self.update_turn_label()  # Cập nhật lượt đi ban đầu

        # --- score label ---
        self.score_label = tk.Label(
            self.frame,
            text=f"{self.L['score_black'].format(0)}   {self.L['score_white'].format(0)}",
            font=("Arial",14)
        )
        self.score_label.pack(side=tk.TOP,pady=2)
        

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


        self.canvas = tk.Canvas(self.frame, bg="#F0D9B5")
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)

            # --- các nút PASS, RESTART ---
        self.pass_button = tk.Button(
            self.frame,
            text=self.L["pass"],
            command=self.pass_turn,
            width=12
        )
        self.pass_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.restart_button = tk.Button(
            self.frame,
            text=self.L["restart"],
            command=self.restart_game,
            width=12
        )
        self.restart_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.previous_board = None
        self.stones = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = 1

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_click)

        # sau cùng trong __init__, khởi động đồng hồ
        self.update_clocks()

        
    def toggle_sound(self):
        if self.sound_on:
            pygame.mixer.music.pause()
            self.sound_button.config(text="🔇")
        else:
            pygame.mixer.music.unpause()
            self.sound_button.config(text="🔊")
        self.sound_on = not self.sound_on

    # --- thêm hàm format giây thành MM:SS ---
    def format_time(self, sec):
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"
    
    # --- hàm đếm ngược, chạy mỗi 1 giây ---
    def update_clocks(self):
        now = time.time()
        # tính khoảng thời gian trôi qua kể từ lần update trước
        delta = now - self.last_time
        # cập nhật mốc thời gian
        self.last_time = now

        # trừ delta vào timer bên đang đi
        if self.turn == 1 and self.black_time > 0:
            self.black_time = max(0, self.black_time - delta)
        elif self.turn == 2 and self.white_time > 0:
            self.white_time = max(0, self.white_time - delta)

        # cập nhật hiển thị
        self.black_timer_label.config(
            text=f"Black: {self.format_time(int(self.black_time))} (s)")
        self.white_timer_label.config(
            text=f"White: {self.format_time(int(self.white_time))} (s)")

        # nếu cả hai bên còn time → gọi lại
        if self.black_time > 0 and self.white_time > 0:
            self.root.after(200, self.update_clocks)
        else:
            loser = "Black" if self.black_time == 0 else "White"
            messagebox.showinfo("Time Up", f"{loser} hết giờ! Game Over.")
    
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
        

    def update_timer_labels(self):
        self.black_timer_label.config(
            text=f"Black: {self.format_time(int(self.black_time))} (s)")
        self.white_timer_label.config(
            text=f"White: {self.format_time(int(self.white_time))} (s)")
        
    def record_elapsed_and_switch(self, new_turn):
        """Chuyển lượt: đặt lại last_time, cập nhật turn và các label."""
        # chuyển lượt
        self.turn = new_turn
        # đặt lại mốc thời gian để update_clocks không tính delta cũ
        self.last_time = time.time()
        # cập nhật label lượt đi và countdown
        self.update_turn_label()
        self.update_timer_labels()
        # chuyển lượt
        self.turn = new_turn
        self.update_turn_label()
        self.update_timer_labels()

    def update_turn_label(self):
        self.L = LANG[AppState.language]

        # Cập nhật thông báo lượt đi theo giá trị self.turn
        # chọn chuỗi phù hợp
        if self.turn == 1:
            text = self.L["turn_black"]    # ví dụ: "Lượt đi của Đen" hoặc "Black's Turn"
        else:
            text = self.L["turn_white"]    # ví dụ: "Lượt đi của Trắng" hoặc "White's Turn"

        # apply lên label
        self.turn_label.config(text=text)

    def update_score_label(self):
    # reload dict ngôn ngữ mới
        self.L = LANG[AppState.language]

    # tính điểm
        b, w = self.calculate_score()

    # format từ LANG
        left  = self.L["score_black"].format(b)   # “Điểm Đen: {b}” hay “Black Score: {b}”
        right = self.L["score_white"].format(w)   # “Điểm Trắng: {w}” hay “White Score: {w}”
        self.score_label.config(text=f"{left}   {right}")




    def on_resize(self, event):
        self.canvas.delete("all")
        self.width = event.width
        self.height = event.height
        self.cell_size = min(self.width, self.height) / (BOARD_SIZE + 1)
        self.stone_radius = self.cell_size * STONE_RADIUS_RATIO

        self.x_offset = (self.width - self.cell_size * (BOARD_SIZE - 1)) / 2
        self.y_offset = (self.height - self.cell_size * (BOARD_SIZE - 1)) / 2

        self.draw_grid()
        self.redraw_stones()

    def draw_grid(self):
        for i in range(BOARD_SIZE):
            x = self.x_offset + i * self.cell_size
            self.canvas.create_line(x, self.y_offset, x, self.y_offset + (BOARD_SIZE - 1) * self.cell_size)
        for j in range(BOARD_SIZE):
            y = self.y_offset + j * self.cell_size
            self.canvas.create_line(self.x_offset, y, self.x_offset + (BOARD_SIZE - 1) * self.cell_size, y)

    def redraw_stones(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != 0:
                    self.draw_stone(r, c, self.board[r][c])

    def draw_stone(self, row, col, color):
        global end
        end=False
        x = self.x_offset + col * self.cell_size
        y = self.y_offset + row * self.cell_size
        fill = "black" if color == 1 else "white"
        stone = self.canvas.create_oval(x - self.stone_radius, y - self.stone_radius,
                                        x + self.stone_radius, y + self.stone_radius,
                                        fill=fill, outline="black")
        self.stones[row][col] = stone

    def on_click(self, event):
        if self.turn != 1:
            return
        col = round((event.x - self.x_offset) / self.cell_size)
        row = round((event.y - self.y_offset) / self.cell_size)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.is_move_legal(row, col, self.turn):
                board_before_move = copy.deepcopy(self.board)
                self.board[row][col] = self.turn
                self.check_captures(self.board, row, col, 3 - self.turn)
                self.previous_board = board_before_move
                self.record_elapsed_and_switch(3 - self.turn)
                self.canvas.delete("all")
                self.canvas.delete("all")
                self.draw_grid()
                self.redraw_stones()
                self.update_score_label()
                self.root.after(100, self.ai_move)
            #else:
               # messagebox.showinfo("Lỗi", "Nước đi không hợp lệ!")
                
    def pass_turn(self):
        if self.turn != 1:
            return
        self.previous_board = copy.deepcopy(self.board)
        self.record_elapsed_and_switch(2)
        self.update_score_label()
        self.root.after(100, self.ai_move)
        self.end_check()
        global end
        end=True

    def end_check(self):
        global end
        if end==True:
            b,w=self.calculate_score()
            messagebox.showinfo(
                "Kết quả",
                "Đen thắng." if b > w else "Trắng thắng." if w > b else "Hòa."
                )
            self.restart_game()

    def restart_game(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.previous_board = None
        self.turn = 1
        self.score_label.config(text="Điểm Đen: 0   Điểm Trắng: 0")
        self.black_prisoners=0
        self.white_prisoners=0
        # reset thời gian
        self.black_time = 5 * 60
        self.white_time = 5 * 60
        self.black_timer_label.config(text=f"Black: {self.format_time(self.black_time)} (s)")
        self.white_timer_label.config(text=f"White: {self.format_time(self.white_time)} (s)")

        self.canvas.delete("all")
        self.draw_grid()
        self.update_clocks()

    def get_group(self, board, r, c, color, visited=None):
        if visited is None:
            visited = set()
        if (r, c) in visited:
            return visited
        visited.add((r, c))
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == color:
                self.get_group(board, nr, nc, color, visited)
        return visited

    def has_liberty(self, board, group):
        for r, c in group:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == 0:
                    return True
        return False

    def check_captures(self, board, r, c, opponent):
        checked = set()
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                continue
            if board[nr][nc] != opponent or (nr, nc) in checked:
                continue

            group = self.get_group(board, nr, nc, opponent)
            checked |= group
            if not self.has_liberty(board, group):
                for gr, gc in group:
                    # Nếu đang xóa trên bàn thật, cập nhật prisoners và canvas
                    if board is self.board:
                        if opponent == 1:
                            # đang xóa quân Đen → Trắng vừa bắt
                            self.white_prisoners += 1
                        else:
                            # đang xóa quân Trắng → Đen vừa bắt
                            self.black_prisoners += 1

                        # xóa stone trên canvas
                        if self.stones[gr][gc]:
                            self.canvas.delete(self.stones[gr][gc])
                            self.stones[gr][gc] = None

                    # xóa khỏi board
                    board[gr][gc] = 0

     #--- Scoring (Japanese) ---
        #--- Scoring (simple: stones + prisoners) ---
    def calculate_score(self):
        black_score = self.black_prisoners
        white_score = self.white_prisoners
        # cộng thêm số quân còn trên bàn
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 1:
                    black_score += 1
                elif self.board[r][c] == 2:
                    white_score += 1
        return black_score, white_score


    def show_score(self):
        b,w=self.calculate_score()
        self.score_label.config(text=f"Điểm Đen: {b}   Điểm Trắng: {w}")
        messagebox.showinfo("Kết quả tính điểm", f"Điểm Đen: {b}\nĐiểm Trắng: {w}")


    def simulate_move_state(self, board, row, col, color):
        new_board = copy.deepcopy(board)
        new_board[row][col] = color
        opponent = 3 - color
        checked = set()
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and new_board[r][c] == opponent:
                group = self.get_group(new_board, r, c, opponent)
                if not self.has_liberty(new_board, group):
                    for gr, gc in group:
                        new_board[gr][gc] = 0
        return new_board

    def is_move_legal(self, row, col, color):
        if self.board[row][col] != 0:
            return False
        temp_board = self.simulate_move_state(self.board, row, col, color)
        group = self.get_group(temp_board, row, col, color)
        if not self.has_liberty(temp_board, group):
            return False
        if self.previous_board and temp_board == self.previous_board:
            return False
        return True

    def valid_moves_sim(self, board, color):
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == 0:
                    temp = self.simulate_move_state(board, r, c, color)
                    group = self.get_group(temp, r, c, color)
                    if self.has_liberty(temp, group):
                        if self.previous_board is None or temp != self.previous_board:
                            moves.append((r, c))
        return moves

    def iterative_deepening(self, time_limit, color):
        bot=ai.GoAI()
        start = time.time()
        best = None
        depth = 1
        while time.time() - start < time_limit and depth <= MAX_DEPTH:
            score, move = bot.minimax(self.board, depth, -math.inf, math.inf, (color == 2))
            if move:
                best = move
            depth += 1
        return best

    def ai_move(self):
        # chỉ khởi luồng AI khi tới lượt Trắng
        if self.turn != 2:
            return
        # spawn một thread để tính toán AI, không block mainloop
        threading.Thread(target=self._compute_and_play_ai, daemon=True).start()

    def _compute_and_play_ai(self):
        # tính nước đi (có thể mất TIME_LIMIT giây, UI vẫn update clocks)
        if all(all(cell == 0 for cell in row) for row in self.board):
            move = (BOARD_SIZE // 2, BOARD_SIZE // 2)
        else:
            move = self.iterative_deepening(TIME_LIMIT, 2)
        # khi xong, đưa kết quả về luồng chính
        self.root.after(0, lambda: self._finish_ai_move(move))

    def _finish_ai_move(self, move):
        # nếu AI không còn nước đi
        global end
        if not move:
            self.end_check
            self.record_elapsed_and_switch(1)
            end=True
            messagebox.showinfo("Kết thúc", "Máy không còn nước đi!")
            return

        row, col = move
        board_before = copy.deepcopy(self.board)
        self.board[row][col] = 2
        self.check_captures(self.board, row, col, 1)
        self.previous_board = board_before

        # chuyển lượt về Đen và update labels / reset last_time
        self.record_elapsed_and_switch(1)

        # vẽ lại
        self.canvas.delete("all")
        self.draw_grid()
        self.redraw_stones()
        self.update_score_label()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")
    game = GoGame(root,language="vi")
    root.mainloop()