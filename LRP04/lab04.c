#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

void master(int n, int p);
int **divide_submatrix(int *M, int n, int t);

int main (int argc, char **argv){
    if (argc != 4) {
        printf("Usage: %s n p s\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);  // size of the square matrix
    int p = atoi(argv[2]);  // port
    int s = atoi(argv[3]);  // status

    if (s == 0){
        master(n, p);
    }
}

void master(int n, int p){
    /*Create a non-zero nxn square matrix M whose elements
    are assigned with random non-zero positive integers;*/
    time_t t1; 
    srand((unsigned) time (&t1));
    int *M = malloc(n*n*sizeof(int));
    for (int i = 0; i < n*n; i++){
        M[i] = (rand() % 10) + 1;  // Generating random integers between 1 and 9
    }

    printf("2D array M\n");
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++)
            printf("%d ", M[i * n + j]);
        printf("\n");
    }

    /*Read the configuration file to determine the IP addresses 
    and ports of the slaves and the number of slaves t;*/
    char IP_address[] = "127.0.0.1";
    int t = 2; // number of slaves
    
    // Allocate memory for an array of pointers to hold submatrices
    // int **submatrices = malloc(t * sizeof(int*));
    int **submatrices = divide_submatrix(M, n, t);

    struct timeval time_before, time_after;
    //Take note of the system time time_before;
    gettimeofday(&time_before, NULL);
    
    // for (int i = 0; i < t; i++){

    // }

    // Free memory allocated for each submatrix
    for (int i = 0; i < t; i++) {
        // printf("Submatrix %d:\n", i + 1);
        // int submatrix_width = (n / t) + (i < (n % t) ? 1 : 0); // Calculate width of submatrix
        // for (int row = 0; row < n; row++) {
        //     for (int col = 0; col < submatrix_width; col++) {
        //         printf("%d ", submatrices[i][row * submatrix_width + col]);
        //     }
        //     printf("\n");
        // }
        printf("Freeing Submatrix %d:\n", i + 1);
        free(submatrices[i]);
    }

    // Free memory allocated for the list of submatrices
    free(submatrices);

    // Free memory allocated for the original matrix M
    free(M);
}

int **divide_submatrix(int *M, int n, int t){
    int **submatrices = malloc(t * sizeof(int*));

    // Divide M into t submatrices column-wise
    int submatrix_width = n / t; // Width of each submatrix
    int remainder_cols = n % t;  // Number of remaining columns after division

    int start_col = 0;
    for (int i = 0; i < t; i++) {
        int submatrix_height = n;  // Height of each submatrix

        // Adjust width for the last submatrix to include any remaining columns
        int end_col = start_col + submatrix_width + (i < remainder_cols ? 1 : 0);

        // Allocate memory for the submatrix
        int *submatrix = malloc(n * (end_col - start_col) * sizeof(int));

        // Copy the corresponding columns from M to the submatrix
        for (int col = start_col; col < end_col; col++) {
            for (int row = 0; row < n; row++) {
                submatrix[row * (end_col - start_col) + (col - start_col)] = M[row * n + col];
            }
        }

        // Append the submatrix to the list of submatrices
        submatrices[i] = submatrix;

        // Print the submatrix for verification
        // printf("Submatrix %d:\n", i + 1);
        // for (int row = 0; row < n; row++) {
        //     for (int col = 0; col < end_col - start_col; col++) {
        //         printf("%d ", submatrix[row * (end_col - start_col) + col]);
        //     }
        //     printf("\n");
        // }

        // Update start_col for the next submatrix
        start_col = end_col;
    }
    return submatrices;
}