#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <sys/time.h>

int generateRandomNonZero();
double *pearson_cor(int *X, int *y, int n);

int main (int argc, char **argv){
    FILE *input_file = fopen(argv[1], "r");
    if (!input_file) {
        printf("Error: Unable to open input file.\n");
        return 1;
    }

    char line[256];
    while (fgets(line, sizeof(line), input_file)) {
        int n;
        if (sscanf(line, "%d", &n) != 1) {
            printf("Error: Invalid input format.\n");
            continue;
        }

        struct timeval start, end;
        
        time_t t1; 
        srand((unsigned) time (&t1));

        //Create a non-zero n x n square matrix X whose elements are assigned with random integers
        int *X = malloc(n*n*sizeof(int));
        for (int i = 0; i < n*n; i++){
            X[i] = generateRandomNonZero(); 
        }
        
        //Create a non-zero n x 1 vector y whose elements are assigned with random integers;
        int* y = (int*) malloc(n * sizeof(int)); 
        for (int i = 0; i < n; i++){
            y[i] = generateRandomNonZero();
        }

        //Create a 1 x n vector v;

        //Take note of the system time time_before;
        // clock_t time_before = clock();
        gettimeofday(&start, NULL);

        //call pearson_cor(X, y, n, n);
        double *v = pearson_cor(X, y, n);

        //Take note of the system time time_after;
        // clock_t time_after = clock();
        gettimeofday(&end, NULL);
        
        //Obtain the elapsed time time_elapsed:=time_after – time_before;
        // double time_elapsed = ((double)(time_after - time_before)) / CLOCKS_PER_SEC;
        double time_elapsed = (double)(((end.tv_sec * 1000000 + end.tv_usec)) - ((start.tv_sec * 1000000 + start.tv_usec))) / pow(10,6);

        //output time_elapsed;
        printf("time elapsed: %f seconds\n", time_elapsed);

        // printf("\n\nPearson correlation coefficients:\n");
        // for (int i = 0; i < n; i++) {
        //     printf("%f ", v[i]);
        // }
        // printf("\n");

        free(X);
        free(y);
        free(v);
        
        return 0;
}
}

int generateRandomNonZero() {
    return (rand() % 100) + 1;  // Generating random integers between 1 and 9
}

double* pearson_cor(int * X, int *y, int n){
    double *v = (double *)malloc(n * sizeof(double));
    double sum_X = 0, sum_y = 0, sum_Xy = 0, sum_X2 = 0, sum_y2 = 0;
    for (int k = 0; k < n; k++) {
        sum_y += y[k];
        sum_y2 += y[k] * y[k];
    }
    for (int i = 0; i < n; i++) {
        sum_X = sum_X2 = sum_Xy = 0;
        for (int k = 0; k < n; k++) {
            sum_X += X[k * n + i];
            sum_X2 += X[k * n + i] * X[k * n + i];
            sum_Xy += X[k * n + i] * y[k];
        }
        double numerator = n * sum_Xy - sum_X * sum_y;
        double denominator = sqrt((n * sum_X2 - sum_X * sum_X) * (n * sum_y2 - sum_y * sum_y));
        v[i] = (denominator != 0) ? numerator / denominator : 0; // Avoid division by zero
    }
    return v;
}

//https://www.geeksforgeeks.org/command-line-arguments-in-c-cpp/
//https://www.javatpoint.com/random-function-in-c
//https://www.geeksforgeeks.org/dynamically-allocate-2d-array-c/
//https://www.javatpoint.com/random-function-in-c
//https://www.geeksforgeeks.org/how-to-measure-time-taken-by-a-program-in-c/