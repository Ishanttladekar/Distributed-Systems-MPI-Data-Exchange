/*
 * Program: 03_nonblocking_exchange.c
 * Description: Asynchronous / Non-blocking communication between System 1 and System 2
 *              using MPI_Isend and MPI_Irecv to overlap computation with network transfer.
 * Architecture: Two independent CPU systems connected via a network.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

#define ARRAY_SIZE 1000000

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
            fprintf(stderr, "Error: This program requires exactly 2 processes.\n");
            fprintf(stderr, "Usage: mpirun -np 2 ./03_nonblocking_exchange\n");
        }
        MPI_Finalize();
        return 1;
    }

    int partner = (rank == 0) ? 1 : 0;
    int *send_array = (int *)malloc(sizeof(int) * ARRAY_SIZE);
    int *recv_array = (int *)malloc(sizeof(int) * ARRAY_SIZE);

    if (!send_array || !recv_array) {
        fprintf(stderr, "[System %d] Memory allocation failed!\n", rank + 1);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // Initialize outgoing array with unique numbers
    for (int i = 0; i < ARRAY_SIZE; i++) {
        send_array[i] = (rank == 0) ? (i + 1) : -(i + 1);
    }

    MPI_Request requests[2];
    MPI_Status statuses[2];

    double start_time = MPI_Wtime();

    printf("[System %d | Host: %s] Initiating non-blocking transfer (%d integers)...\n",
           rank + 1, processor_name, ARRAY_SIZE);

    // 1. Post non-blocking receive first to ensure receiver is ready
    MPI_Irecv(recv_array, ARRAY_SIZE, MPI_INT, partner, 10, MPI_COMM_WORLD, &requests[0]);

    // 2. Post non-blocking send
    MPI_Isend(send_array, ARRAY_SIZE, MPI_INT, partner, 10, MPI_COMM_WORLD, &requests[1]);

    // 3. Perform overlapping CPU computation while message is in transit across the network
    printf("[System %d | Host: %s] Performing CPU computation concurrently while network transfers data...\n",
           rank + 1, processor_name);
    
    long long local_sum = 0;
    for (int i = 0; i < ARRAY_SIZE; i++) {
        local_sum += (send_array[i] % 100);
    }

    printf("[System %d | Host: %s] Local CPU computation finished (Sum remainder: %lld). Waiting for network...\n",
           rank + 1, processor_name, local_sum);

    // 4. Wait for both non-blocking operations (send and recv) to finish
    MPI_Waitall(2, requests, statuses);

    double end_time = MPI_Wtime();

    // Verify first and last elements received
    printf("[System %d | Host: %s] Transfer completed in %.6f seconds. Received sample: [0]=%d, [%d]=%d\n",
           rank + 1, processor_name, end_time - start_time, recv_array[0], ARRAY_SIZE - 1, recv_array[ARRAY_SIZE - 1]);

    free(send_array);
    free(recv_array);

    MPI_Finalize();
    return 0;
}
