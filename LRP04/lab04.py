import pickle
import socket
import threading
import time
import timeit
import numpy as np
import os

class ThreadArguments:
    def __init__(self, threadId, n, start_idx, end_idx, result):
        self.threadId = threadId
        self.n = n
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.result = result

def main():
    n, p, s, t = input("Enter n, p, s, t: ").split()
    
    try:
        n = int(n)
        p = int(p)
        s = int(s)
        t = int(t)
    except ValueError:
        print("User input is not an integer")

    host= '127.0.0.1'

    if (s == 0):
        master(host, p, n, t)
    else:
        slave(host, p)

def master(host, p, n, t):
    M = np.random.randint(100, size=(n,n)).tolist()
    # print(M)
    threadArgs = []
    blockSize = n/t
    remainder = n%t
    start_idx = 0
    result = []
    for i in range(0, t):
        threadArgs.append(ThreadArguments((i+1), n, start_idx, int(start_idx+blockSize + (1 if i<remainder else 0)), result))
        start_idx = int(start_idx+blockSize + (1 if i<remainder else 0))
    
    start = timeit.default_timer()
    
    srvsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Server socket opened')

    srvsocket.bind((host, p))
    print('Bind to the local port')

    srvsocket.listen(t)
    print('Started Listening')

    client_counter = 0
    while True:
        print('Waiting for connections')
        
        cli, ip = srvsocket.accept()
        index = client_counter
        
        if index >= t:
            print("Maximum number of clients reached")
            cli.close()
            continue

        client_counter+=1

        # if index < len(threadArgs):
        #     serialized_obj = pickle.dumps(threadArgs[index])
        #     cli.sendall(serialized_obj)

        data = []
        for i in range(0, len(M)):
            temp_data = []
            for j in range(threadArgs[index].start_idx, threadArgs[index].end_idx):
                temp_data.append(M[i][j])
            data.append(temp_data)
        
        serialized_arr = pickle.dumps(data)
        cli.sendall(serialized_arr)
        # print(data)

        threading._start_new_thread(NewClientSocketHandler, (cli, ip, client_counter, start,  t))

def NewClientSocketHandler(cli, ip, index, start, t):
    print('The new client has socket id: ', cli)
    
    print('Message got from client', cli)
    print(cli.recv(256).decode())

    if index == t:
        stop = timeit.default_timer()
        print("Time taken:", stop - start)

def slave(host, p):
    clisocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connected = False
    while not connected:
        try:

            clisocket.connect((host, p))
            print('Client has been connected')
            start = timeit.default_timer()
            connected = True
            
        except ConnectionRefusedError:
            print("[INFO] Connection refused by the server. Retrying in 1 second...")
            time.sleep(1)
            continue

    print('The message from server')
    # serialized_data = clisocket.recv(4096)

    
    data = []
    while True:
        packet = clisocket.recv(4096)
        if not packet: break
        data.append(packet)
    # data_arr = pickle.loads(b"".join(data))
    print (data)

    # received_object = pickle.loads(data)
    # print("Thread ID:", received_object.threadId)
    # print("Size of the square matrix:", received_object.n)
    # print("Start index:", received_object.start_idx)
    # print("End index:", received_object.end_idx)
    # print("Result:", received_object.result)
    # print()
    # print(received_object)

    msg = 'ack'
    clisocket.send(msg.encode())

    stop = timeit.default_timer()
    print("Time taken:", stop - start)


if __name__ == "__main__":
    main()