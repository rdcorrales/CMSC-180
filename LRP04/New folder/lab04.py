import socket
import threading
import signal
import sys
import time

server_socket = None
clients = []


# Function to handle client connections
def handle_client(client_socket, address):
    print(f"[+] Accepted connection from {address}")
    clients.append(client_socket)

    # Receive data from the client
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Received from {address}: {data.decode('utf-8')}")

        # Echo the received data back to the client
        for client in clients:
            client.send(data)

    # Close the client socket
    client_socket.close()
    print(f"[-] Connection closed with {address}")

# Function to run as a server
def run_server(port, num_clients):
    global server_socket
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific IP address and port
    server_socket.bind(('0.0.0.0', port))

    # Listen for incoming connections
    server_socket.listen(num_clients)
    print(f"[*] Server is listening for {num_clients} incoming connections...")

    try:
        while len(clients) < num_clients-1:
            if len(clients) >= num_clients-1:
                break
            # Accept a new connection
            client_socket, address = server_socket.accept()

            # Create a new thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()

        print("[*] All clients connected.")

        # Wait for all clients to disconnect
        for client in clients:
            client_handler.join()

    except KeyboardInterrupt:
        print("[!] Server interrupted. Closing...")
        server_socket.close()
        sys.exit(0)  # Exit gracefully

def signal_handler(sig, frame):
    print('[!] SIGINT received. Exiting...')
    if server_socket:
        server_socket.close()
    sys.exit(0)

# Function to run as a client
def run_client(port):
    connected = False
    while not connected:
        try:
            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            client_socket.connect(('localhost', port))
            connected = True
            print("[*] Connected to the server.")
        except ConnectionRefusedError:
            print("[!] Server is not available. Retrying in 5 seconds...")
            time.sleep(5)

    try:
        # Send data to the server
        while True:
            message = input("Enter message to send: ")
            client_socket.send(message.encode('utf-8'))

            # Receive data from the server
            data = client_socket.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")
    except KeyboardInterrupt:
        print("[!] Client interrupted. Closing...")
        client_socket.close()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    # Ask for user input for port number (p) and server/client mode (s)
    p = int(input("Enter port number: "))
    s = int(input("Enter 0 for server or 1 for client: "))
    t = int(input("Enter number of clients: "))

    if s == 0:
        run_server(p, t)
    elif s == 1:
        run_client(p)
    else:
        print("Invalid input for server/client mode.")
