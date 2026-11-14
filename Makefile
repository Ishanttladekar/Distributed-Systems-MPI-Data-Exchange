# Makefile for MPI Parallel Programs on System 1 and System 2
# Compiler and Flags
CC = mpicc
CFLAGS = -Wall -O3
LDFLAGS = -lm

# Targets
TARGETS = 01_basic_exchange 02_deadlock_free_exchange 03_nonblocking_exchange 04_array_computation_exchange

all: $(TARGETS)

01_basic_exchange: 01_basic_exchange.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

02_deadlock_free_exchange: 02_deadlock_free_exchange.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

03_nonblocking_exchange: 03_nonblocking_exchange.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

04_array_computation_exchange: 04_array_computation_exchange.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Local test execution (simulating both systems on local machine)
run-local: all
	@echo "=== Running 01_basic_exchange locally ==="
	mpirun -np 2 ./01_basic_exchange
	@echo "\n=== Running 02_deadlock_free_exchange locally ==="
	mpirun -np 2 ./02_deadlock_free_exchange
	@echo "\n=== Running 03_nonblocking_exchange locally ==="
	mpirun -np 2 ./03_nonblocking_exchange
	@echo "\n=== Running 04_array_computation_exchange locally ==="
	mpirun -np 2 ./04_array_computation_exchange

# Multi-host network execution (across System 1 and System 2)
run-network: all
	@echo "=== Running across System 1 and System 2 over network ==="
	mpirun -np 2 --hostfile hosts.txt ./01_basic_exchange

clean:
	rm -f $(TARGETS) *.o
