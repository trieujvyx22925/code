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

# ================== MAIN GAME ==================
def main(vs_ai):
    p.init()
    sc = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    loadImages()

    chess_clock = ChessClock(time_per_player=600)
    end_dialog = EndGameDialog(WIDTH, HEIGHT)

    sounds = init_sound()

    gs = ChessEngine.GameState()
    valid_moves = gs.getValidMoves()
    
    chess_clock.start('white')

    sq_selected = ()
    clicks = []

    show_hint = False
    hint_move = None

    ai_thinking = False
    ai_proc = None

    game_over = False
    winner = None

    font = p.font.SysFont("Segoe UI",14)
    btnf = p.font.SysFont("Segoe UI",16,True)

    while True:
         # Kiểm tra điều kiện kết thúc game
        if not game_over:
            # Kiểm tra hết giờ
            timeout_winner = chess_clock.check_timeout()
            if timeout_winner:
                game_over = True
                if timeout_winner == 'white':
                    end_dialog.show("white_win", "timeout")
                else:
                    end_dialog.show("black_win", "timeout")
                if sounds:
                    sounds['game_end'].play()
                chess_clock.game_over = True
            
            # Kiểm tra chiếu hết
            if gs.checkmate:
                game_over = True
                if gs.white_to_move:  # Lượt trắng đi nhưng bị chiếu hết => đen thắng
                    end_dialog.show("black_win", "checkmate")
                else:  # Lượt đen đi nhưng bị chiếu hết => trắng thắng
                    end_dialog.show("white_win", "checkmate")
                if sounds:
                    sounds['game_end'].play()
                chess_clock.game_over = True
            
            # Kiểm tra hòa
            if gs.stalemate:
                game_over = True
                end_dialog.show("stalemate", "stalemate")
                if sounds:
                    sounds['game_end'].play()
                chess_clock.game_over = True
        # Cập nhật đồng hồ
        if not game_over:
            current_player = 'white' if gs.white_to_move else 'black'
            if not chess_clock.is_running and not (gs.checkmate or gs.stalemate):
                chess_clock.start(current_player)
            elif chess_clock.current_player != current_player:
                chess_clock.switch_player(current_player)
    
        # Kiểm tra hết giờ
        white_time = chess_clock.get_time('white')
        black_time = chess_clock.get_time('black')
        if white_time <= 0:
            print("Trắng hết giờ! Đen thắng!")
        # Có thể thêm logic xử lý thua do hết giờ
        if black_time <= 0:
            print("Đen hết giờ! Trắng thắng!")
        # ---------- EVENTS ----------
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit(); sys.exit()

            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    mainMenu(); return
                if e.key == p.K_z and (e.mod & p.KMOD_CTRL) and not game_over:
                    if gs.move_log:
                        gs.undoMove()
                        valid_moves = gs.getValidMoves()
                        show_hint = False
                        hint_move = None
                        game_over = False
                        end_dialog.hide()
                        chess_clock.game_over = False

            if e.type == p.MOUSEBUTTONDOWN:
                mx, my = e.pos

                 # Nếu game đã kết thúc, kiểm tra nút trong hộp thoại
                if game_over and end_dialog.visible:
                    replay_btn, menu_btn = end_dialog.draw(sc)
                    if replay_btn.collidepoint(e.pos):
                        main(vs_ai)
                        return
                    if menu_btn.collidepoint(e.pos):
                        mainMenu()
                        return
                    continue
                btn_menu  = p.Rect(BOARD_SIZE+10,10,120,30)
                btn_reset = p.Rect(BOARD_SIZE+150,10,120,30)
                btn_hint  = p.Rect(BOARD_SIZE+10,50,260,30)
                btn_resign = p.Rect(BOARD_SIZE+10,90,260,30) # Nút đầu hàng
                if btn_menu.collidepoint(e.pos):
                    mainMenu(); return

                if btn_reset.collidepoint(e.pos):
                    main(vs_ai); return

                if btn_hint.collidepoint(e.pos) and not game_over:
                    if valid_moves:
                        hint_move = ChessAI.findRandomMove(valid_moves)
                        show_hint = True
                    continue
                #nút đầu hàng
                if btn_resign.collidepoint(e.pos) and not game_over:
                    game_over = True
                    if gs.white_to_move:
                        end_dialog.show("black_win", "resign")
                    else:
                        end_dialog.show("white_win", "resign")
                    if sounds:
                        sounds['game_end'].play()
                    chess_clock.game_over = True
                    continue
                col = mx // SQ
                row = my // SQ
                if col < 8 and row < 8:
                    if sq_selected == (row,col):
                        sq_selected = ()
                        clicks = []
                    else:
                        sq_selected = (row,col)
                        clicks.append(sq_selected)
                    human_turn = (gs.white_to_move and True) or \
                     (not gs.white_to_move and not vs_ai)

                    if len(clicks) == 2 and human_turn and not game_over:
                        move = ChessEngine.Move(clicks[0], clicks[1], gs.board)
                        for m in valid_moves:
                            if move == m:
                                gs.makeMove(m)
                                valid_moves = gs.getValidMoves()
                                 # Phát âm thanh
                                if sounds:
                                    if m.piece_captured != "--":
                                        sounds['capture'].play()
                                    elif m.is_castle_move:
                                        sounds['castle'].play()
                                    else:
                                        sounds['move'].play()
                
                                # Cập nhật đồng hồ
                                chess_clock.switch_player('black' if gs.white_to_move else 'white')
                                sq_selected = ()
                                clicks = []
                                show_hint = False
                                hint_move = None
                                break
                        if len(clicks) == 2:
                            clicks = [sq_selected]

        # ---------- AI ----------
        if vs_ai and not game_over:
            human_turn = (gs.white_to_move and True) or \
                         (not gs.white_to_move and not vs_ai)
            
            if not human_turn and not ai_thinking:
                ai_thinking = True
                q = Queue()
                ai_proc = Process(
                    target=ChessAI.findBestMove,
                    args=(gs, valid_moves, q)
                )
                ai_proc.start()

            if ai_thinking and not ai_proc.is_alive():
                ai_move = q.get()
                if ai_move:
                    gs.makeMove(ai_move)
                    valid_moves = gs.getValidMoves()
                ai_thinking = False
                show_hint = False
                hint_move = None

        drawAll(sc, gs, valid_moves, sq_selected,
                font, btnf, show_hint, hint_move, chess_clock, 
                game_over, end_dialog)

        clock.tick(FPS)
        p.display.flip()

# ================== DRAW ==================
def drawAll(sc, gs, moves, sq, font, btnf, show_hint, hint, chess_clock, game_over=False, end_dialog=None):
    drawBoard(sc)
    if not game_over:
        drawHighlight(sc, gs, moves, sq, show_hint, hint)
    drawPieces(sc, gs.board)
    drawCheck(sc, gs)
    drawMoveLog(sc, gs, font)
    drawButtons(sc, btnf)
    drawClock(sc, chess_clock)
    if game_over and end_dialog:
        end_dialog.draw(sc)
    

def drawBoard(sc):
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r+c)%2==0 else DARK
            p.draw.rect(sc, color, p.Rect(c*SQ, r*SQ, SQ, SQ))


def drawHighlight(sc, gs, moves, sq, show_hint, hint):
    if sq:
        r,c = sq
        s = p.Surface((SQ,SQ))
        s.set_alpha(90)
        s.fill(p.Color("blue"))
        sc.blit(s, (c*SQ, r*SQ))

        for m in moves:
            if m.start_row == r and m.start_col == c:
                center = (m.end_col*SQ+SQ//2,
                          m.end_row*SQ+SQ//2)
                if m.piece_captured != "--":
                    p.draw.circle(sc, p.Color("red"), center, 15, 3)
                else:
                    p.draw.circle(sc, p.Color("green"), center, 7)

    if show_hint and hint:
        sx = hint.start_col*SQ + SQ//2
        sy = hint.start_row*SQ + SQ//2
        ex = hint.end_col*SQ + SQ//2
        ey = hint.end_row*SQ + SQ//2

        p.draw.line(sc, p.Color("green"), (sx,sy), (ex,ey), 4)
        p.draw.circle(sc, p.Color("green"), (sx,sy), 12, 3)
        p.draw.circle(sc, p.Color("green"), (ex,ey), 10)

def drawPieces(sc, board):
    for r in range(8):
        for c in range(8):
            if board[r][c] != "--":
                sc.blit(IMAGES[board[r][c]], (c*SQ, r*SQ))

def drawCheck(sc, gs):
    if not gs.in_check:
        return
    king = "wK" if gs.white_to_move else "bK"
    for r in range(8):
        for c in range(8):
            if gs.board[r][c] == king:
                p.draw.rect(
                    sc, p.Color("red"),
                    p.Rect(c*SQ, r*SQ, SQ, SQ), 4
                )

def drawMoveLog(sc, gs, font):
    rect = p.Rect(BOARD_SIZE, 140, LOG_WIDTH, HEIGHT-150)
    p.draw.rect(sc, p.Color(20,20,20), rect)

    y = 150
    for i in range(0, len(gs.move_log), 2):
        text = f"{i//2+1}. {gs.move_log[i]}"
        if i+1 < len(gs.move_log):
            text += f"   {gs.move_log[i+1]}"
        sc.blit(font.render(text, True, p.Color("white")),
                (BOARD_SIZE+10, y))
        y += 18


def drawButtons(sc, font, game_over =False):
    # Nút Menu
    btn_menu = p.Rect(BOARD_SIZE+10, 10, 120, 30)
    p.draw.rect(sc, p.Color(70, 130, 180), btn_menu, border_radius=6)
    p.draw.rect(sc, p.Color(100, 160, 210), btn_menu, width=2, border_radius=6)
    menu_text = font.render("Menu", True, p.Color("white"))
    sc.blit(menu_text, menu_text.get_rect(center=btn_menu.center))
    
    # Nút Chơi lại
    btn_reset = p.Rect(BOARD_SIZE+150, 10, 120, 30)
    p.draw.rect(sc, p.Color(180, 70, 70), btn_reset, border_radius=6)
    p.draw.rect(sc, p.Color(210, 100, 100), btn_reset, width=2, border_radius=6)
    reset_text = font.render("Chơi lại", True, p.Color("white"))
    sc.blit(reset_text, reset_text.get_rect(center=btn_reset.center))
    
    # Nút Hint
    btn_hint = p.Rect(BOARD_SIZE+10, 50, 260, 30)
    p.draw.rect(sc, p.Color(70, 180, 70), btn_hint, border_radius=6)
    p.draw.rect(sc, p.Color(100, 210, 100), btn_hint, width=2, border_radius=6)
    hint_text = font.render("Hint (nước đi gợi ý)", True, p.Color("white"))
    sc.blit(hint_text, hint_text.get_rect(center=btn_hint.center))
    
    # Nút Đầu hàng (chỉ hiện khi game chưa kết thúc)
    if not game_over:
        btn_resign = p.Rect(BOARD_SIZE+10, 90, 260, 30)
        p.draw.rect(sc, p.Color(180, 50, 50), btn_resign, border_radius=6)
        p.draw.rect(sc, p.Color(210, 80, 80), btn_resign, width=2, border_radius=6)
        resign_text = font.render("ĐẦU HÀNG", True, p.Color("white"))
        sc.blit(resign_text, resign_text.get_rect(center=btn_resign.center))


# ================== DRAW CLOCK ==================
def drawClock(sc, chess_clock):
    """Vẽ đồng hồ cho hai bên"""
    font = p.font.SysFont("Segoe UI", 24, True)
    small_font = p.font.SysFont("Segoe UI", 16)
    
    # Đồng hồ Trắng (ở dưới)
    white_time = chess_clock.get_time('white')
    white_text = font.render(chess_clock.format_time(white_time), 
                             True, p.Color("white"))
    white_bg = p.Rect(BOARD_SIZE + 10, HEIGHT - 80, LOG_WIDTH - 20, 40)
    p.draw.rect(sc, p.Color(40, 40, 40), white_bg, border_radius=5)
    
    # Đánh dấu nếu đang chạy
    if chess_clock.is_running and chess_clock.current_player == 'white':
        p.draw.rect(sc, p.Color(0, 200, 0), white_bg, 3, border_radius=5)
    
    sc.blit(white_text, 
            white_text.get_rect(center=white_bg.center))
    sc.blit(small_font.render("TRẮNG", True, p.Color(220,220,220)),
            (BOARD_SIZE + 20, HEIGHT - 105))
    
    # Đồng hồ Đen (ở trên)
    black_time = chess_clock.get_time('black')
    black_text = font.render(chess_clock.format_time(black_time), 
                             True, p.Color("white"))
    black_bg = p.Rect(BOARD_SIZE + 10, HEIGHT - 160, LOG_WIDTH - 20, 40)
    p.draw.rect(sc, p.Color(40, 40, 40), black_bg, border_radius=5)
    
    if chess_clock.is_running and chess_clock.current_player == 'black':
        p.draw.rect(sc, p.Color(0, 200, 0), black_bg, 3, border_radius=5)
    
    sc.blit(black_text, 
            black_text.get_rect(center=black_bg.center))
    sc.blit(small_font.render("ĐEN", True, p.Color(220,220,220)),
            (BOARD_SIZE + 20, HEIGHT - 185))
# ================== RUN ==================
if __name__ == "__main__":
    mainMenu()
    