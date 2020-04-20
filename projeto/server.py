import socket
import threading


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

#message info
COMMAND = 0
ARGUMENT = 1

#return codes
OK          = 'OK: '
NOT_OK      = 'ERROR: '

#return sub-codes
REG_OK      = 'client successfully registered'
REG_UPDATED = 'client registration updated'
REG_NOT_OK  = 'client unsuccessfully registered'
INV_CLIENT  = 'client is not registered' # invalid client
INV_SESSION = 'client has no status session'  #no status session for the client"
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

#generic functions

def find_addr (addr): # pede addr
    for key, val in list(users.items()):
        if val == addr:
            return key
    return NULL

def find_name(name): # pede name
    for key, val in list(users.items()):
        if key == name:
            return users[name]
    return NULL


def register_client(msg_request, client_socket):
    name = msg_request[ARGUMENT]
    msg_reply = NOT_OK + NOTHING + "\n"
    client_name = find_addr(client_socket)

    if (client_name != NULL):
        msg_reply = NOT_OK + HAS_SESSION + client_name + "\n"
    elif name in users: 
        msg_reply = NOT_OK + REG_USED + "\n"
    else:
        users[name] = client_socket
        status[name] = FREE
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


def show_status(client_socket):
    msg_reply = OK + '\n'
    for key, val in list(status.items()): #fazer funcao
        if status[key] == FREE:
            msg_reply += key + ': free\n'
    for key, val in list(status.items()): #fazer funcao
        if status[key] == BUSY:
            msg_reply += key + ': busy\n'
    return msg_reply


def invite(msg_request, client_socket):
    dst_name = msg_request[ARGUMENT]
    status[dst_name] = BUSY
    invited_socket = find_name(dst_name)
    src_name = find_addr(client_socket)
    status[src_name] = BUSY
    server_reply = " You have been invited to a game by: " + src_name + ". (Y/n)"
    server_reply = server_reply.encode() #fazer uma funcao auxiliar que faz estas 2 linhas depois
    invited_socket.send(server_reply)
    msg_reply = OK + ACK + '\n'

    return msg_reply


def update_status(accepted, client_socket):
    dst_name = find_addr(client_socket)
    
    status[dst_name] = PLAYING # mudar todos if else para este formato?
    msg_reply = OK + ACCEPT
    if accepted == "N":
        status[dst_name] = FREE
        msg_reply = OK + DECLINE

    return msg_reply

def invalid_msg(msg_request):
  respond_msg = "INVALID MESSAGE\n"
  msg_reply = NOT_OK + msg_request[COMMAND] + ' ' + INV_MSG + "\n"
  return msg_reply


def exit_session(client_socket):
    name = find_addr(client_socket)
    del users[name]
    del status[name]
    return EXIT.encode()


def server_function(client_socket):
    while True:
        client_msg = client_socket.recv(MSG_SIZE)
        print(client_msg.decode())
        msg_request = client_msg.decode().split()
        command = msg_request[COMMAND]
        if(command == "IAM"): # se command 2 for NULL breaka
            server_msg = register_client(msg_request, client_socket)
        elif(command == "HELLO"):
            server_msg = reply_hello(client_socket)
        elif(command == "HELLOTO"):
            server_msg = forward_hello(msg_request, client_socket)
        elif(command == "LIST"):
            server_msg = show_status(client_socket)
        elif(command == "INVITE"):
            server_msg = invite(msg_request, client_socket)
        elif(command.upper() == "Y" or command.upper() == "N"):
            client_name = find_addr(client_socket)
            if status[client_name] == BUSY:
                server_msg = update_status(command.upper(), client_socket)
        elif(command == "EXIT"):
            server_msg = exit_session(client_socket)
            server_msg = msg_reply.encode()
            client_socket.send(server_msg)
            break
        else:
            server_msg = invalid_msg(msg_request)
        #server_sock.sendto(server_msg, (client_addr, SERVER_PORT))
        server_msg = server_msg.encode()
        client_socket.send(server_msg)
    client_socket.close()


#main code
threads = []
users = {} #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)
status = {}
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
