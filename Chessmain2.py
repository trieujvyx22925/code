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
