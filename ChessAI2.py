


def findBestMove(game_state, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if game_state.white_to_move else -1)
    return_queue.put(next_move)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    # move ordering - implement later //TODO
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undoMove()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def scoreBoard(game_state):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif game_state.stalemate:
        return STALEMATE #Hòa
    #Chưa hiểu tạo score làm gì
    score = 0 #Nếu không có tình huống checkmate hay stalemate thì khởi tạo score
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score

    return score


def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)
