import socket
import threading
import sys
import random


#############################################
#              AVAILABLE COMMANDS           # 
# REGISTER <name>                           #
# PLAYERLIST                                #
# INVITE <name>                             #
# YES / NO                                  #           
# PLACE <p>                                 #
# EXIT                                      #
# HELP                                      #
# ###########################################



# Recebe no porto SERVER PORT os comandos "IAM <nome>", "HELLO",
#    "HELLOTO <nome>" ou "KILLSERVER"
# "IAM <nome>" - regista um cliente como <nome>
# "HELLO" - responde HELLO <nome> se o cliente estiver registado
# "HELLOTO <nome>" - envia HELLO para o cliente <nome>
# "KILLSERVER" - mata o servidor

#constants definition
NULL = ''
#sockets communication parameters
SERVER_PORT = 12100
MSG_SIZE = 1024
NUMBER_OF_POSITIONS = 3

#message info
COMMAND = 0
ARGUMENT = 1

SOCKET  = 0
STATUS  = 1
INVITED = 2
INGAME  = 3
SYMBOL  = 4
TURN    = 5


#return codes
OK          = 'OK: '
NOT_OK      = 'ERROR: '

#return sub-codes
REG_OK      = 'client successfully registered'
REG_UPDATED = 'client registration updated'             # NAO USADA
REG_NOT_OK  = 'client unsuccessfully registered'        # NAO USADA
INV_CLIENT  = 'client is not registered' # invalid client
INV_SESSION = 'client has no user_infos session'  #no user_infos session for the client"
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
NOT_GAME    = 'You are not in a game!'
BAD_PLAY    = 'Please PLACE in 1-9'
WRONG_TURN  = 'It\'s not your turn!'
YOUR_TURN   = 'It\'s your turn to play!'
BAD_PLACE   = 'That position is already filled!'
WIN         = 'You win!'
LOSE        = 'You lose!'
NOT_REGISTED = 'You aren\'t registered'
YOURSELF    = 'You can\'t invite yourself!'
USE_ARG     = 'Use the format: COMMAND ARGUMENT'
MUST_INT    = 'Argument must be an integer'
#GAME        = 'game has started'

#generic functions

#procura o endereco dado nos existentes
def find_addr (addr): # pede addr
    for key, val in list(user_infos.items()):
        if val[SOCKET] == addr:
            return key
    return NULL

#procura o nome dado nos registados
def find_name(name): # pede name
    for key, val in list(user_infos.items()):
        if key == name:
            return user_infos[name][SOCKET]
    return NULL

#funcao que efetua o registo do cliente descrito nos parametros
def register_client(msg_request, client_socket):
    name = msg_request[ARGUMENT]
    msg_reply = NOT_OK + NOTHING + "\n"
    client_name = find_addr(client_socket)

    if (client_name != NULL):                 # cliente ja tem sessao
        msg_reply = NOT_OK + HAS_SESSION + client_name + "\n"
    elif name in user_infos:                    # nome ja existe noutro cliente
        msg_reply = NOT_OK + REG_USED + "\n"
    else:
        user_infos[name] = [client_socket, FREE, NULL, [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']], 0, 0]
        msg_reply = OK + REG_OK + "\n"

    return msg_reply


def reply_hello(client_socket):
    msg_reply = NOT_OK + INV_CLIENT + "\n"
    dst_name = find_addr(client_socket)

    if dst_name != NULL:
        msg_reply = 'HELLO' + ' ' + dst_name + "\n"

    return msg_reply


def forward_hello(msg_request, client_socket):
    dst_name = msg_request[ARGUMENT]
    dst_addr = find_name(dst_name)
    msg_reply = NOT_OK + INV_SESSION + "\n"
    src_name =  find_addr(client_socket)

    if src_name == NULL:
        msg_reply = NOT_OK + INV_SESSION
    elif dst_addr == NULL:
        msg_reply = NO_USER + "\n"
    else:
        msg_reply = OK + ACK + "\n"
        server_reply = 'HELLO'   + ' ' + dst_name + ' from ' + src_name + "\n"
        server_reply = server_reply.encode()
        dst_addr.send(server_reply)

    return msg_reply

#funcao que lista os estados de todos os utilzadores
def show_status(client_socket):
    msg_reply = OK + '\n'
    for key, val in list(user_infos.items()): #fazer funcao
        if user_infos[key][STATUS] == FREE:
            msg_reply += key + ': free\n'
    for key, val in list(user_infos.items()): #fazer funcao
        if user_infos[key][STATUS] == BUSY:
            msg_reply += key + ': busy\n'
    for key, val in list(user_infos.items()): #fazer funcao
        if user_infos[key][STATUS] == PLAYING:
            msg_reply += key + ': playing\n'
    return msg_reply


#funcao que trata dos convites para jogos
def invite(dst_name, client_socket, src_name): # pode convidar se a si proprio lol
    """try:
        dst_name = msg_request[ARGUMENT]
    except IndexError:
        msg_reply = NOT_OK + NO_USER
    
    else:
    """   
    invited_socket = find_name(dst_name)
    if src_name == NULL:                  # se quem está a convidar nao esta registado
        msg_reply = NOT_OK + INV_CLIENT + '\n'

    elif dst_name == src_name:
        msg_reply = NOT_OK + YOURSELF + '\n'
    
    elif invited_socket == NULL:              # se o convidado nao existe
        msg_reply = NOT_OK + NO_USER + '\n'

    else:
        if user_infos[dst_name][STATUS] == FREE:
            user_infos[dst_name][STATUS] = BUSY
            user_infos[dst_name][INVITED] = src_name
            user_infos[src_name][STATUS] = BUSY
            server_reply = " You have been invited to a game by: " + src_name + ". (Y/N)"
            fast_send(server_reply, invited_socket)
            msg_reply = OK + ACK + '\n'
        else:
            msg_reply = NOT_OK + BUSY + '\n'

    return msg_reply


def update_user_infos(accepted, client_socket, src_name): # fazer jogo um objeto separado, para dar para jogar varios
    dst_addr = find_name(user_infos[src_name][INVITED])
    dst_name = find_addr(dst_addr)         

    if accepted == "Y":         #se o convite foi aceite passa ao estado PLAYING
        first = random.randint(0, 1)
        print(first)
        user_infos[src_name][STATUS] = PLAYING 
        user_infos[src_name][INGAME] = user_infos[dst_name][INGAME] # quem aceita fica com o INGAME de quem convidou
        user_infos[src_name][SYMBOL] = 'x'                          # simbolo do jogo
        user_infos[src_name][TURN] = first                             # primeiro a jogar
        
        user_infos[dst_name][STATUS] = PLAYING
        user_infos[dst_name][INVITED] = src_name # tem de ser depois de comeCar pq senao ele poderia fazer INVITE P1 e logo asseguir Y
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
        user_infos[dst_name][STATUS] = FREE
        
        msg_reply = OK + DECLINE
        server_reply = OK + DECLINED

    fast_send(server_reply, dst_addr)
    return msg_reply

#trata das jogadas
def play_space(position, client_socket, client_name): #da erro se n for int
    msg_reply = NOT_OK + NOT_GAME
    if client_name == NULL:                         # se o client nao estiver registado
        msg_reply = NOT_OK + INV_SESSION + '\n'

    elif user_infos[client_name][STATUS] == PLAYING:        # se o client nao estiver num jogo
        msg_reply = NOT_OK + WRONG_TURN
        try:
            position = int(position)
        except ValueError:
            msg_reply = NOT_OK + MUST_INT
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
                    str_mapa = show_map(client_socket)
                    msg_reply = OK + ACK + '\n' + str_mapa
                    win = check_win(mapa, line, column)
                    if win:
                        winner = check_winner(client_name, win) # preciso meter mutexes pq senao pode n verificar vitoria
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

def end_game(winner, message):
    dst_name = user_infos[winner][INVITED]
    dst_addr = user_infos[dst_name][SOCKET]
    reset(winner)
    reset(dst_name)
    server_reply = message
    fast_send(server_reply, dst_addr)


def reset(name):
    user_infos[name][STATUS] = FREE
    user_infos[name][INVITED] = NULL
    user_infos[name][INGAME] = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
    user_infos[name][SYMBOL] = 0
    user_infos[name][TURN] = 0


def check_win(mapa, line, column):
    if mapa[line][0] == mapa[line][1] == mapa[line][2] != ' ':
        return mapa[line][0]

    elif mapa[0][column] == mapa[1][column] == mapa[2][column] != ' ':
        return mapa[0][column]

    elif mapa[0][0] == mapa[1][1] == mapa[2][2] != ' ' or mapa[0][2] == mapa[1][1] == mapa[2][0] != ' ':
            return mapa[1][1]


def check_winner(name, symbol):
    if user_infos[name][SYMBOL] == symbol:
        return name
    else:
        return user_infos[name][INVITED]


def change_turn(name):
    dst_addr = find_name(user_infos[name][INVITED])
    dst_name = find_addr(dst_addr)
    user_infos[name][TURN] = 0
    user_infos[dst_name][TURN] = 1
    return

def get_map(client_socket):
    name = find_addr(client_socket)
    mapa = user_infos[name][INGAME]
    return mapa


def show_map(client_socket):
    mapa = get_map(client_socket)

    msg_reply = (str(mapa[0][0]) + "|" + str(mapa[0][1]) + "|" + str(mapa[0][2])) + '\n'
    msg_reply += (str(mapa[1][0]) + "|" + str(mapa[1][1]) + "|" + str(mapa[1][2])) + '\n'
    msg_reply += (str(mapa[2][0]) + "|" + str(mapa[2][1]) + "|" + str(mapa[2][2]))

    return msg_reply


def invalid_msg(msg_request):
  respond_msg = "INVALID MESSAGE\n"
  msg_reply = NOT_OK + msg_request[COMMAND] + ' ' + INV_MSG + "\n"
  return msg_reply


def exit_session(client_socket): # falta ver se o cliente fizer ctrl+c a meio de um jogo..
    name = find_addr(client_socket)
    if user_infos[name][STATUS] == PLAYING:             # exit durante uma partida
        end_game(name, WIN);

    try:
        del user_infos[name]
    except KeyError:
        return EXIT
    return EXIT


def fast_send(server_reply, dst_addr):
    server_reply = server_reply.encode()
    dst_addr.send(server_reply)


def server_function(client_socket):
    # meter aqui variaveis tipo nome, que devem ser locais
    client_name = NULL
    while True:
        client_msg = client_socket.recv(MSG_SIZE)
        msg_request = client_msg.decode().split()
        try:
            command = msg_request[COMMAND]
        except IndexError:
            server_msg = NOT_OK + INV_MSG + '\n'
        else:

            if command == "LIST":
                server_msg = show_status(client_socket)

            elif command == "EXIT": 
                server_msg = exit_session(client_socket)
                fast_send(server_msg, client_socket)
                break

            elif command == "Y" or command == "N": # mudou para SO com maiusculas
                server_msg = update_user_infos(command, client_socket, client_name)

            elif command in ["INVITE", "PLACE", "IAM"]: # nao gosto muito
                try:
                    arg = msg_request[ARGUMENT]
                except IndexError:
                    server_msg = NOT_OK + USE_ARG

                else:
                    if command == "INVITE":
                        server_msg = invite(arg, client_socket, client_name)

                    elif command == "PLACE":
                        server_msg = play_space(arg, client_socket, client_name)

                    elif command == "IAM":
                        server_msg = register_client(msg_request, client_socket)
                        client_name = find_addr(client_socket)

            else:
                server_msg = invalid_msg(msg_request)

        fast_send(server_msg, client_socket)
    client_socket.close()
    sys.exit()


#main code
threads = []
user_infos = {} #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)

# programa inicial, nao e thread
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # para depois poder matar com ctrl+c
server_sock.bind(('', SERVER_PORT))
server_sock.listen(5)


while True:
    client_sock, client_addr = server_sock.accept()
    cliente = threading.Thread(target=server_function, args = (client_sock,))
    threads.append(cliente)
    cliente.start()



# jogos guardados numa lista, jogo guarda os players e os seus simbolos, 
# podes fazer quit para voltar para o cmd, SHOWGAMES e ENTER NUM pa voltar
