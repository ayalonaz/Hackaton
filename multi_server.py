import socket
import struct
from threading import Thread

import time
import random
import scapy.all as scapy
all_teams = {}
score_group_2 = 0
score_group_1 = 0


# from SocketServer import ThreadingMixIn

# Multithreaded Python server : TCP Server Socket Thread Pool


# def count_keys(conn):
#     counter = 0
#     t_end = time.time() + 10 * 1
#     while time.time() < t_end:
#         try:
#             data = conn.recv(2048).decode()
#         # data = data+"\n"
#     # print(data)
#             counter += 1
#         except socket.error:
#             continue
#     return conn, counter
def count_keys_1(conns_group_1):
    """
             this function count the score of group 1
             :param conns_group_1: list of all the connection objects of the clients in group 1
             :return:
      """
    global score_group_1
    t_end = time.time() + 10 * 1
    while time.time() < t_end:
        for conn in conns_group_1:
            try:
                conn.settimeout(0.1)
                data = conn.recv(2048).decode()
                score_group_1 += 1
            # data = data+"\n"
            # print(data)
            except socket.timeout:
                continue


def count_keys_2(conns_group_2):
    """
           this function count the score of group 2
           :param conns_group_2: list of all the connection objects of the clients in group 2
           :return:
    """
    global score_group_2
    t_end = time.time() + 10 * 1
    while time.time() < t_end:
        for conn in conns_group_2:
            try:
                conn.settimeout(0.1)
                data = conn.recv(2048).decode()
                score_group_2 += 1
            # data = data+"\n"
            # print(data)
            except socket.timeout:
                continue


def broadcast(udp_ip, udp_port, udp_server, first_message):
    """
       this function broadcast to all clients in network
       :param udp_ip: ip of udp protocol
       :param udp_port: port of udp protocol
       :param udp_server: object that represent the udp  connection of server
       :param first_message: message that send to all
       :return:
       """
    t_end = time.time() + 10 * 1
    while time.time() < t_end:
        print("Server started, listening on IP address " + udp_server.getsockname()[0])
        udp_server.sendto(first_message, (udp_ip, udp_port))
        time.sleep(1)




def wait_for_clients(tcp_server):
    """
    this function create a upd connect sending message to network and client begin to connect the server in tcp connection, the function keep the connection and the first data from client in dict.
    :param tcp_server: object that represent the tcp connection of server
    :return: the dictionary when the key is the connection of each client and value is the name team of the client.
    """

    global dict_of_clients
    dict_of_clients = {}
    udp_ip = "255.255.255.255"
    udp_port = 13117
    # ip_of_server = scapy.get_if_addr('eth1')
    cookie = bytes.fromhex('feedbeef')
    offer = bytes.fromhex('02')
    port = bytes.fromhex('2074')
    MESSAGE = cookie, offer, port
    first_message = struct.pack('4s 1s 2s', *MESSAGE)

    udp_server = socket.socket(socket.AF_INET,  # Internetsocket
                               socket.SOCK_DGRAM)  # UDP
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_server.bind((scapy.get_if_addr('wlp2s0'), udp_port))#bindind with local network ip and with udp port that gave us

    args_for_function = (udp_ip, udp_port, udp_server, first_message)
    thread = Thread(target=broadcast, args=args_for_function) #sending few arguments to broadcast function to send message that the server is transmiting
    thread.start()
    t_end = time.time() + 10 * 1

    while time.time() < t_end:#10 seconds
        try:
            tcp_server.settimeout(t_end - time.time())
            tcp_server.listen()
            (conn, (ip, port)) = tcp_server.accept()#wait for clients
            data = conn.recv(2048).decode()
            data.replace('\n', '')
            all_teams[conn] = data
        except socket.timeout:
            continue

    if len(all_teams) == 0:
        print("clients did not try to connect")
    return all_teams


def play_game(all_the_teams, tcp_server):
    """
       this function get the dictionary of the name teams of client from the function  "wait_for_clients" divide them to two groups and activate th game,the two threads fro each group count the score of each group and announc on the winners
       :param tcp_server: object that represent the tcp connection of server
       :param all_the_teams: dictionary of the name teams of clients and their connection
       :return:
    """
    global score_group_1, score_group_2
    random_list_of_teams = random.sample(list(all_the_teams.items()), len(all_the_teams))
    group_1 = random_list_of_teams[:int(len(random_list_of_teams) / 2)]#divide hem to two groups
    group_2 = random_list_of_teams[int(len(random_list_of_teams) / 2):]
    group_1_as_string = ""
    group_2_as_string = ""
    for idx, group in enumerate(group_1):
        if idx == len(group_1) - 1:
            group_1_as_string += group[1]
        else:
            group_1_as_string += group[1] + ","

    for idx, group in enumerate(group_2):
        if idx == len(group_2) - 1:
            group_2_as_string += group[1]
        else:
            group_2_as_string += group[1] + ","
    conns_group_1 = []
    conns_group_2 = []
    for item in group_1:
        conns_group_1.append(item[0])
    for item in group_2:
        conns_group_2.append(item[0])
    welcome_data = "Welcome to Keyboard Spamming Battle Royal." + "\n" + "Group 1:" + "\n" + "==" + "\n" + group_1_as_string + "\n" + "Group 2:" + "\n" + "==" + "\n" + group_2_as_string + "\n" + "\n" + "Start pressing keys on your keyboard as fast as you can"
    welcome_data = welcome_data.encode()
    list_of_conns = list(all_the_teams.keys())
    for conn in list_of_conns:
        conn.send(welcome_data)

    thread_1 = Thread(target=count_keys_1, args=[conns_group_1])
    thread_1.start()
    thread_2 = Thread(target=count_keys_2, args=[conns_group_2])
    thread_2.start()
    thread_1.join()
    thread_2.join()
    if score_group_1 > score_group_2:
        final_data = "Game over!" + "\n" + "Group 1 typed in " + str(
            score_group_1) + " characters.Group 2 typed " + str(score_group_2) + " " + "characters." "\n" + "Group 1 wins!" + "\n" + "\n" + "Congratulations to the winners:\n" + "==\n" + group_1_as_string
    else:
        final_data = "Game over!" + "\n" + "Group 2 typed in " + str(
            score_group_1) + " characters. Group 1 typed " + str(score_group_2) + " " + "characters." "\n" + "Group 2 wins!" + "\n" + "\n" + "Congratulations to the winners:\n" + "==\n" + group_2_as_string
    final_data = final_data.encode()
    for conn in list_of_conns:
        conn.send(final_data)
    tcp_server.close()
    main()


def main():
    global all_teams, score_group_1, score_group_2
    # host_name = socket.gethostname()
    tcp_ip = scapy.get_if_addr('wlp2s0')
    tcp_port = 2074

    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind((tcp_ip, tcp_port))
    server = socket.getfqdn()
    print(server)
    while True:
        all_teams = {}
        score_group_1 = 0
        score_group_2 = 0
        results = wait_for_clients(tcp_server)
        play_game(results, tcp_server)


if __name__ == '__main__':
    main()

