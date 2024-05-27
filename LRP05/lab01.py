import numpy as np
import timeit
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
    n = input("Enter n: ")

    try:
        matrix_size = int(n)
    except ValueError:
        print("User input is not an integer")
        return
    
    matrix = np.random.randint(100, size=(matrix_size, matrix_size)).tolist()
    y_matrix = np.random.randint(100, size=matrix_size).tolist()
    
    # #test
    # matrix = generate_x_test()
    # y_matrix = generate_y_test()
    # matrix_size = 10
        
    start_time = timeit.default_timer()

    results = pearson_cor(matrix, y_matrix, matrix_size)
    # print(results)
    stop_time = timeit.default_timer()
    print("time elapsed: ", stop_time-start_time)

def pearson_cor(X_matrix, y_matrix, n):
    r_array = []

    for i in range(n):
        sum_x = 0
        sum_x_sq = 0
        for row in X_matrix:
            sum_x += row[i]
            sum_x_sq += (row[i] * row[i])
        sum_y = sum(y_matrix)                    
        sum_y_sq = 0
        for y in y_matrix:
            sum_y_sq += y*y
        sum_xy = 0
        for row, y in zip(X_matrix, y_matrix):
            sum_xy += row[i]*y
        
        num = (n*sum_xy) - (sum_x*sum_y)
        denom = math.sqrt(((n*sum_x_sq)-(sum_x*sum_x))*((n*sum_y_sq)-(sum_y*sum_y)))
        r = num/denom
        
        r_array.append(r)

    return r_array

if __name__ == "__main__":
    main()