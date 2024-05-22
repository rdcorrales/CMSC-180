import pickle
import socket
import threading
import time
import timeit
import numpy as np
import os

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
    submatrix = reshape_matrix(M, t)
    
    # print(M)
    # print(submatrix)
    
    start = timeit.default_timer()
    
    srvsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Server socket opened')

    srvsocket.bind((host, p))
    print('Bind to the local port')

    srvsocket.listen(t)
    print('Started Listening')

    time_dict = {}
    client_counter = 0
    while client_counter != t:
        print('Waiting for connections')
        index = client_counter
        cli, ip = srvsocket.accept()
        variable = threading.Thread(target=NewClientSocketHandler, args=(cli, ip, pickle.dumps(submatrix[index]), start,  t, time_dict))
        variable.start()    
        client_counter+=1
        variable.join()
    
    print("Time taken:", sum(time_dict.values()))

def NewClientSocketHandler(cli, ip, serialized_data, start, t, myDict):
    
    print('The new client has socket id: ', cli)
    cli.sendall(serialized_data)
    
    print('Message got from client', ip)
    print(cli.recv(4096).decode())

    stop = timeit.default_timer()
    myDict[ip] = stop-start
    # print("Time taken:", stop - start)

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
    # Receive the actual data
    serialized_data = bytearray()
    while True:
        data_chunk = clisocket.recv(4096)
        serialized_data.extend(data_chunk)
        if (len(data_chunk) <4096):
            break

    try:
        data = pickle.loads(serialized_data)
        # print(data)
    except pickle.UnpicklingError as e:
        print(f'Error occured while unpickling: {e}')
    
    msg = 'ack'
    clisocket.send(msg.encode())

    stop = timeit.default_timer()
    print("Time taken:", stop - start)
    clisocket.close()


def reshape_matrix(matrix, num_slaves):
    n = len(matrix)
    cols_per_submatrix = n // num_slaves 
    remainder_cols = n % num_slaves
    submatrices = []

    # Split the matrix into submatrices
    start_col = 0
    for i in range(num_slaves):
        extra_cols = 1 if i < remainder_cols else 0
        end_col = start_col + cols_per_submatrix + extra_cols

        submatrix = [row[start_col:end_col] for row in matrix]
        submatrices.append(submatrix)

        start_col = end_col

    return submatrices

if __name__ == "__main__":
    main()