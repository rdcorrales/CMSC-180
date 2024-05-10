#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/time.h>
#include <math.h>
// #define PORT 8080
typedef struct {
    int thread_id;
    int n;
    int start_idx;
    int end_idx;
    double *result;
} ThreadArgs;

int generateRandomNonZero();
void *handle_client(void *socket_desc);
int master(int n, int port, int numSlaves);
int slave(int n, int port);

int *M;

int main(){
    int n, p, s, t;
    scanf("%d %d %d %d", &n, &p, &s, &t);

    if (s == 0){
        master(n, p, t);
    } else if (s == 1) {
        // slave(n, p);
        printf("Waiting for server on port %d...\n", p);
        int client_fd = slave(n, p);
        if (client_fd != -1) {
            printf("Connected to server!\n");
            // Handle communication with server here
        } else {
            printf("Failed to connect to server. Exiting...\n");
        }
    }
    return 0;
}

int master(int n, int port, int numSlaves){
    printf("In master\n");

    //Create a non-zero nxn square matrix M whose elements are 
    //assigned with random non-zero positive integers
    M = malloc(n*n*sizeof(int));
        for (int i = 0; i < n*n; i++){
            M[i] = generateRandomNonZero(); 
    }

    double *v = malloc(n * sizeof(double));

    ThreadArgs args[numSlaves];
    int block_size = n / numSlaves;
    int remainder = n % numSlaves;
    int start_idx = 0;
    for (int i = 0; i < numSlaves; i++) {
        args[i].thread_id = i + 1;
        args[i].n = n; //row
        args[i].start_idx = start_idx; //start column
        args[i].end_idx = start_idx + block_size + (i < remainder ? 1 : 0); //end column
        args[i].result = v;
        start_idx = args[i].end_idx;
    }

    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    char* hello = "Hello from server";

    struct timeval time_before, time_after;

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
 
    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR, &opt,
                   sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);
 
    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr*)&address,
             sizeof(address))
        < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", port);

    int client_count = 0;
    gettimeofday(&time_before, NULL);
    while(client_count < numSlaves){
        if ((new_socket = accept(server_fd, (struct sockaddr*)&address, &addrlen)) < 0) {
            perror("accept");
            exit(EXIT_FAILURE);
        }

        // Create a new thread for each client connection
        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, handle_client, (void*)&args[client_count]) < 0) {
            perror("could not create thread");
            exit(EXIT_FAILURE);
        }
        
        // Detach the thread to allow it to run independently
        pthread_detach(thread_id);
        client_count++;

        // if (client_count == numSlaves) {
        //     break; // Break the loop after accepting 't' clients
        // }
    }

    while (client_count > 0) {
        sleep(1); // Wait for 1 second
        client_count--;
    }
    gettimeofday(&time_after, NULL);

    // Calculate time taken
    double elapsed_time = (double)(((time_after.tv_sec * 1000000 + time_after.tv_usec)) - ((time_before.tv_sec * 1000000 + time_before.tv_usec))) / pow(10,6);

    printf("Time taken to receive messages from %d clients: %.6f seconds\n", numSlaves, elapsed_time);
    return 0; 
}

int slave(int n, int port){
    printf("In slave\n");
    int status, client_fd;
    struct sockaddr_in serv_addr;
    char* hello = "Hello from client";
    char buffer[1024] = { 0 };

    struct timeval time_before, time_after;
    while(1){
        if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            printf("\n Socket creation error \n");
            return -1;
        }
 
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(port);
 
        // Convert IPv4 and IPv6 addresses from text to binary
        // form
        if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)
            <= 0) {
            printf(
                "\nInvalid address/ Address not supported \n");
            return -1;
        }
 
        if ((status
            = connect(client_fd, (struct sockaddr*)&serv_addr,
                   sizeof(serv_addr)))
            < 0) {
            printf("Failed to connect to server. Retrying in 1 second...\n");
            close(client_fd);
            sleep(1); // Wait for 1 second before retrying
        } else {
            // Connection successful
        break;
        }
    }
    gettimeofday(&time_before, NULL);
    // Receive message from server
    ssize_t valread = read(client_fd, buffer, 1024);
    printf("Received from server: %s\n", buffer);

    // Send response back to server
    char* response = "ack";
    send(client_fd, response, strlen(response), 0);
    printf("Response sent to server\n");

    // Capture time after sending message
    gettimeofday(&time_after, NULL);

    double send_elapsed_time = (double)(((time_after.tv_sec * 1000000 + time_after.tv_usec)) - ((time_before.tv_sec * 1000000 + time_before.tv_usec))) / pow(10,6);

    printf("Time taken to send message to server: %.6f seconds\n", send_elapsed_time);

    // Keep client connected
    while (1) {
        // Receive any further messages from server
        ssize_t valread = read(client_fd, buffer, 1024);
        if (valread <= 0) {
            break; // Server disconnected
        }
        printf("Received from server: %s\n", buffer);
        
        // Send any further responses to server
        // Example: send(client_fd, response, strlen(response), 0);
    }

    
    // Close client socket
    close(client_fd);
    return 0;
}

void *handle_client(void *args) {
    ThreadArgs *thread_args = (ThreadArgs*)args;
    int client_socket = -1; // Initialize client socket

    // Connect to client
    if ((client_socket = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\n Socket creation error \n");
        pthread_exit(NULL);
    }
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    // Convert IPv4 and IPv6 addresses from text to binary
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        printf("\nInvalid address/ Address not supported \n");
        pthread_exit(NULL);
    }
    if (connect(client_socket, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("\nConnection Failed \n");
        pthread_exit(NULL);
    }

    // Serialize ThreadArgs struct into a string format
    char args_str[1024]; // Assuming serialized string won't exceed 1024 characters
    snprintf(args_str, sizeof(args_str), "%d %d %d %d %p", thread_args->thread_id, thread_args->n, thread_args->start_idx, thread_args->end_idx, (void*)thread_args->result);

    // Send serialized ThreadArgs struct to client
    send(client_socket, args_str, strlen(args_str), 0);

    // Close client socket
    close(client_socket);
    pthread_exit(NULL);
    
}

int generateRandomNonZero() {
    return (int)(rand() % 100) + 1;  // Generating random integers between 1 and 9
}