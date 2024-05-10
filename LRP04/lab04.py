import numpy as np
import timeit
import socket
import pickle
import threading
import time
t = 3

class ThreadArguments:
    def __init__(self, threadId, n, start_idx, end_idx, result):
        self.threadId = threadId
        self.n = n
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.result = result

# Function to handle client connections
def handle_client(client_socket, addr, data, index):
    print(f"[INFO] Accepted connection from {addr}")

    # Ensure index is within the bounds of the data list
    if index < len(data):
        # Serialize the t-th object using pickle and send it to the t-th client
        serialized_obj = pickle.dumps(data[index])
        client_socket.sendall(serialized_obj)
    
    print(client_socket.recv(1024))

    print(f"[INFO] Finished sending data to {addr}")
    client_socket.close()

def receive_data(server_socket):
    # Receive data from the server
    serialized_data = server_socket.recv(4096)

    # Deserialize the received data using pickle
    received_object = pickle.loads(serialized_data)

    return received_object

def main():
    # Read n, p and s as user inputs
    # n is the size of the square matrix
    # p is the port number
    # s is the status of the instance 
        # (0 for master and 1 for slave)
    n, p, s = input("Enter n, p, s: ").split()
    
    try:
        n = int(n)
        p = int(n)
        s = int(s)
    except ValueError:
        print("User input is not an integer")
    
    if (s==0):
        # Master 
        master(n,p)
    elif (s==1):
        slave(n,p)
    
def master(n, p):
    #Create a non-zero nxn square matrix M
    M = np.random.randint(100, size=(n,n)).tolist()

    threadArgs = []
    blockSize = n/t
    remainder = n%t
    start_idx = 0
    result = []
    for i in range(0, t):
        threadArgs.append(ThreadArguments((i+1), n, start_idx, int(start_idx+blockSize + (1 if i<remainder else 0)), result))
        start_idx = int(start_idx+blockSize + (1 if i<remainder else 0))
    
    start = timeit.default_timer()
    # stop = timeit.default_timer()
    # print("Time taken:", stop - start)

    host= '127.0.0.1'
    port = 12345

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((host, port))

    # Start listening for incoming connections
    server_socket.listen(t)
    print(f"[INFO] Server listening on {host}:{port}")

    try:
        client_counter = 0
        while 1:
            # Accept incoming connection
            client_socket, addr = server_socket.accept()

            # Determine the index based on the number of clients served so far
            index = client_counter
            client_counter += 1

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, threadArgs, index))
            client_thread.start()
 
            # if client_counter >= t:
            #     stop = timeit.default_timer()
            #     print("Time taken:", stop - start)
            #     print("[INFO] Server shutting down.")
            #     server_socket.close()
        
    except KeyboardInterrupt:
        print("[INFO] Server shutting down.")
        server_socket.close()

def slave(n,p):
    server_address= '127.0.0.1'
    server_port = 12345

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[INFO] Waiting for server to initiate connection...")

    connected = False
    while not connected:
        try:
            #Connect to the server
            client_socket.connect((server_address, server_port))
            start = timeit.default_timer()
            connected = True
            print(f"[INFO] Connected to server {server_address}:{server_port}")
        except ConnectionRefusedError:
            print("[INFO] Connection refused by the server. Retrying in 1 second...")
            time.sleep(1)
            continue

    try:
        # Receive and deserialize data from the server
        arg = receive_data(client_socket)

        # Process the received data
        print("Thread ID:", arg.threadId)
        print("Size of the square matrix:", arg.n)
        print("Start index:", arg.start_idx)
        print("End index:", arg.end_idx)
        print("Result:", arg.result)
        print()

        ack = 'ack'
        client_socket.sendall(ack.encode())
        # print("[INFO] Received data:", received_data)
    except ConnectionRefusedError:
        print("[INFO] Connection refused by the server.")
    finally:
        # Close the connection
        client_socket.close()
        stop = timeit.default_timer()
    print("Time taken:", stop - start)

# stop = timeit.default_timer()
# print("Time taken:", stop - start)

if __name__ == "__main__":
    main()