//https://github.com/nikhilroxtomar/Multiple-Client-Server-Program-in-C-using-fork
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>

#define PORT 4444

int generateRandomNonZero();
// double *pearson_cor(int *X, int *y, int n);
int master(int n, int p, int s);
int slave(int n, int p, int s);

typedef struct {
    int thread_id;
    int n;
    int start_idx;
    int end_idx;
    double *result;
} ThreadArgs;

int main (int argc, char **argv){
    FILE *input_file = fopen(argv[1], "r");
    if (!input_file) {
        printf("Error: Unable to open input file.\n");
        return 1;
    }

    FILE *output_file = fopen("results.txt", "w");
    if (!output_file) {
        printf("Error: Unable to create output file.\n");
        fclose(input_file);
        return 1;
    }

    char line[256];
    //Read n, p and s as user inputs
    //n is the size of the square matrix
    //p is the port number
    //s is the status of the instance (0 for master and 1 for slave)
    while (fgets(line, sizeof(line), input_file)) {
        int n, p, s;
        if (sscanf(line, "%d %d %d", &n, &p, &s) != 3) {
            printf("Error: Invalid input format.\n");
            continue;
        }

        if (s == 0){
            //call master
            master(n,p,s);
        } else {
            slave(n,p,s);
        }
    }
}

int master(int n, int p, int s){

    struct timeval start, end;

    time_t t1; 
    srand((unsigned) time (&t1));

    //Create a non-zero n x n square matrix X whose elements are 
    //assigned with random integers
    int *X = malloc(n*n*sizeof(int));
    for (int i = 0; i < n*n; i++){
        X[i] = generateRandomNonZero(); 
    }

    double *v = malloc(n * sizeof(double));

    int t; 

    //Read the configuration file...
    FILE *config_file = fopen("config_master.txt", "r");
    if (!config_file) {
        printf("Error: Unable to open config file.\n");
        return 1;
    }
    //...to determine the number of slaves t;
    if (fscanf(config_file, "%d", &t) != 1) {
            printf("Error: Invalid configuration file format.\n");
            fclose(config_file);
            return 1;
    }
    if (t <= 0) {
            printf("Error: Invalid number of slaves in configuration file.\n");
            fclose(config_file);
            return 1;
    }
    fclose(config_file);
    // printf("%d", t);

    //Divide X into t submatrices of size n/t x n each
    ThreadArgs args[t];
    int block_size = n / t;
    int remainder = n % t;
    int start_idx = 0;
    for (int i = 0; i < t; i++){
        args[i].thread_id = i + 1;
        args[i].n = n;
        args[i].start_idx = start_idx;
        args[i].end_idx = start_idx + block_size + (i < remainder ? 1 : 0);
        args[i].result = v;
    }
    // Take note of the system time time_before;
    gettimeofday(&start, NULL);

    int sockfd, ret;
	 struct sockaddr_in serverAddr;

	int newSocket;
	struct sockaddr_in newAddr;

	socklen_t addr_size;

	char buffer[1024];
	pid_t childpid;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if(sockfd < 0){
		printf("[-]Error in connection.\n");
		exit(1);
	}
	printf("[+]Server Socket is created.\n");

	memset(&serverAddr, '\0', sizeof(serverAddr));
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(PORT);
	serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");

	ret = bind(sockfd, (struct sockaddr*)&serverAddr, sizeof(serverAddr));
	if(ret < 0){
		printf("[-]Error in binding.\n");
		exit(1);
	}
	printf("[+]Bind to port %d\n", 4444);

	if(listen(sockfd, 10) == 0){
		printf("[+]Listening....\n");
	}else{
		printf("[-]Error in binding.\n");
	}


	while(1){
		newSocket = accept(sockfd, (struct sockaddr*)&newAddr, &addr_size);
		if(newSocket < 0){
			exit(1);
		}
		printf("Connection accepted from %s:%d\n", inet_ntoa(newAddr.sin_addr), ntohs(newAddr.sin_port));

		if((childpid = fork()) == 0){
			close(sockfd);

			while(1){
				recv(newSocket, buffer, 1024, 0);
				if(strcmp(buffer, ":exit") == 0){
					printf("Disconnected from %s:%d\n", inet_ntoa(newAddr.sin_addr), ntohs(newAddr.sin_port));
					break;
				}else{
					printf("Client: %s\n", buffer);
					send(newSocket, buffer, strlen(buffer), 0);
					bzero(buffer, sizeof(buffer));
				}
			}
		}

	}

	close(newSocket);


	return 0;



    int submatrix_size = (args[i].end_idx - args[i].start_idx) * n * sizeof(int);
    char *submatrix_data = (char*)malloc(submatrix_size);
    memcpy(submatrix_data, &X[args[i].start_idx * n], submatrix_size);

}

int slave(int n, int p, int s){
    return 0;
}

int generateRandomNonZero() {
    return (int)(rand() % 100) + 1;  // Generating random integers between 1 and 9
}