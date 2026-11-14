"""
Program: mpi_exchange.py
Description: Python MPI implementation using mpi4py to exchange data
             between System 1 (Rank 0) and System 2 (Rank 1).
Architecture: Two independent CPU systems connected via a network.

Requirements:
    pip install mpi4py numpy
Execution:
    mpiexec -n 2 python mpi_exchange.py
    (or with hostfile across 2 machines: mpiexec -n 2 -f hosts.txt python mpi_exchange.py)
"""

import socket
import time
from mpi4py import MPI
import numpy as np

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = socket.gethostname()

    if size != 2:
        if rank == 0:
            print("Error: This script must be run with 2 processes.")
            print("Usage: mpiexec -n 2 python mpi_exchange.py")
        return

    print(f"[System {rank + 1} | Rank {rank} | Host: {hostname}] Process initialized.")
    comm.Barrier()  # Synchronize both systems before starting

    # -------------------------------------------------------------
    # 1. Point-to-Point Communication (Python Dictionaries / Objects)
    # -------------------------------------------------------------
    if rank == 0:
        # System 1 prepares structured dictionary data
        outbound_data = {
            "origin": "System 1",
            "host": hostname,
            "timestamp": time.time(),
            "payload": [10, 20, 30, 40, 50],
            "status": "OPERATIONAL"
        }
        print(f"\n[System 1] Sending dictionary to System 2: {outbound_data}")
        comm.send(outbound_data, dest=1, tag=11)

        # Receive reply
        reply = comm.recv(source=1, tag=12)
        print(f"[System 1] Received response from System 2: {reply}\n")

    elif rank == 1:
        # System 2 receives dictionary
        incoming_data = comm.recv(source=0, tag=11)
        print(f"[System 2] Received data from System 1: {incoming_data}")

        # Send response
        reply_data = {
            "origin": "System 2",
            "host": hostname,
            "ack": True,
            "processed_items": len(incoming_data["payload"]),
            "message": "Data processed successfully by CPU on System 2"
        }
        print(f"[System 2] Sending ACK to System 1...")
        comm.send(reply_data, dest=0, tag=12)

    comm.Barrier()

    # -------------------------------------------------------------
    # 2. Fast Contiguous Buffer Exchange (NumPy Array)
    # -------------------------------------------------------------
    N = 100000
    if rank == 0:
        # System 1 prepares a float64 array
        send_buf = np.arange(N, dtype=np.float64)
        recv_buf = np.empty(N, dtype=np.float64)

        print(f"[System 1] Exchanging {N} NumPy float64 elements with System 2 via Sendrecv...")
        t0 = time.perf_counter()
        comm.Sendrecv(sendbuf=send_buf, dest=1, sendtag=21,
                      recvbuf=recv_buf, source=1, recvtag=22)
        t1 = time.perf_counter()

        print(f"[System 1] Exchange completed in {(t1 - t0)*1000:.3f} ms.")
        print(f"[System 1] Received array sample: first={recv_buf[0]}, last={recv_buf[-1]}")

    elif rank == 1:
        # System 2 prepares a negative float64 array
        send_buf = -np.arange(N, dtype=np.float64)
        recv_buf = np.empty(N, dtype=np.float64)

        print(f"[System 2] Exchanging {N} NumPy float64 elements with System 1 via Sendrecv...")
        comm.Sendrecv(sendbuf=send_buf, dest=0, sendtag=22,
                      recvbuf=recv_buf, source=0, recvtag=21)
        print(f"[System 2] Received array sample: first={recv_buf[0]}, last={recv_buf[-1]}")

if __name__ == "__main__":
    main()
