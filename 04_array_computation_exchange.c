/*
 * Program: 04_array_computation_exchange.c
 * Description: Parallel Workload Distribution between System 1 and System 2.
 *              System 1 distributes half of an array to System 2 over the network.
 *              Both systems compute their partial sum on their respective CPUs,
 *              and System 2 sends its partial result back for final aggregation.
 * Architecture: Two independent CPU systems connected via a network.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

#define TOTAL_ELEMENTS 1000000

int main(int argc, char *argv[]) {
    int rank, size;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Get_processor_name(processor_name, &name_len);

    if (size != 2) {
        if (rank == 0) {
            fprintf(stderr, "Error: This program must run with exactly 2 processes.\n");
            fprintf(stderr, "Usage: mpirun -np 2 ./04_array_computation_exchange\n");
        }
        MPI_Finalize();
        return 1;
    }

    int half_size = TOTAL_ELEMENTS / 2;
    double *data_buffer = NULL;
    double local_sum = 0.0;
    double start_time, end_time;

    if (rank == 0) {
        // System 1 creates the full dataset
        data_buffer = (double *)malloc(sizeof(double) * TOTAL_ELEMENTS);
        if (!data_buffer) {
            fprintf(stderr, "System 1: Memory allocation failed!\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        for (int i = 0; i < TOTAL_ELEMENTS; i++) {
            data_buffer[i] = 1.0; // Expected total sum = TOTAL_ELEMENTS
        }

        printf("====================================================================\n");
        printf("Distributed Data Processing between System 1 and System 2\n");
        printf("Total Elements: %d (System 1: %d, System 2: %d)\n", TOTAL_ELEMENTS, half_size, half_size);
        printf("====================================================================\n\n");

        start_time = MPI_Wtime();

        // System 1 sends the second half of the data to System 2 over the network
        printf("[System 1 | Host: %s] Sending %d elements to System 2 over network...\n", processor_name, half_size);
        MPI_Send(&data_buffer[half_size], half_size, MPI_DOUBLE, 1, 50, MPI_COMM_WORLD);

        // System 1 computes partial sum of its own half (0 to half_size - 1) on its CPU
        printf("[System 1 | Host: %s] Computing partial sum for elements 0 to %d on local CPU...\n", processor_name, half_size - 1);
        for (int i = 0; i < half_size; i++) {
            local_sum += data_buffer[i];
        }
        printf("[System 1 | Host: %s] Local partial sum: %.2f\n", processor_name, local_sum);

        // System 1 receives the partial sum computed by System 2
        double system2_sum = 0.0;
        MPI_Status status;
        MPI_Recv(&system2_sum, 1, MPI_DOUBLE, 1, 51, MPI_COMM_WORLD, &status);
        printf("[System 1 | Host: %s] Received partial sum from System 2: %.2f\n", processor_name, system2_sum);

        // Aggregate total sum
        double total_sum = local_sum + system2_sum;
        end_time = MPI_Wtime();

        printf("\n--------------------------------------------------------------------\n");
        printf("FINAL RESULT:\n");
        printf("Total Accumulated Sum : %.2f (Expected: %.2f)\n", total_sum, (double)TOTAL_ELEMENTS);
        printf("Total Execution Time   : %.6f seconds\n", end_time - start_time);
        printf("--------------------------------------------------------------------\n\n");

        free(data_buffer);

    } else if (rank == 1) {
        // System 2 allocates buffer for its portion
        data_buffer = (double *)malloc(sizeof(double) * half_size);
        if (!data_buffer) {
            fprintf(stderr, "System 2: Memory allocation failed!\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        // System 2 receives workload from System 1
        MPI_Status status;
        printf("[System 2 | Host: %s] Awaiting %d elements from System 1...\n", processor_name, half_size);
        MPI_Recv(data_buffer, half_size, MPI_DOUBLE, 0, 50, MPI_COMM_WORLD, &status);

        // System 2 computes partial sum of received data on its CPU
        printf("[System 2 | Host: %s] Workload received. Computing partial sum on local CPU...\n", processor_name);
        for (int i = 0; i < half_size; i++) {
            local_sum += data_buffer[i];
        }
        printf("[System 2 | Host: %s] Computed partial sum: %.2f. Sending back to System 1...\n", processor_name, local_sum);

        // Send partial sum back to System 1
        MPI_Send(&local_sum, 1, MPI_DOUBLE, 0, 51, MPI_COMM_WORLD);

        free(data_buffer);
    }

    MPI_Finalize();
    return 0;
}
