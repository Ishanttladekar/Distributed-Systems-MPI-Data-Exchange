/*
 * Program: 02_deadlock_free_exchange.c
 * Description: Simultaneous bidirectional data exchange between System 1 and System 2
 *              using MPI_Sendrecv to prevent communication deadlock.
 * Architecture: Two independent CPU systems connected via a network.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

#define BUFFER_SIZE 256
#define TAG_EXCHANGE 300

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
            fprintf(stderr, "Error: This program must be run with exactly 2 processes.\n");
            fprintf(stderr, "Usage: mpirun -np 2 ./02_deadlock_free_exchange\n");
        }
        MPI_Finalize();
        return 1;
    }

    char send_buffer[BUFFER_SIZE];
    char recv_buffer[BUFFER_SIZE];
    MPI_Status status;
    int partner_rank = (rank == 0) ? 1 : 0;

    // Both systems prepare their outgoing payload
    if (rank == 0) {
        snprintf(send_buffer, BUFFER_SIZE, "Payload-Alpha: Workload dispatched from System 1 (%s)", processor_name);
    } else {
        snprintf(send_buffer, BUFFER_SIZE, "Payload-Beta: Workload dispatched from System 2 (%s)", processor_name);
    }

    printf("[System %d | Host: %s] Preparing to exchange data with System %d...\n", 
           rank + 1, processor_name, partner_rank + 1);
    printf("[System %d | Host: %s] Outgoing Message: \"%s\"\n", 
           rank + 1, processor_name, send_buffer);

    /*
     * MPI_Sendrecv executes both send and receive atomically.
     * Arguments:
     *   sendbuf, sendcount, sendtype, dest,   sendtag,
     *   recvbuf, recvcount, recvtype, source, recvtag,
     *   comm,    status
     *
     * This avoids deadlocks that happen when both processes attempt a blocking
     * MPI_Send simultaneously before entering MPI_Recv.
     */
    MPI_Sendrecv(send_buffer, (int)strlen(send_buffer) + 1, MPI_CHAR, partner_rank, TAG_EXCHANGE,
                 recv_buffer, BUFFER_SIZE,                 MPI_CHAR, partner_rank, TAG_EXCHANGE,
                 MPI_COMM_WORLD, &status);

    printf("[System %d | Host: %s] Exchange complete! Received Message: \"%s\"\n", 
           rank + 1, processor_name, recv_buffer);

    MPI_Finalize();
    return 0;
}
