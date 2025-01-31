import random

NULL = ''

#message info
COMMAND  = 0
ARGUMENT = 1


NUMBER_OF_POSITIONS = 3
MAX_TURNS = 9

# para o user_infos
SOCKET  = 0
STATUS  = 1
INVITED = 2
INGAME  = 3
SYMBOL  = 4
TURN    = 5
INVITES = 6       
NUM_TURN = 7

#return codes
OK          = 'OK: '
NOT_OK      = 'ERROR: '

#return sub-codes
REG_OK      = 'client successfully registered'
INV_CLIENT  = 'client is not registered' 
INV_MSG     = 'invalid message type'
REG_USED    = 'client with that name already exists'
HAS_SESSION = 'you already have a session, '
EXIT        = 'you have ended your session'
NOTHING     = 'has done nothing'
NO_USER     = 'No user with that name!'
ACK         = 'Your message has been delivered'
FREE        = 'free'
BUSY        = 'busy'
PLAYING     = 'playing'
ACCEPT      = 'you are in a game now!'
ACCEPTED    = 'you are in a game now!'
DECLINE     = 'you declined the game invite'
DECLINED    = 'the player declined your invite'
YOURSELF    = 'You can\'t invite yourself'
EXIT_INVITE = ' is not available anymore. The invitation has been canceled.'
NOT_GAME    = 'You are not in a game!'
BAD_PLAY    = 'Please PLACE in 1-9'
WRONG_TURN  = 'It\'s not your turn!'
YOUR_TURN   = 'It\'s your turn to play!'
BAD_PLACE   = 'That position is already filled!'
WIN         = 'You win!'
LOSE        = 'You lose!'
DRAW        = 'Your game ended with a draw.'
USE_ARG     = 'Use the format: COMMAND ARGUMENT'
MUST_INT    = 'Argument must be an integer'
NOT_INVITED = 'You have not been invited to a game!'

user_infos = {}

#generic functions

#procura o endereco dado nos existentes e devolve o name
def find_addr (addr): # pede addr
    for key, val in list(user_infos.items()):
        if val[SOCKET] == addr:
            return key
    return NULL

# Funcao que procura o nome dado nos registados e devolve o addr
def find_name(name): # pede name
    for key, val in list(user_infos.items()):
        if key == name:
            return user_infos[name][SOCKET]
    return NULL

# Funcao que efetua o registo do cliente
def register_client(msg_request, client_socket):
    name = msg_request[ARGUMENT]
    msg_reply = NOT_OK + NOTHING + "\n"
    client_name = find_addr(client_socket)

    if (client_name != NULL):                     # cliente ja tem sessao
        msg_reply = NOT_OK + HAS_SESSION + client_name + "\n"
    elif name in user_infos:                    # nome ja existe noutro cliente
        msg_reply = NOT_OK + REG_USED + "\n"
    else:
        user_infos[name] = [client_socket, FREE, NULL, [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']], 0, 0, 0, [0]]
        msg_reply = OK + REG_OK + "\n"

    return msg_reply

# Funcao que lista os estados de todos os utilzadores
def show_status(client_socket):
    msg_reply = OK + '\n'
    for key, val in list(user_infos.items()): 
        if user_infos[key][STATUS] == FREE:
            msg_reply += key + ': Free\n'
    for key, val in list(user_infos.items()): 
        if user_infos[key][STATUS] == BUSY:
            msg_reply += key + ': Busy\n'
    for key, val in list(user_infos.items()): 
        if user_infos[key][STATUS] == PLAYING:
            msg_reply += key + ': Playing\n'
    return msg_reply


# Funcao que trata dos convites para jogos
def invite(dst_name, client_socket, src_name):
    invited_socket = find_name(dst_name)
    if src_name == NULL:                    # se quem está a convidar nao esta registado
        msg_reply = NOT_OK + INV_CLIENT + '\n'

    elif dst_name == src_name:              # se se esta a convidar a si mesmo
        msg_reply = NOT_OK + YOURSELF + '\n'
    
    elif invited_socket == NULL:              # se o convidado nao existe
        msg_reply = NOT_OK + NO_USER + '\n'

    else:
        if user_infos[dst_name][STATUS] == FREE:
            user_infos[dst_name][STATUS] = BUSY
            user_infos[dst_name][INVITED] = src_name
            user_infos[dst_name][INVITES] = 2           # foi convidado
            user_infos[src_name][STATUS] = BUSY
            user_infos[src_name][INVITES] = 1           # convidou
            user_infos[src_name][INVITED] = dst_name
            server_reply = OK + " You have been invited to a game by: " + src_name + ". (Y/N)"
            fast_send(server_reply, invited_socket)
            msg_reply = OK + ACK + '\n'
        else:
            msg_reply = NOT_OK + BUSY + '\n'

    return msg_reply


# Funcao que aturaliza informacoes dos clientes dependendo da resposta ao INVITE
def update_user_infos(accepted, client_socket, src_name): 
    if src_name == NULL:
        msg_reply = INV_CLIENT
    elif user_infos[src_name][STATUS] == BUSY:
        dst_addr = find_name(user_infos[src_name][INVITED])
        dst_name = find_addr(dst_addr)        

        if accepted == "Y":         #se o convite foi aceite passa ao estado PLAYING
            first = random.randint(0, 1)
            user_infos[src_name][STATUS] = PLAYING 
            user_infos[src_name][INGAME] = user_infos[dst_name][INGAME] 
            user_infos[src_name][SYMBOL] = 'x'                          # simbolo do jogo
            user_infos[src_name][TURN] = first                          
            user_infos[src_name][NUM_TURN] = user_infos[dst_name][NUM_TURN]
            
            user_infos[dst_name][STATUS] = PLAYING
            user_infos[dst_name][INVITED] = src_name 
            user_infos[dst_name][SYMBOL] = 'o'  
            user_infos[dst_name][TURN] = 1 - first
            

            if first == 1:
                msg_reply = OK + ACCEPT + '\n' + YOUR_TURN
                server_reply = OK + ACCEPTED
            else:
                server_reply = OK + ACCEPT + '\n' + YOUR_TURN
                msg_reply = OK + ACCEPTED

        else:                   #se o convite foi recusado passa a FREE
            user_infos[src_name][STATUS] = FREE
            user_infos[src_name][INVITED] = NULL
            user_infos[src_name][INVITES] = 0
            user_infos[dst_name][STATUS] = FREE
            user_infos[dst_name][INVITED] = NULL
            user_infos[dst_name][INVITES] = 0
            
            msg_reply = OK + DECLINE
            server_reply = OK + DECLINED
        fast_send(server_reply, dst_addr)

    else:
        msg_reply = NOT_INVITED
        return msg_reply

    return msg_reply

#trata das jogadas
def play_space(position, client_socket, client_name):
    msg_reply = NOT_OK + NOT_GAME
    if client_name == NULL:                         # se o client nao estiver registado
        msg_reply = NOT_OK + INV_CLIENT + '\n'

    elif user_infos[client_name][STATUS] == PLAYING:    # se o client nao estiver num jogo
        msg_reply = NOT_OK + WRONG_TURN
        try:
            position = int(position)                    
        except ValueError:
            msg_reply = NOT_OK + MUST_INT           # caso o input nao seja int
            return msg_reply
        turn = user_infos[client_name][TURN]
        dst_addr = find_name(user_infos[client_name][INVITED])
        dst_name = find_addr(dst_addr)
        if turn == 1:
            if (0 < position < 10): 
                position -= 1
                line = position // NUMBER_OF_POSITIONS
                column = position % NUMBER_OF_POSITIONS
                mapa = user_infos[client_name][INGAME]
                simbolo = user_infos[client_name][SYMBOL]
                if mapa[line][column] == ' ':
                    mapa[line][column] = simbolo
                    user_infos[client_name][NUM_TURN][0] = user_infos[client_name][NUM_TURN][0] + 1
                    if user_infos[client_name][NUM_TURN][0] == MAX_TURNS:
                        end_game(client_name, DRAW)
                        msg_reply = OK + DRAW
                        return msg_reply

                    str_mapa = show_map(client_socket)
                    msg_reply = OK + ACK + '\n' + str_mapa
                    win = check_win(mapa, line, column)
                    if win:
                        winner = check_winner(client_name, win) 
                        end_game(winner, LOSE)
                        msg_reply = OK + WIN
                        return msg_reply
                    change_turn(client_name)
                    server_reply = '\n' + str_mapa
                    fast_send(server_reply, dst_addr)
                else:
                    msg_reply = NOT_OK + BAD_PLACE
            else:
                msg_reply = NOT_OK + BAD_PLAY
    return msg_reply

# Funcao que termina o jogo
def end_game(winner, message):
    dst_name = user_infos[winner][INVITED]
    dst_addr = user_infos[dst_name][SOCKET]
    reset(winner)
    reset(dst_name)
    server_reply = OK + message
    fast_send(server_reply, dst_addr)

# Funcao que limpa os atributos do cliente 
def reset(name):
    user_infos[name][STATUS] = FREE
    user_infos[name][INVITED] = NULL
    user_infos[name][INGAME] = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
    user_infos[name][SYMBOL] = 0
    user_infos[name][TURN] = 0
    user_infos[name][INVITES] = 0
    user_infos[name][NUM_TURN] = [0]

# Funcao que verifica se as posicoes jogadas correspondem a vitoria
def check_win(mapa, line, column):
    if mapa[line][0] == mapa[line][1] == mapa[line][2] != ' ':
        return mapa[line][0]

    elif mapa[0][column] == mapa[1][column] == mapa[2][column] != ' ':
        return mapa[0][column]

    elif mapa[0][0] == mapa[1][1] == mapa[2][2] != ' ' or mapa[0][2] == mapa[1][1] == mapa[2][0] != ' ':
            return mapa[1][1]

# Funcao que retorna o nome do vencedor da partida
def check_winner(name, symbol):
    if user_infos[name][SYMBOL] == symbol:
        return name
    else:
        return user_infos[name][INVITED]

# Funcao que troca a vez de jogar dos jogadores
def change_turn(name):
    dst_addr = find_name(user_infos[name][INVITED])
    dst_name = find_addr(dst_addr)
    user_infos[name][TURN] = 0
    user_infos[dst_name][TURN] = 1
    return

# Funcao que retorna o mapa de jogo do client dado como arg
def get_map(client_socket):
    name = find_addr(client_socket)
    mapa = user_infos[name][INGAME]
    return mapa


# Funcao que imprime o mapa do jogo
def show_map(client_socket):
    mapa = get_map(client_socket)

    msg_reply = (str(mapa[0][0]) + "|" + str(mapa[0][1]) + "|" + str(mapa[0][2])) + '\n'
    msg_reply += (str(mapa[1][0]) + "|" + str(mapa[1][1]) + "|" + str(mapa[1][2])) + '\n'
    msg_reply += (str(mapa[2][0]) + "|" + str(mapa[2][1]) + "|" + str(mapa[2][2]))

    return msg_reply


# Funcao que envia a mensagem invalida de aviso ao client
def invalid_msg(msg_request):
  respond_msg = "INVALID MESSAGE\n"
  msg_reply = NOT_OK + msg_request[COMMAND] + ' ' + INV_MSG + "\n"
  return msg_reply


 # Funcao auxiliar para o caso em que quem convidou outro player faz EXIT
def update_inviting(client_name):              
    dst_name = user_infos[client_name][INVITED]
    dst_addr = find_name(dst_name)

    user_infos[dst_name][STATUS] = FREE
    user_infos[dst_name][INVITED] = NULL
    user_infos[dst_name][INVITES] = 0
    user_infos[dst_name][NUM_TURN] = [0]
    server_reply = client_name + EXIT_INVITE
    fast_send(server_reply, dst_addr)


# Funcao que trata de diferentes casos onde pode ser usado o comando EXIT
def exit_session(client_socket):
    name = find_addr(client_socket)

    if name == NULL:
        return EXIT

    elif user_infos[name][STATUS] == PLAYING:              # EXIT durante uma partida
        end_game(name, WIN)

    elif (user_infos[name][STATUS] == BUSY) and (user_infos[name][INVITES] == 2):       # EXIT ao ser convidado
        update_user_infos("N", client_socket, name)

    elif (user_infos[name][STATUS] == BUSY) and (user_infos[name][INVITES] == 1):       # EXIT ao convidar
        update_inviting(name)

    try:
        del user_infos[name]
    except KeyError:
        return EXIT

    return EXIT


def fast_send(server_reply, dst_addr):
    server_reply = server_reply.encode()
    dst_addr.send(server_reply)