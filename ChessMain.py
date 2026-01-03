import pygame as p
import sys
from multiprocessing import Process, Queue
import ChessEngine, ChessAI
import time
# ================== CHESS CLOCK ==================
class ChessClock:
    def __init__(self, time_per_player):
        self.white_time = time_per_player  # Thời gian tính bằng giây
        self.black_time = time_per_player
        self.last_update = time.time()
        self.is_running = False
        self.current_player = 'white'  # 'white' hoặc 'black'
    
    def start(self, player):
        """Bắt đầu đồng hồ cho người chơi"""
        if not self.is_running:
            self.current_player = player
            self.last_update = time.time()
            self.is_running = True
    
    def stop(self):
        """Dừng đồng hồ và cập nhật thời gian"""
        if self.is_running:
            elapsed = time.time() - self.last_update
            if self.current_player == 'white':
                self.white_time = max(0, self.white_time - elapsed)
            else:
                self.black_time = max(0, self.black_time - elapsed)
            self.is_running = False
    
    def switch_player(self, new_player):
        """Chuyển sang người chơi khác"""
        if self.is_running:
            self.stop()
        self.start(new_player)
    
    def get_time(self, player):
        """Lấy thời gian còn lại của người chơi"""
        if self.is_running and self.current_player == player:
            current_time = time.time()
            elapsed = current_time - self.last_update
            if player == 'white':
                return max(0, self.white_time - elapsed)
            else:
                return max(0, self.black_time - elapsed)
        else:
            return self.white_time if player == 'white' else self.black_time
    def check_timeout(self):
        """Kiểm tra hết giờ"""
        if self.white_time <= 0:
            return 'black'
        if self.black_time <= 0:
            return 'white'
        return None
    
    def format_time(self, seconds):
        """Định dạng thời gian MM:SS"""
        if seconds <= 0:
            return "00:00"
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
# ================== END GAME DIALOG ==================
class EndGameDialog:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.visible = False
        self.result = ""  # "white_win", "black_win", "stalemate"
        self.reason = ""  # Lý do: "checkmate", "timeout", "resign"
        
    def show(self, result, reason=""):
        """Hiển thị hộp thoại kết thúc game"""
        self.visible = True
        self.result = result
        self.reason = reason
        
    def hide(self):
        """Ẩn hộp thoại"""
        self.visible = False
        
    def draw(self, screen):
        """Vẽ hộp thoại"""
        if not self.visible:
            return
            
        # Màn hình mờ nền
        overlay = p.Surface((self.width, self.height), p.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
        screen.blit(overlay, (0, 0))
        
        # Hộp thoại chính
        dialog_width = 400
        dialog_height = 300
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2
        
        # Nền hộp thoại
        p.draw.rect(screen, p.Color(30, 30, 40), 
                    (dialog_x, dialog_y, dialog_width, dialog_height),
                    border_radius=15)
        p.draw.rect(screen, p.Color(70, 70, 90), 
                    (dialog_x, dialog_y, dialog_width, dialog_height),
                    width=3, border_radius=15)
        
        # Tiêu đề
        title_font = p.font.SysFont("Segoe UI", 32, True)
        reason_font = p.font.SysFont("Segoe UI", 20)
        button_font = p.font.SysFont("Segoe UI", 22, True)
        
        # Xác định nội dung hiển thị
        if self.result == "white_win":
            title = "TRẮNG THẮNG!"
            color = p.Color(220, 220, 255)
        elif self.result == "black_win":
            title = "ĐEN THẮNG!"
            color = p.Color(220, 220, 255)
        else:  # stalemate
            title = "HÒA!"
            color = p.Color(180, 180, 180)
        
        # Lý do
        reason_text = ""
        if self.reason == "checkmate":
            reason_text = "Chiếu hết!"
        elif self.reason == "timeout":
            reason_text = "Đối thủ hết giờ!"
        elif self.reason == "stalemate":
            reason_text = "Hết nước đi hợp lệ!"
        elif self.reason == "resign":
            reason_text = "Đối thủ đầu hàng!"
        
        # Vẽ tiêu đề
        title_surface = title_font.render(title, True, color)
        screen.blit(title_surface, 
                   title_surface.get_rect(center=(self.width//2, dialog_y + 60)))
        
        # Vẽ lý do
        if reason_text:
            reason_surface = reason_font.render(reason_text, True, p.Color(200, 200, 220))
            screen.blit(reason_surface, 
                       reason_surface.get_rect(center=(self.width//2, dialog_y + 110)))
        
        # Nút chơi lại
        replay_btn = p.Rect(self.width//2 - 180, dialog_y + 180, 170, 50)
        p.draw.rect(screen, p.Color(70, 150, 70), replay_btn, border_radius=10)
        p.draw.rect(screen, p.Color(100, 200, 100), replay_btn, width=3, border_radius=10)
        replay_text = button_font.render("CHƠI LẠI", True, p.Color("white"))
        screen.blit(replay_text, 
                   replay_text.get_rect(center=replay_btn.center))
        
        # Nút về menu
        menu_btn = p.Rect(self.width//2 + 10, dialog_y + 180, 170, 50)
        p.draw.rect(screen, p.Color(150, 70, 70), menu_btn, border_radius=10)
        p.draw.rect(screen, p.Color(200, 100, 100), menu_btn, width=3, border_radius=10)
        menu_text = button_font.render("VỀ MENU", True, p.Color("white"))
        screen.blit(menu_text, 
                   menu_text.get_rect(center=menu_btn.center))
        
        return replay_btn, menu_btn
# ================== SOUND ==================
def init_sound():
    """Khởi tạo âm thanh"""
    try:
        p.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        sounds = {
            'move': p.mixer.Sound('sounds/move.wav'),
            'capture': p.mixer.Sound('sounds/capture.wav'),
            'check': p.mixer.Sound('sounds/check.wav'),
            'castle': p.mixer.Sound('sounds/castle.wav'),
            'promote': p.mixer.Sound('sounds/promote.wav')
        }
        return sounds
    except:
        print("")
        return None   
# ================== CONFIG ==================
BOARD_SIZE = 512
LOG_WIDTH = 280
WIDTH = BOARD_SIZE + LOG_WIDTH
HEIGHT = BOARD_SIZE
DIM = 8
SQ = BOARD_SIZE // DIM
FPS = 15
IMAGES = {}

LIGHT = p.Color(210, 230, 255)
DARK = p.Color(70, 130, 180)

# ================== LOAD IMAGES ==================
def loadImages():
    pieces = ['wp','wR','wN','wB','wQ','wK',
              'bp','bR','bN','bB','bQ','bK']
    for pce in pieces:
        IMAGES[pce] = p.transform.scale(
            p.image.load("images/" + pce + ".png"), (SQ, SQ)
        )

# ================== BUTTON ==================
def drawButton(sc, rect, text, font):
    p.draw.rect(sc, p.Color(235,235,235), rect, border_radius=6)
    t = font.render(text, True, p.Color("black"))
    sc.blit(t, t.get_rect(center=rect.center))

# ================== MENU ==================
def mainMenu():
    p.init()
    sc = p.display.set_mode((900,500))
    p.display.set_caption("CHESS BATTLE")
    clock = p.time.Clock()

    title = p.font.SysFont("Segoe UI",42,True)
    sub = p.font.SysFont("Segoe UI",18)
    btnf = p.font.SysFont("Segoe UI",22,True)

    while True:
        sc.fill((20,50,80))

        sc.blit(title.render("CHESS BATTLE",True,p.Color("white")),(300,80))
        sc.blit(
            sub.render(
                "Trường Đại Học Đồng Tháp / Khoa Sư Phạm Toán – Tin",
                True, p.Color(200,220,240)
            ),
            (230,140)
        )

        btn_pvp = p.Rect(350,240,200,55)
        btn_ai  = p.Rect(350,320,200,55)

        drawButton(sc, btn_pvp, "Chơi với người", btnf)
        drawButton(sc, btn_ai, "Chơi với máy", btnf)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit(); sys.exit()
            if e.type == p.MOUSEBUTTONDOWN:
                if btn_pvp.collidepoint(e.pos):
                    main(False); return
                if btn_ai.collidepoint(e.pos):
                    main(True); return

        p.display.flip()
        clock.tick(60)