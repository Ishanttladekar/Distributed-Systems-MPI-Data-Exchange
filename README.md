# Parallel Data Exchange Between Two Systems Using MPI

This project provides parallel programs written in C (and Python) using the **Message Passing Interface (MPI)** to exchange data between two networked computer systems (**System 1** and **System 2**), each equipped with its own CPU and dedicated memory.

---

## 1. System Architecture & Communication Model

```
+------------------------------------+           +------------------------------------+
|             SYSTEM 1               |           |             SYSTEM 2               |
|  +------------------------------+  |           |  +------------------------------+  |
|  |             CPU              |  |           |  |             CPU              |  |
|  +------------------------------+  |           |  +------------------------------+  |
|  |     Private System Memory    |  |           |  |     Private System Memory    |  |
|  |    (MPI Rank 0 / Master)     |  |           |  |    (MPI Rank 1 / Worker)     |  |
|  +------------------------------+  |           |  +------------------------------+  |
|  |        Network Interface     |  |           |  |        Network Interface     |  |
+--+---------------|-----------------+           +--+---------------|-----------------+
                   |                                                |
                   +=================== ETHERNET / IP ==============+
                                  (TCP/IP / InfiniBand)
```

In distributed-memory architectures, CPUs cannot access each other's physical RAM directly. Instead, all data exchange occurs via explicit network message packets orchestrated by the MPI runtime:
- **System 1 (Process Rank 0)**: Initiates communication, coordinates tasks, or exchanges datasets.
- **System 2 (Process Rank 1)**: Receives, processes on its local CPU, and returns results or synchronizes.

---

## 2. Program Catalog

| File | Protocol / Pattern | Key MPI Functions | Purpose |
| :--- | :--- | :--- | :--- |
| [`01_basic_exchange.c`](file:///d:/DS1/01_basic_exchange.c) | Blocking Point-to-Point | `MPI_Send`, `MPI_Recv` | Ping-Pong message exchange and acknowledgment between System 1 and System 2. |
| [`02_deadlock_free_exchange.c`](file:///d:/DS1/02_deadlock_free_exchange.c) | Simultaneous Exchange | `MPI_Sendrecv` | Bidirectional data exchange avoiding network buffer deadlock. |
| [`03_nonblocking_exchange.c`](file:///d:/DS1/03_nonblocking_exchange.c) | Asynchronous / Overlapped | `MPI_Isend`, `MPI_Irecv`, `MPI_Waitall` | Overlaps CPU computation while data travels across the network. |
| [`04_array_computation_exchange.c`](file:///d:/DS1/04_array_computation_exchange.c) | Distributed Workload | `MPI_Send`, `MPI_Recv`, `MPI_Wtime` | Distributes an array across both CPUs, computes partial sums in parallel, and aggregates. |
| [`mpi_exchange.py`](file:///d:/DS1/mpi_exchange.py) | Python (mpi4py) | `comm.send`, `comm.recv`, `comm.Sendrecv` | Python implementation handling Python dicts and fast contiguous NumPy buffers. |

---

## 3. Network Environment Configuration

To run MPI across two physically distinct computers over a network:

### A. Network & IP Setup
1. Connect System 1 and System 2 to the same local area network (LAN / Wi-Fi / Switch).
2. Note their IP addresses:
   - System 1: e.g., `192.168.1.10`
   - System 2: e.g., `192.168.1.11`
3. Verify connectivity using ping:
   ```bash
   ping 192.168.1.11
   ```

### B. Linux / WSL / macOS (OpenMPI / MPICH)
1. **Install MPI**:
   ```bash
   sudo apt update
   sudo apt install mpich libmpich-dev    # Or: openmpi-bin libopenmpi-dev
   ```
2. **Passwordless SSH (from System 1 to System 2)**:
   MPI spawns processes on remote nodes via SSH:
   ```bash
   ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
   ssh-copy-id user@192.168.1.11
   ssh user@192.168.1.11  # Confirm you can log in without entering a password
   ```
3. **Synchronize Binary**:
   Ensure the compiled binary exists at the identical path on both systems (e.g. `/home/user/DS1/01_basic_exchange`) or use an NFS shared folder.
4. **Configure `hosts.txt`**:
   ```text
   192.168.1.10 slots=1
   192.168.1.11 slots=1
   ```

### C. Windows (Microsoft MPI)
1. Install **MS-MPI v10+** (both `msmpisetup.exe` and `msmpisdk.msi`) on both systems.
2. Start the SMPD service on both systems:
   ```powershell
   smpd -d
   ```
3. Run across machines:
   ```powershell
   mpiexec -hosts 2 192.168.1.10 1 192.168.1.11 1 01_basic_exchange.exe
   ```

---

## 4. Build and Execution Instructions

### Using Linux / WSL / macOS:
```bash
# 1. Compile all programs
make

# 2. Run locally (simulating two processes on the current CPU)
make run-local

# 3. Run across two network systems using the hostfile
mpirun -np 2 --hostfile hosts.txt ./01_basic_exchange
mpirun -np 2 --hostfile hosts.txt ./02_deadlock_free_exchange
mpirun -np 2 --hostfile hosts.txt ./03_nonblocking_exchange
mpirun -np 2 --hostfile hosts.txt ./04_array_computation_exchange
```

### Using Windows:
```cmd
:: Compile using the provided batch script (supports MSVC or MinGW GCC)
compile_windows.bat

:: Execute locally
mpiexec -n 2 01_basic_exchange.exe

:: Execute across System 1 and System 2 over the network
mpiexec -hosts 2 192.168.1.10 1 192.168.1.11 1 01_basic_exchange.exe
```

### Using Python (`mpi4py`):
```bash
pip install mpi4py numpy
mpiexec -n 2 python mpi_exchange.py
```

---

## 5. Visual Screenshots & Execution Results

All screenshots are stored in the [`screenshots/`](file:///d:/DS1/screenshots/) directory for direct inclusion in reports and submissions:

| Deliverable | Description | File Link |
| :--- | :--- | :--- |
| **System Architecture** | Physical layout of System 1 and System 2 with CPUs, private RAM, and Network Interconnect | [`00_system_architecture_diagram.png`](file:///d:/DS1/screenshots/00_system_architecture_diagram.png) |
| **Code Implementation** | Syntax-highlighted C code implementation of MPI communication | [`05_code_implementation_vscode.png`](file:///d:/DS1/screenshots/05_code_implementation_vscode.png) |
| **Basic Point-to-Point** | Compilation and execution output of blocking data send/receive & ACK | [`01_basic_exchange_execution.png`](file:///d:/DS1/screenshots/01_basic_exchange_execution.png) |
| **Deadlock-Free Exchange** | Atomic bidirectional data exchange using `MPI_Sendrecv` | [`02_deadlock_free_exchange_execution.png`](file:///d:/DS1/screenshots/02_deadlock_free_exchange_execution.png) |
| **Non-blocking Asynchronous** | Overlapping CPU computation while transmitting 1,000,000 elements | [`03_nonblocking_exchange_execution.png`](file:///d:/DS1/screenshots/03_nonblocking_exchange_execution.png) |
| **Distributed Array Workload** | Workload partitioning, parallel CPU execution, and sum aggregation | [`04_array_computation_execution.png`](file:///d:/DS1/screenshots/04_array_computation_execution.png) |

---

## 6. Sample Execution Logs

### `01_basic_exchange`
```
=======================================================
[System 1 | Rank 0 | Node: node-alpha] Initialized.
[System 1 | Rank 0] Sending message to System 2: "Hello from System 1 (Host: node-alpha, CPU Core Active)"
[System 1 | Rank 0] Message sent. Waiting for response from System 2...
[System 2 | Rank 1 | Node: node-beta] Initialized. Waiting for data from System 1...
[System 2 | Rank 1] Received data from System 1: "Hello from System 1 (Host: node-alpha, CPU Core Active)"
[System 2 | Rank 1] Sending reply back to System 1...
[System 2 | Rank 1] Reply sent successfully.
[System 1 | Rank 0] Received acknowledgment from System 2: "ACK from System 2 (Host: node-beta): Data received and processed successfully."
=======================================================
```

### `04_array_computation_exchange`
```
====================================================================
Distributed Data Processing between System 1 and System 2
Total Elements: 1000000 (System 1: 500000, System 2: 500000)
====================================================================

[System 1 | Host: node-alpha] Sending 500000 elements to System 2 over network...
[System 1 | Host: node-alpha] Computing partial sum for elements 0 to 499999 on local CPU...
[System 1 | Host: node-alpha] Local partial sum: 500000.00
[System 2 | Host: node-beta] Awaiting 500000 elements from System 1...
[System 2 | Host: node-beta] Workload received. Computing partial sum on local CPU...
[System 2 | Host: node-beta] Computed partial sum: 500000.00. Sending back to System 1...
[System 1 | Host: node-alpha] Received partial sum from System 2: 500000.00

--------------------------------------------------------------------
FINAL RESULT:
Total Accumulated Sum : 1000000.00 (Expected: 1000000.00)
Total Execution Time   : 0.003421 seconds
--------------------------------------------------------------------
```
