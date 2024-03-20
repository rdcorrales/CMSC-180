#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/time.h>
#include <pthread.h>
#include <unistd.h>

int generateRandomNonZero();
double *pearson_cor(int *X, int *y, int n, int start_idx, int end_idx);
void *compute_correlations(void *args);

int *X;
int *y;

typedef struct {
    int thread_id;
    int n;
    int start_idx;
    int end_idx;
    double *result;
} ThreadArgs;

void set_affinity(pthread_t thread, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
}

int main (int argc, char **argv){

    FILE *input_file = fopen(argv[1], "r");
    if (!input_file) {
        printf("Error: Unable to open input file.\n");
        return 1;
    }

    char line[256];
    while (fgets(line, sizeof(line), input_file)) {
        int n, t;
        if (sscanf(line, "%d %d", &n, &t) != 2) {
            printf("Error: Invalid input format.\n");
            continue;
        }
        struct timeval start, end;

        time_t t1; 
        srand((unsigned) time (&t1));

        //Create a non-zero n x n square matrix X whose elements are assigned with random integers
        X = malloc(n*n*sizeof(int));
        for (int i = 0; i < n*n; i++){
            X[i] = generateRandomNonZero(); 
        }
        
        //Create a non-zero n x 1 vector y whose elements are assigned with random integers;
        y = (int*) malloc(n * sizeof(int)); 
        for (int i = 0; i < n; i++){
            y[i] = generateRandomNonZero();
        }

        // printf("2D array X\n");
        // for (int i = 0; i < n; i++) {
        //     for (int j = 0; j < n; j++)
        //         printf("%d ", X[i * n + j]);
        //     printf("\n");
        // }

        //Create a 1 x n vector v;
        double *v = malloc(n * sizeof(double));

        int num_cores = sysconf(_SC_NPROCESSORS_ONLN); // Get number of online CPU cores
        int num_threads = t; // Leaving out one core
        int num_threads_per_core = (num_cores == 4) ? 3 : ((num_cores == 8) ? 7 : 1);

        int core_assignments[t];
        for (int i = 0; i < t; i++) {
            core_assignments[i] = i % num_threads_per_core; // Assign threads sequentially to cores
        }
        // // //Take note of the system time time_before;
        gettimeofday(&start, NULL);
        
        pthread_t threads[t];
        ThreadArgs args[t];
        int block_size = n / num_threads;
        int remainder = n % num_threads;
        int start_idx = 0;
        for (int i = 0; i < num_threads; i++) {
            args[i].thread_id = i + 1;
            args[i].n = n; //row
            args[i].start_idx = start_idx; //start column
            args[i].end_idx = start_idx + block_size + (i < remainder ? 1 : 0); //end column
            args[i].result = v;
            
            cpu_set_t cpuset;
            CPU_ZERO(&cpuset);
            int core_id = (num_cores == 4) ? i % 3 : i % 7; // Assign threads to cores 0, 1, and 2 for 4 cores; 0 to 6 for 8 cores
            CPU_SET(core_id, &cpuset);
            
            pthread_create(&threads[i], NULL, compute_correlations, (void *)&args[i]);

            set_affinity(threads[i], core_assignments[i]);
            

            start_idx = args[i].end_idx;
        }

        for (int i = 0; i < t; i++) {
            pthread_join(threads[i], NULL);
        }
        
        // printf("\narray y\n");
        // for (int i = 0; i < n; i++) { 
        //     printf("%d ", y[i]); 
        // }
        // printf("\n");

        // printf("\n\nPearson correlation coefficients:\n");
        // for (int i = 0; i < n; i++) {
        //     printf("%f ", v[i]);
        // }
        // printf("\n");

        // //Take note of the system time time_after;
        gettimeofday(&end, NULL);

        // //Obtain the elapsed time time_elapsed:=time_after – time_before;
        double time_elapsed = (double)(((end.tv_sec * 1000000 + end.tv_usec)) - ((start.tv_sec * 1000000 + start.tv_usec))) / pow(10,6);

        // //output time_elapsed;
        printf("n:%d t:%d - time elapsed: %f seconds\n", n, t, time_elapsed);

        free(X);
        free(y);
        free(v);
    }
    fclose(input_file);
    return 0;
}

int generateRandomNonZero() {
    return (rand() % 10) + 1;  // Generating random integers between 1 and 9
}

double* pearson_cor(int * X, int *y, int n, int start_idx, int end_idx){
    double *v = (double *)malloc(n * sizeof(double));
    double sum_X = 0, sum_y = 0, sum_Xy = 0, sum_X2 = 0, sum_y2 = 0;

    for (int k = 0; k < n; k++) {
        sum_y += y[k];
        sum_y2 += y[k] * y[k];
    }
    for (int i = start_idx; i < end_idx; i++) {
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

void *compute_correlations(void *args) {
    ThreadArgs *thread_args = (ThreadArgs *)args;
    double *v = pearson_cor(X, y, thread_args->n, thread_args->start_idx, thread_args->end_idx);
    for (int i = thread_args->start_idx; i < thread_args->end_idx; i++) {
        thread_args->result[i] = v[i];
        // printf("Working on row %d\n", i);
    }
    free(v);
    return 0;
}

//https://www.geeksforgeeks.org/command-line-arguments-in-c-cpp/
//https://www.javatpoint.com/random-function-in-c
//https://www.geeksforgeeks.org/dynamically-allocate-2d-array-c/
//https://www.javatpoint.com/random-function-in-c
//https://www.geeksforgeeks.org/how-to-measure-time-taken-by-a-program-in-c/