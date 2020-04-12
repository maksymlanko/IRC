import socket
import sys
import select


#sockets communication parameters
SERVER_PORT = 12100
SERVER_IP   = '127.0.0.1'
MSG_SIZE = 1024


client_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# o select quer ficar a espera de ler o socket e ler do stdin (consola)
inputs = [client_sock, sys.stdin]


while True:
  print('Input message to server: ')
  ins, outs, exs = select.select(inputs,[],[])
  #select devolve para a lista ins quem esta a espera de ler
  for i in ins:
    # i == sys.stdin - alguem escreveu na consola, vamos ler e enviar
    if i == sys.stdin:
        user_msg = sys.stdin.readline()
        client_msg = user_msg.encode()
        client_sock.sendto(client_msg,(SERVER_IP,SERVER_PORT))
    # i == sock - o servidor enviou uma mensagem para o socket
    elif i == client_sock:
        (server_msg,addr) = client_sock.recvfrom(MSG_SIZE)
        server_request = server_msg.decode()
        print("Message received from server:", server_request)
