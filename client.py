import kbhit
import random
import socket
import struct
import time
import scapy.all as scapy


def try_to_connect(client_socket, host, port):
    """
                this function get message in udp connection from server check the message by some conditions and try to connect to the server.
                after connect succeed client send the server his team name and after the server send him respone
                the client begin to play and send each typing to server.


                :param client_socket: socket of client
                :param host: ip of client
                :param port: port of client
                :return:
         """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    print("Client started, listening for offer requests....")
    client.bind((scapy.get_if_addr('wlp2s0'), 13117))
    is_ok = False
    while not is_ok:
        try:
            data, address = client.recvfrom(2048)
            host, _ = address#address is a tuple
            first_data = struct.unpack('4s 1s 2s', data)
            cookie = first_data[0].hex()
            offer = str(first_data[1].hex())
            port = first_data[2].hex()

            print(f"Received offer from {host},attempting to connect...")# instantiate
            # split_data = data.split(',')
            if cookie == 'feedbeef' and offer == '02':# check if the first message from server is by some conditions
                is_ok = True
        except socket.error:
            continue

    client_socket.connect((host, port))  # connect to the server
    print("Client started, listening for offer requests")
    message = 'party_poopers' +'\n'  # take input
    client_socket.send(message.encode())  # send message
    is_ok_1 = False
    while not is_ok_1:
        try:
            data = client_socket.recv(1024).decode()  # receive response
            print(data)  # show in terminal

            is_ok_1 = True
        except socket.error:
            continue

    if "Welcome" in data:
        t_end = time.time() + 10 * 1



        client_socket.setblocking(False)
        kb = kbhit.KBHit()
        while time.time() < t_end:
            try:
                if kb.kbhit():
                    key = kb.getch()
                    client_socket.send('key'.encode())
            except:
                break
        is_ok = False
        while not is_ok:
            try:
                data = client_socket.recv(1024).decode()  # receive response
                print(data)  # show in terminal
                is_ok = True
            except socket.error:
                continue


def main():
    host = socket.gethostname()
    port = 2074  #  port number that gave us
    client_socket = socket.socket()
    client_socket.bind((scapy.get_if_addr('wlp2s0'), 8080))
    while True:
        try_to_connect(client_socket, host, port)
        client_socket.close()
        print("Server disconnected, listening for offer requests...")
        client_socket = socket.socket()


if __name__ == '__main__':
    main()