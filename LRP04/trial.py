import pickle
import socket
import threading
import time
import timeit
import numpy as np
import sys
from _thread import *
import threading

print_lock = threading.Lock()

host= '127.0.0.1'

def main():
    print("[0]: master\n[1]: slave")
    s = input("Enter instance: ")
    try: s = int(s)
    except ValueError:
        sys.exit("Invalid user input")

    p = input("Enter port number: ")
    try: p = int(p)
    except ValueError:
        sys.exit("Invalid user input")

    if (s < 0 and s > 1) or (p < 1000):
        sys.exit("Invalid user input")

    if (s == 0): master(p)
    elif (s == 1): slave(p)
    
def master(port):
    print("Master")
    
    n = input("Enter array size: ")
    try: n = int(n)
    except ValueError:
        sys.exit("Invalid user input")
    
    t = input("Enter number of slaves: ")
    try: t = int(t)
    except ValueError:
        sys.exit("Invalid user input")

    if n < 1 or t < 1:
        sys.exit("Invalid user input")

    M = np.random.randint(100, size=(n,n)).tolist()
    # print(M)
    submatrices = reshape_matrix(M, t)
    print(submatrices)

    svrsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svrsocket.bind((host, port))
    print("socket binded to port", port)

    svrsocket.listen()
    print("socket is listening")

    while True:
        c, addr = svrsocket.accept()
 
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
 
        # Start a new thread and return its identifier
        threading.Thread(target=threaded, args=(c, submatrices.pop(0))).start()
    
    # svrsocket.close()
    
def slave(port):
    print("Slave")
 
    clisocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    connected = False
    while not connected:
        try:
            clisocket.connect((host, port))
            print('Client has been connected')
            start = timeit.default_timer()
            connected = True
            
        except ConnectionRefusedError:
            print("[INFO] Connection refused by the server. Retrying in 1 second...")
            time.sleep(1)
            continue

    while True:
        data = clisocket.recv(4096)
        if not data:
            print('Server disconnected')
            break

        # Unpickle the received data
        submatrix = pickle.loads(data)

        print('Received submatrix from the server:', submatrix)

        # Send acknowledgment to server
        clisocket.send("Acknowledgment".encode('utf-8'))
    # close the connection
    clisocket.close()

def reshape_matrix(matrix, num_slaves):
    n = len(matrix)
    cols_per_submatrix = n // num_slaves 
    remainder_cols = n % num_slaves
    submatrices = []

    start_col = 0
    for i in range(num_slaves):
        extra_cols = 1 if i < remainder_cols else 0 
        end_col = start_col + cols_per_submatrix + extra_cols

        submatrix = [row[start_col:end_col] for row in matrix]
        submatrices.append(submatrix)

        start_col = end_col

    return submatrices

def threaded(c, submatrix):
    data_to_send = pickle.dumps(submatrix)

    c.send(data_to_send)

    ack = c.recv(1024)
    if ack:
        print('Acknowledgment received from client')

    c.close()

if __name__ == "__main__":
    main()