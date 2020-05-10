import socket
import sys
import select
from signal import signal, SIGINT

EXIT        = 'you have ended your session'
EXITING     = 'EXIT'


#sockets communication parameters
SERVER_PORT = 12100
SERVER_IP   = '127.0.0.1'
MSG_SIZE = 1024


client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # TCP

client_sock.connect((SERVER_IP, SERVER_PORT))
# o select quer ficar a espera de ler o socket e ler do stdin (consola)
inputs = [client_sock, sys.stdin]


def handler(signal_received, frame):
    client_msg = EXITING
    client_msg = client_msg.encode()
    client_sock.send(client_msg)
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    server_msg = client_sock.recv(MSG_SIZE)
    server_request = server_msg.decode()
    print("Message received from server:", server_request)
    if server_request == EXIT:
        exit()
    

signal(SIGINT, handler)

while True:
  print('Input message to server: ')
  ins, outs, exs = select.select(inputs,[],[])
  #select devolve para a lista ins quem esta a espera de ler
  for i in ins:
    # i == sys.stdin - alguem escreveu na consola, vamos ler e enviar
    if i == sys.stdin:
        user_msg = sys.stdin.readline()
        client_msg = user_msg.encode()
        client_sock.send(client_msg)
    # i == sock - o servidor enviou uma mensagem para o socket
    elif i == client_sock:
        server_msg = client_sock.recv(MSG_SIZE)
        server_request = server_msg.decode()
        print("Message received from server:", server_request)
        if server_request == EXIT:
          exit()
