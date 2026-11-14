/*
 * Program: 01_basic_exchange.c
 * Description: Point-to-Point data exchange between System 1 (Rank 0) and System 2 (Rank 1)
 *              using blocking MPI_Send and MPI_Recv.
 * Architecture: Two independent CPU systems connected via a network.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

#define BUFFER_SIZE 256
#define TAG_DATA 100
#define TAG_ACK  200

int main(int argc, char *argv[]) {
    int rank, size;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;

    // Initialize the MPI environment
    MPI_Init(&argc, &argv);

    // Get the total number of processes
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Get the rank (ID) of the current process
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Get the name of the physical machine (hostname)
    MPI_Get_processor_name(processor_name, &name_len);

    // Ensure exactly 2 systems / processes are participating
    if (size != 2) {
        if (rank == 0) {
            fprintf(stderr, "Error: This program must be run with exactly 2 processes (one for System 1, one for System 2).\n");
            fprintf(stderr, "Usage: mpirun -np 2 ./01_basic_exchange\n");
        }
        MPI_Finalize();
        return 1;
    }

    if (rank == 0) {
        // SYSTEM 1 (Rank 0)
        char send_msg[BUFFER_SIZE];
        char recv_msg[BUFFER_SIZE];
        MPI_Status status;

        snprintf(send_msg, BUFFER_SIZE, "Hello from System 1 (Host: %s, CPU Core Active)", processor_name);

        printf("\n=======================================================\n");
        printf("[System 1 | Rank 0 | Node: %s] Initialized.\n", processor_name);
        printf("[System 1 | Rank 0] Sending message to System 2: \"%s\"\n", send_msg);

        // Blocking Send to System 2 (Rank 1)
        MPI_Send(send_msg, (int)strlen(send_msg) + 1, MPI_CHAR, 1, TAG_DATA, MPI_COMM_WORLD);

        printf("[System 1 | Rank 0] Message sent. Waiting for response from System 2...\n");

        // Blocking Receive acknowledgment from System 2 (Rank 1)
        MPI_Recv(recv_msg, BUFFER_SIZE, MPI_CHAR, 1, TAG_ACK, MPI_COMM_WORLD, &status);

        printf("[System 1 | Rank 0] Received acknowledgment from System 2: \"%s\"\n", recv_msg);
        printf("=======================================================\n\n");

    } else if (rank == 1) {
        // SYSTEM 2 (Rank 1)
        char recv_msg[BUFFER_SIZE];
        char reply_msg[BUFFER_SIZE];
        MPI_Status status;

        printf("[System 2 | Rank 1 | Node: %s] Initialized. Waiting for data from System 1...\n", processor_name);

        // Blocking Receive from System 1 (Rank 0)
        MPI_Recv(recv_msg, BUFFER_SIZE, MPI_CHAR, 0, TAG_DATA, MPI_COMM_WORLD, &status);

        printf("[System 2 | Rank 1] Received data from System 1: \"%s\"\n", recv_msg);

        // Process data and prepare reply
        snprintf(reply_msg, BUFFER_SIZE, "ACK from System 2 (Host: %s): Data received and processed successfully.", processor_name);

        printf("[System 2 | Rank 1] Sending reply back to System 1...\n");

        // Blocking Send reply back to System 1 (Rank 0)
        MPI_Send(reply_msg, (int)strlen(reply_msg) + 1, MPI_CHAR, 0, TAG_ACK, MPI_COMM_WORLD);

        printf("[System 2 | Rank 1] Reply sent successfully.\n");
    }

    // Finalize the MPI execution environment
    MPI_Finalize();
    return 0;
}
