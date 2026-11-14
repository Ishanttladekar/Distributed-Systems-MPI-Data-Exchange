# Practical / Assignment Report: Distributed Systems

**Course:** Distributed Systems Lab (Sem 7)  
**Topic:** Inter-Process Communication & Data Exchange Using Message Passing Interface (MPI)  
**Student Name:** Ishant Ladekar  
**Roll No:** [Your Roll No]  
**Repository Link:** https://github.com/Ishanttladekar/Distributed-Systems-MPI-Data-Exchange  
**Date of Submission:** November 2026  

---

## 1. Aim / Objective
To design and develop parallel programs using the Message Passing Interface (MPI) to exchange data across two networked computer systems (**System 1** and **System 2**), each equipped with its own CPU and dedicated memory.

---

## 2. Hardware and Software Specifications
- **Hardware:**
  - System 1 (Node 1 / Master): CPU with dedicated physical RAM and Network Interface Card (NIC).
  - System 2 (Node 2 / Worker): CPU with dedicated physical RAM and Network Interface Card (NIC).
  - Network Interconnect: High-speed TCP/IP Local Area Network (LAN / Ethernet).
- **Software:**
  - Operating System: Linux (Ubuntu/WSL) / Windows
  - MPI Standard Implementations: OpenMPI / MPICH / Microsoft MPI (MS-MPI)
  - Compiler: GCC (`mpicc`) / MSVC (`cl.exe`)
  - Python Environment: Python 3 with `mpi4py` and `numpy`
  - Version Control: Git & GitHub

---

## 3. Distributed Architecture & Theory

In a distributed memory parallel architecture:
1. **Private Memory Boundaries:** Unlike multi-threading in shared memory, each system has a private physical address space. System 1's CPU cannot directly read from or write to System 2's RAM.
2. **Explicit Message Passing:** All information sharing and synchronization occur via discrete network packets formatted according to the MPI standard.
3. **Communicator & Ranks:** In `MPI_COMM_WORLD`:
   - System 1 is assigned **Rank 0** (acts as coordinator/initiator).
   - System 2 is assigned **Rank 1** (acts as participant/worker).
4. **Key Communication Paradigms Implemented:**
   - **Blocking Point-to-Point (`MPI_Send`, `MPI_Recv`):** Synchronous transmission where the sender halts until the buffer is safely stored or transmitted.
   - **Deadlock-Free Bidirectional Exchange (`MPI_Sendrecv`):** Executes simultaneous send and receive operations atomically, eliminating buffer-exhaustion deadlocks.
   - **Non-blocking / Asynchronous (`MPI_Isend`, `MPI_Irecv`, `MPI_Waitall`):** Decouples data transfer from CPU computation, permitting 100% overlap of computation and network communication.
   - **Distributed Array Partitioning:** Workload parallelization where a large vector is partitioned across both nodes, processed on respective CPUs, and aggregated.

```
+------------------------------------+           +------------------------------------+
|             SYSTEM 1               |           |             SYSTEM 2               |
|  +------------------------------+  |           |  +------------------------------+  |
|  |             CPU              |  |           |  |             CPU              |  |
|  +------------------------------+  |           |  +------------------------------+  |
|  |     Private System Memory    |  |           |  |     Private System Memory    |  |
|  |    (MPI Rank 0 / Master)     |  |           |  |    (MPI Rank 1 / Worker)     |  |
|  +------------------------------+  |           |  +------------------------------+  |
|  |      Network Interface       |  |           |  |      Network Interface       |  |
+--+---------------|-----------------+           +--+---------------|-----------------+
                   |                                                |
                   +================== NETWORK (TCP/IP) ============+
```

---

## 4. Communication Flowchart

```
                [SYSTEM 1 (Rank 0)]                        [SYSTEM 2 (Rank 1)]
                         |                                          |
                         v                                          v
                   MPI_Init()                                 MPI_Init()
                         |                                          |
           Prepare Data Buffer to Send                      Wait for Network Packet
                         |                                          |
               MPI_Send(Data -> Rank 1) ===================> MPI_Recv(from Rank 0)
                         |                                          |
               Wait for Acknowledgment                       Process Data on CPU
                         |                                          |
             MPI_Recv(from Rank 1) <=================== MPI_Send(ACK -> Rank 0)
                         |                                          |
             Print Received ACK / Data                     Print Completion Status
                         |                                          |
                   MPI_Finalize()                             MPI_Finalize()
                         |                                          |
                        END                                        END
```

---

## 5. Complete Source Code

### Program 1: Basic Point-to-Point Blocking Data Exchange (`01_basic_exchange.c`)
```c
/*
 * Program: 01_basic_exchange.c
 * Description: Point-to-Point data exchange between System 1 (Rank 0) and System 2 (Rank 1)
 *              using blocking MPI_Send and MPI_Recv.
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

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Get_processor_name(processor_name, &name_len);

    if (size != 2) {
        if (rank == 0) {
            fprintf(stderr, "Error: This program must be run with exactly 2 processes.\n");
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

        snprintf(reply_msg, BUFFER_SIZE, "ACK from System 2 (Host: %s): Data received and processed successfully.", processor_name);

        printf("[System 2 | Rank 1] Sending reply back to System 1...\n");

        // Blocking Send reply back to System 1 (Rank 0)
        MPI_Send(reply_msg, (int)strlen(reply_msg) + 1, MPI_CHAR, 0, TAG_ACK, MPI_COMM_WORLD);

        printf("[System 2 | Rank 1] Reply sent successfully.\n");
    }

    MPI_Finalize();
    return 0;
}
```

---

### Program 2: Deadlock-Free Bidirectional Simultaneous Exchange (`02_deadlock_free_exchange.c`)
```c
/*
 * Program: 02_deadlock_free_exchange.c
 * Description: Simultaneous bidirectional data exchange between System 1 and System 2
 *              using MPI_Sendrecv to prevent communication deadlock.
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
        }
        MPI_Finalize();
        return 1;
    }

    char send_buffer[BUFFER_SIZE];
    char recv_buffer[BUFFER_SIZE];
    MPI_Status status;
    int partner_rank = (rank == 0) ? 1 : 0;

    if (rank == 0) {
        snprintf(send_buffer, BUFFER_SIZE, "Payload-Alpha: Workload dispatched from System 1 (%s)", processor_name);
    } else {
        snprintf(send_buffer, BUFFER_SIZE, "Payload-Beta: Workload dispatched from System 2 (%s)", processor_name);
    }

    printf("[System %d | Host: %s] Outgoing Message: \"%s\"\n", rank + 1, processor_name, send_buffer);

    // Atomic bidirectional exchange avoiding circular wait deadlock
    MPI_Sendrecv(send_buffer, (int)strlen(send_buffer) + 1, MPI_CHAR, partner_rank, TAG_EXCHANGE,
                 recv_buffer, BUFFER_SIZE,                 MPI_CHAR, partner_rank, TAG_EXCHANGE,
                 MPI_COMM_WORLD, &status);

    printf("[System %d | Host: %s] Exchange complete! Received Message: \"%s\"\n", rank + 1, processor_name, recv_buffer);

    MPI_Finalize();
    return 0;
}
```

---

### Program 3: Non-blocking Asynchronous Communication (`03_nonblocking_exchange.c`)
```c
/*
 * Program: 03_nonblocking_exchange.c
 * Description: Overlapping computation with network transfer using MPI_Isend and MPI_Irecv.
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
        MPI_Finalize();
        return 1;
    }

    int partner = (rank == 0) ? 1 : 0;
    int *send_array = (int *)malloc(sizeof(int) * ARRAY_SIZE);
    int *recv_array = (int *)malloc(sizeof(int) * ARRAY_SIZE);

    for (int i = 0; i < ARRAY_SIZE; i++) {
        send_array[i] = (rank == 0) ? (i + 1) : -(i + 1);
    }

    MPI_Request requests[2];
    MPI_Status statuses[2];
    double start_time = MPI_Wtime();

    // 1. Post non-blocking receive and send
    MPI_Irecv(recv_array, ARRAY_SIZE, MPI_INT, partner, 10, MPI_COMM_WORLD, &requests[0]);
    MPI_Isend(send_array, ARRAY_SIZE, MPI_INT, partner, 10, MPI_COMM_WORLD, &requests[1]);

    // 2. Overlapping CPU computation while data travels across network
    long long local_sum = 0;
    for (int i = 0; i < ARRAY_SIZE; i++) {
        local_sum += (send_array[i] % 100);
    }

    // 3. Wait for network transfer to finish
    MPI_Waitall(2, requests, statuses);
    double end_time = MPI_Wtime();

    printf("[System %d | Host: %s] Transfer completed in %.6f seconds. Received: [0]=%d, [%d]=%d\n",
           rank + 1, processor_name, end_time - start_time, recv_array[0], ARRAY_SIZE - 1, recv_array[ARRAY_SIZE - 1]);

    free(send_array);
    free(recv_array);
    MPI_Finalize();
    return 0;
}
```

---

### Program 4: Distributed Array Computation & Aggregation (`04_array_computation_exchange.c`)
```c
/*
 * Program: 04_array_computation_exchange.c
 * Description: Partitioning a 1,000,000 element array across System 1 and System 2,
 *              computing partial sums on each CPU, and aggregating results.
 */

#include <stdio.h>
#include <stdlib.h>
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
        MPI_Finalize();
        return 1;
    }

    int half_size = TOTAL_ELEMENTS / 2;
    double *data_buffer = NULL;
    double local_sum = 0.0;
    double start_time, end_time;

    if (rank == 0) {
        data_buffer = (double *)malloc(sizeof(double) * TOTAL_ELEMENTS);
        for (int i = 0; i < TOTAL_ELEMENTS; i++) data_buffer[i] = 1.0;

        start_time = MPI_Wtime();

        // Send second half to System 2 over network
        MPI_Send(&data_buffer[half_size], half_size, MPI_DOUBLE, 1, 50, MPI_COMM_WORLD);

        // System 1 CPU computes its first half
        for (int i = 0; i < half_size; i++) local_sum += data_buffer[i];

        // Receive partial sum from System 2
        double system2_sum = 0.0;
        MPI_Status status;
        MPI_Recv(&system2_sum, 1, MPI_DOUBLE, 1, 51, MPI_COMM_WORLD, &status);

        double total_sum = local_sum + system2_sum;
        end_time = MPI_Wtime();

        printf("Distributed Aggregation Result:\n");
        printf("Total Sum: %.2f (Expected: %.2f) | Time: %.6f s\n", total_sum, (double)TOTAL_ELEMENTS, end_time - start_time);
        free(data_buffer);

    } else if (rank == 1) {
        data_buffer = (double *)malloc(sizeof(double) * half_size);
        MPI_Status status;

        // Receive workload from System 1
        MPI_Recv(data_buffer, half_size, MPI_DOUBLE, 0, 50, MPI_COMM_WORLD, &status);

        // System 2 CPU computes its assigned half
        for (int i = 0; i < half_size; i++) local_sum += data_buffer[i];

        // Send partial sum back to System 1
        MPI_Send(&local_sum, 1, MPI_DOUBLE, 0, 51, MPI_COMM_WORLD);
        free(data_buffer);
    }

    MPI_Finalize();
    return 0;
}
```

---

## 6. Step-by-Step Instructions: Setup, Running, and Testing

### A. Network Setup
1. Configure both systems on the same subnet (e.g. `192.168.1.10` and `192.168.1.11`).
2. Verify communication using `ping 192.168.1.11`.
3. Configure passwordless SSH from System 1 to System 2:
   ```bash
   ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
   ssh-copy-id user@192.168.1.11
   ```

### B. Machinefile Configuration (`hosts.txt`)
Create a file named `hosts.txt`:
```text
192.168.1.10 slots=1
192.168.1.11 slots=1
```

### C. Compilation
```bash
# Using Makefile:
make

# Or manually using mpicc:
mpicc -Wall -O3 -o 01_basic_exchange 01_basic_exchange.c
mpicc -Wall -O3 -o 02_deadlock_free_exchange 02_deadlock_free_exchange.c
mpicc -Wall -O3 -o 03_nonblocking_exchange 03_nonblocking_exchange.c
mpicc -Wall -O3 -o 04_array_computation_exchange 04_array_computation_exchange.c
```

### D. Testing & Execution
```bash
# 1. Local Verification (both processes on 1 host for initial debugging):
mpirun -np 2 ./01_basic_exchange

# 2. Network Cluster Execution across System 1 and System 2:
mpirun -np 2 --hostfile hosts.txt ./01_basic_exchange
mpirun -np 2 --hostfile hosts.txt ./02_deadlock_free_exchange
mpirun -np 2 --hostfile hosts.txt ./03_nonblocking_exchange
mpirun -np 2 --hostfile hosts.txt ./04_array_computation_exchange
```

---

## 7. Execution Screenshots and Logs

All screenshots are located in the `screenshots/` directory:

1. **System Architecture Diagram:**  
   `screenshots/00_system_architecture_diagram.png`
2. **Code Implementation in IDE:**  
   `screenshots/05_code_implementation_vscode.png`
3. **Execution 1: Point-to-Point Message Exchange:**  
   `screenshots/01_basic_exchange_execution.png`
4. **Execution 2: Deadlock-Free Bidirectional Exchange:**  
   `screenshots/02_deadlock_free_exchange_execution.png`
5. **Execution 3: Asynchronous Non-blocking Execution:**  
   `screenshots/03_nonblocking_exchange_execution.png`
6. **Execution 4: Distributed Array Computation & Aggregation:**  
   `screenshots/04_array_computation_execution.png`

---

## 8. Conclusion
The Message Passing Interface (MPI) parallel programs were successfully developed and tested to exchange data between System 1 and System 2. The solution demonstrated synchronous point-to-point communication, atomic deadlock-free bidirectional data exchange, non-blocking asynchronous overlap between CPU execution and network transfer, and distributed parallel computation with aggregation.
