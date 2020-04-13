import socket


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
TYPE = 0
USER_ID = 1

#return codes
OK          = 'OK: '
NOT_OK      = 'ERROR: '

#return sub-codes
REG_OK      = 'client successfully registered'
REG_UPDATED = 'client registration updated'
REG_NOT_OK  = 'client unsuccessfully registered'
INV_CLIENT  = 'client is not registered' # invalid client
INV_SESSION = 'client has no active session'  #no active session for the client"
INV_MSG     = 'invalid message type'

#generic functions

def find_client (addr, active_users):
    for key, val in list(active_users.items()):
        if val == addr:
            return key
    return NULL

#message handling functions
def register_client(msg_request, addr, active_users):
    name = msg_request[USER_ID]
    msg_reply = OK + REG_OK + "\n"
    # delete existing users
    if name in active_users:
        active_users.pop(name)
        msg_reply = OK + REG_UPDATED + "\n"
    dst_name = find_client(addr, active_users)
    if (dst_name != NULL):
        active_users.pop(dst_name)
        msg_reply = OK + REG_UPDATED + "\n"
    # register the user
    active_users[name] = addr
    server_msg = msg_reply.encode()
    return(server_msg)


def reply_hello(addr, active_users):
    msg_reply = NOT_OK + INV_CLIENT + "\n"
    dst_name = find_client(addr, active_users)
    if (dst_name != NULL):
        msg_reply = 'HELLO' + ' ' + dst_name + "\n"
    server_msg = msg_reply.encode()
    return(server_msg)

def forward_hello(msg_request, addr, active_users):
    dst_name = msg_request[USER_ID]
    src_name =  find_client(addr, active_users)
    msg_reply = NOT_OK + INV_SESSION + "\n"
    for key, val in list(active_users.items()):
        if key == dst_name:
            msg_reply = 'HELLO'   + ' ' + dst_name + ' from ' + src_name +"\n"
            addr = active_users[dst_name]
            break
    server_msg = msg_reply.encode()
    return(server_msg, addr)

def invalid_msg(msg_request):
  respond_msg = "INVALID MESSAGE\n"
  msg_reply = NOT_OK + msg_request[TYPE] + ' ' + INV_MSG + "\n"
  server_msg = msg_reply.encode()
  return server_msg

#main code
#threads = []

#connections = {}  guardar infos das ligacoes antes de fazerem register: formato -> 

active_users = {} #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)

# programa inicial, nao e thread
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # para depois poder matar com ctrl+c

server_sock.bind(('', SERVER_PORT))


server_sock.listen(5)





server_sock, client_addr = server_sock.accept() 




    #while True:
        #server_sock, client_addr = server_sock.accept()
        # a parte de cima guardamos num buffer para se outra thread abrir depois e registar primeiro?
        #cliente = threading.Thread(target=server)
        #threads.append(cliente)
        #cliente.start()
    while True:
        (client_msg, client_addr) = server_sock.recvfrom(MSG_SIZE)
        print("Passou")
        msg_request = client_msg.decode().split()
        print(msg_request)
        request_type = msg_request[TYPE]
        if(request_type == "IAM"):
            server_msg = register_client(msg_request, client_addr, active_users)
        elif(request_type == "HELLO"):
            server_msg = reply_hello(client_addr, active_users)
        elif(request_type == "HELLOTO"):
            (server_msg, client_addr) = forward_hello(msg_request, client_addr, active_users)
        elif(request_type == "KILLSERVER"):
            server_msg = "KILL".encode()
            server_sock.send(server_msg)
            break
        else:
            server_msg = invalid_msg(msg_request)
        #server_sock.sendto(server_msg, (client_addr, SERVER_PORT))
        server_sock.send(server_msg)
    server_sock.close()


#def server():
"""
        while True:
        (client_msg, client_addr) = server_sock.recvfrom(MSG_SIZE)
        print("Passou")
        msg_request = client_msg.decode().split()
        print(msg_request)
        request_type = msg_request[TYPE]
        if(request_type == "IAM"):
            server_msg = register_client(msg_request, client_addr, active_users)
        elif(request_type == "HELLO"):
            server_msg = reply_hello(client_addr, active_users)
        elif(request_type == "HELLOTO"):
            (server_msg, client_addr) = forward_hello(msg_request, client_addr, active_users)
        elif(request_type == "KILLSERVER"):
            server_msg = "KILL".encode()
            server_sock.send(server_msg)
            break
        else:
            server_msg = invalid_msg(msg_request)
        #server_sock.sendto(server_msg, (client_addr, SERVER_PORT))
        server_sock.send(server_msg)
    server_sock.close()
    """