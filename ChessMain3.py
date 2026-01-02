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
    