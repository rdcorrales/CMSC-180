import pickle
import socket
import threading
import time
import timeit
import numpy as np
import os
import json
import base64

# class ThreadArguments:
#     def __init__(self, threadId, submatrix, n, start_idx, end_idx, result):
#         self.threadId = threadId
#         self.submatrix = submatrix
#         self.n = n
#         self.start_idx = start_idx
#         self.end_idx = end_idx
#         self.result = result

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

def reshape_matrix(matrix, num_slaves):
    n = len(matrix)
    cols_per_submatrix = n // num_slaves  # Determine the number of columns in each submatrix
    remainder_cols = n % num_slaves  # Determine the number of remainder columns
    submatrices = []

    # Split the matrix into submatrices
    start_col = 0
    for i in range(num_slaves):
        extra_cols = 1 if i < remainder_cols else 0  # Distribute remainder columns among submatrices
        end_col = start_col + cols_per_submatrix + extra_cols

        # Extract the columns for the current submatrix
        submatrix = [row[start_col:end_col] for row in matrix]
        submatrices.append(submatrix)

        start_col = end_col

    return submatrices

def master(host, p, n, t):
    M = np.random.randint(100, size=(n,n)).tolist()
    # print(M)
    submatrix = reshape_matrix(M, t)
    # print(submatrix)
    # threadArgs = []
    # blockSize = n/t
    # remainder = n%t
    # start_idx = 0
    # result = []
    # for i in range(0, t):
    #     threadArgs.append(ThreadArguments((i+1), submatrix[i], n, start_idx, int(start_idx+blockSize + (1 if i<remainder else 0)), result))
    #     start_idx = int(start_idx+blockSize + (1 if i<remainder else 0))
    
    start = timeit.default_timer()
    
    srvsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Server socket opened')

    srvsocket.bind((host, p))
    print('Bind to the local port')

    srvsocket.listen(t)
    print('Started Listening')

    myDict = {}

    client_counter = 0
    while client_counter != t:
        print('Waiting for connections')
        index = client_counter
        cli, ip = srvsocket.accept()
        submatrix_json = {"submatrix": submatrix[index]}
        submatrix_dumps = json.dumps(submatrix_json)
        submatrix_b64 = base64.b64encode(submatrix_dumps.encode()).decode()
        print(submatrix_b64[:10])
        print(submatrix_b64[-10:])
        # variable = threading.Thread(target=NewClientSocketHandler, args=(cli, ip, pickle.dumps(submatrix[index]), start,  t, myDict))
        variable = threading.Thread(target=NewClientSocketHandler, args=(cli, ip, submatrix_b64, start,  t, myDict))
        variable.start()    
        client_counter+=1
        variable.join()
        # print(data
    
    print("Time taken:", sum(myDict.values()))
    
def NewClientSocketHandler(cli, ip, serialized_data, start, t, myDict):
    
    print('The new client has socket id: ', cli)
    # cli.sendall(serialized_data)
    data_length = len(serialized_data)
    cli.sendall(data_length.to_bytes(4, byteorder='big'))  # Send length as 4 bytes
    cli.sendall(serialized_data.encode())
    
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

    # First receive the length of the data
    data_length_bytes = clisocket.recv(4)
    data_length = int.from_bytes(data_length_bytes, byteorder='big')

    # Receive the actual data
    serialized_data = bytearray()
    while len(serialized_data) < data_length:
        data_chunk = clisocket.recv(min(4096, data_length - len(serialized_data)))
        serialized_data.extend(data_chunk)
    
    try:
        data_str = serialized_data.decode()
        print(data_str[:10])
        print(data_str[-10:])
        # Decode the Base64 string
        decoded_data = base64.b64decode(data_str.encode()).decode()
        
        # Deserialize the JSON data
        submatrix_json = json.loads(decoded_data)
        submatrix = submatrix_json['submatrix']

        # print("Received submatrix:", submatrix)
    except pickle.UnpicklingError as e:
        print(f'Error occured while unpickling: {e}')

    

    # serialized_data = bytearray()
    # serialized_data = []
    # while True:
        
    #     data_chunk = clisocket.recv(4096).decode()
        
    #     serialized_data.append(data_chunk)
    #     # if len(data_chunk) < 4096:
    #     if not data_chunk:
    #         break

    # data_chunk = clisocket.recv(4096).decode()    


    # try:
    #     print(data_chunk[:10])
    # except pickle.UnpicklingError as e:
    #     print(f'Error occured while unpickling: {e}')
    # # print(data)
    
    msg = 'ack'
    clisocket.send(msg.encode())

    stop = timeit.default_timer()
    print("Time taken:", stop - start)

if __name__ == "__main__":
    main()