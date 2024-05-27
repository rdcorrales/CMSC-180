import pickle
import socket
import threading
import time
import timeit
import numpy as np
import os
import psutil
import random
import math

def generate_y_test():
    return ([53.1, 49.7, 48.4, 54.2, 54.9, 43.7, 47.2, 45.2, 54.4, 50.4])

def generate_x_test():
    array = []
    x_array = [3.63, 3.02, 3.82, 3.42, 3.59, 2.87, 3.03, 3.46, 3.36, 3.3]
    
    for x in x_array:
        temp_array = [x] * len(x_array)
        array.append(temp_array)

    return array

def main():
    n, p, s, t = input("Enter n, p, s, t: ").split()

    try:
        n = int(n)
        p = int(p)
        s = int(s)
        t = int(t)
    except ValueError:
        print("User input is not an integer")
        return

    host = '127.0.0.1'
    if s == 0:
        run_master(host, p, n, t)
    else:
        run_slave(host, p)

def core_affine_master():
    process = psutil.Process(os.getpid())
    master_core = 0
    process.cpu_affinity([master_core])
    print(f"Master process is pinned to core {master_core}")

def core_affine_slave():
    process = psutil.Process(os.getpid())
    available_cores = psutil.cpu_count(logical=False)
    slave_core = random.randint(1, available_cores - 1)
    process.cpu_affinity([slave_core])
    print(f"Slave process is pinned to core {slave_core}")

def run_master(host, port, matrix_size, num_slaves):
    #core_affine
    core_affine_master()

    matrix = np.random.randint(100, size=(matrix_size, matrix_size)).tolist()
    
    #test
    # matrix = generate_x_test()
    
    submatrices = split_matrix(matrix, num_slaves)
    
    # print
    # print(matrix)
    # for submatrix in submatrices:
    #     print(submatrix)
    # print_matrix_elements(submatrices)
    
    y_matrix = np.random.randint(100, size=matrix_size).tolist()
    
    # test
    # y_matrix = generate_y_test()
    
    #print
    # print(y_matrix)

    for submatrix in submatrices:
        submatrix.append(y_matrix)

    for submatrix in submatrices:
        print(submatrix)
    
    
    start_time = timeit.default_timer()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(num_slaves)
        print('Server is listening for connections')

        threads = []
        slave_ids = {}
        results = [None] * num_slaves

        for i in range(num_slaves):
            client_socket, client_address = server_socket.accept()
            print(f'Connected to client {client_address}')
            slave_id = i
            slave_ids[client_address] = slave_id
            # print_matrix_elements(submatrices[i])
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address, pickle.dumps(submatrices[slave_id]), slave_id, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    # for slave_id, result in enumerate(results):
    #     print(f"Results from slave {slave_id}: {result}")
    combined_results = []
    for result in results:
        if result:
            combined_results.extend(result)

    # print("Combined results:", combined_results)    

    stop_time = timeit.default_timer()

    print("Total time taken:", stop_time - start_time)

def handle_client(client_socket, client_address, serialized_data, slave_id, results):
    with client_socket:
        print(f'Connected to client {client_address}')
        client_socket.sendall(len(serialized_data).to_bytes(4, byteorder='big') + serialized_data)
        print(f'Sent data to client {client_address}')

        r_array_length = int.from_bytes(client_socket.recv(4), byteorder='big')
        r_array_data = bytearray()

        while len(r_array_data) < r_array_length:
            data_chunk = client_socket.recv(4096)
            r_array_data.extend(data_chunk)

        # ack_message = client_socket.recv(4096).decode()
        # print(f'Received acknowledgment from client {client_address}: {ack_message}')
        r_array = pickle.loads(r_array_data)
        results[slave_id] = r_array

        print(f'Slave ID: {slave_id} completed processing')

def run_slave(host, port):
    #core_affine
    core_affine_slave()

    connected = False
    while not connected:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                connected = True
                print('Client has connected to the server')

                data_length = int.from_bytes(client_socket.recv(4), byteorder='big')
                serialized_data = bytearray()

                while len(serialized_data) < data_length:
                    data_chunk = client_socket.recv(4096)
                    serialized_data.extend(data_chunk)

                data = pickle.loads(serialized_data)
                y_matrix = data.pop(-1)
                
                start_time = timeit.default_timer()
                
                lengths = len(data[0])
                n = len(y_matrix)
                # print(f'Received data from server: {data}')
                # print_matrix_elements(data)
                # print(data)
                # print(y_matrix)
                # print(lengths)
                
                r_array = []

                for i in range(lengths):
                    sum_x = 0
                    sum_x_sq = 0
                    for row in data:
                        sum_x += row[i]
                        sum_x_sq += (row[i] * row[i])
                    sum_y = sum(y_matrix)                    
                    sum_y_sq = 0
                    for y in y_matrix:
                        sum_y_sq += y*y
                    sum_xy = 0
                    for row, y in zip(data, y_matrix):
                        sum_xy += row[i]*y
                    
                    num = (n*sum_xy) - (sum_x*sum_y)
                    denom = math.sqrt(((n*sum_x_sq)-(sum_x*sum_x))*((n*sum_y_sq)-(sum_y*sum_y)))
                    r = num/denom
                    
                    r_array.append(r)
                
                # print(r_array)
                stop_time = timeit.default_timer()

                serialized_r_array = pickle.dumps(r_array)
                client_socket.sendall(len(serialized_r_array).to_bytes(4, byteorder='big') + serialized_r_array)
                # client_socket.sendall(b'ack')
                
                print("Time taken:", stop_time - start_time)

        except ConnectionRefusedError:
            print("[INFO] Connection refused by the server. Retrying in 1 second...")
            time.sleep(1)

def split_matrix(matrix, num_slaves):
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

def print_matrix_elements(matrix):
    if not matrix:
        print("Matrix is empty")
        return
    first_element = matrix[0]
    last_element = matrix[-1]
    middle_element = matrix[len(matrix) // 2]
    print(f"First element: {first_element}, Middle element: {middle_element}, Last element: {last_element}")

if __name__ == "__main__":
    main()