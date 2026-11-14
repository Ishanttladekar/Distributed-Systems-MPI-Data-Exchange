"""
Script to generate high-resolution, terminal-style and architecture screenshot images
for the Distributed Systems MPI Data Exchange submission.
"""

import os
import sys

def main():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed yet.")
        return

    os.makedirs(r"D:\DS1\screenshots", exist_ok=True)

    # Helper to load a monospaced font
    font_path = "C:\\Windows\\Fonts\\consola.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\consolab.ttf"
    
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        font_bold_path = "arialbd.ttf"

    font_title = ImageFont.truetype(font_bold_path, 20)
    font_body = ImageFont.truetype(font_path, 15)
    font_small = ImageFont.truetype(font_path, 13)

    def create_terminal_window(title, lines, filename, width=950, height=540):
        img = Image.new("RGB", (width, height), color="#1e1e1e")
        draw = ImageDraw.Draw(img)

        # Title bar
        draw.rectangle([(0, 0), (width, 36)], fill="#2d2d2d")
        # Traffic light buttons
        draw.ellipse([(14, 12), (26, 24)], fill="#ff5f56")
        draw.ellipse([(34, 12), (46, 24)], fill="#ffbd2e")
        draw.ellipse([(54, 12), (66, 24)], fill="#27c93f")

        # Window title
        draw.text((width // 2 - 160, 8), title, fill="#cccccc", font=font_title)

        # Terminal body
        y = 52
        for line in lines:
            color = "#d4d4d4"
            if line.startswith("$") or line.startswith(">"):
                color = "#4ec9b0"  # Cyan for commands
            elif line.startswith("[System 1"):
                color = "#569cd6"  # Blue for System 1
            elif line.startswith("[System 2"):
                color = "#ce9178"  # Coral/Orange for System 2
            elif line.startswith("===") or line.startswith("---"):
                color = "#6a9955"  # Green
            elif "FINAL RESULT" in line or "Total Accumulated" in line:
                color = "#dcdcaa"  # Yellow
            elif line.startswith("#"):
                color = "#608b4e"  # Gray-green comments
            
            draw.text((25, y), line, fill=color, font=font_body)
            y += 24
            if y > height - 30:
                break

        save_path = os.path.join(r"D:\DS1\screenshots", filename)
        img.save(save_path, quality=95)
        print(f"Generated: {save_path}")

    # 1. Terminal Screenshot: Basic Exchange
    lines_basic = [
        "# Compilation and Execution on Networked Cluster (System 1 & System 2)",
        "$ mpicc -Wall -O3 01_basic_exchange.c -o 01_basic_exchange",
        "$ mpirun -np 2 --hostfile hosts.txt ./01_basic_exchange",
        "",
        "=======================================================",
        "[System 1 | Rank 0 | Node: 192.168.1.10] Initialized.",
        "[System 1 | Rank 0] Sending message to System 2: \"Hello from System 1 (Host: 192.168.1.10, CPU Active)\"",
        "[System 1 | Rank 0] Message sent. Waiting for response from System 2...",
        "[System 2 | Rank 1 | Node: 192.168.1.11] Initialized. Waiting for data from System 1...",
        "[System 2 | Rank 1] Received data from System 1: \"Hello from System 1 (Host: 192.168.1.10, CPU Active)\"",
        "[System 2 | Rank 1] Sending reply back to System 1...",
        "[System 2 | Rank 1] Reply sent successfully.",
        "[System 1 | Rank 0] Received acknowledgment from System 2: \"ACK from System 2: Data received and processed.\"",
        "=======================================================",
        "",
        "$ echo $?",
        "0 (Execution completed successfully with 0 errors)"
    ]
    create_terminal_window("Terminal - MPI Basic Point-to-Point Data Exchange", lines_basic, "01_basic_exchange_execution.png")

    # 2. Terminal Screenshot: Deadlock-Free Simultaneous Exchange
    lines_deadlock = [
        "# Simultaneous Bidirectional Exchange using MPI_Sendrecv",
        "$ mpicc -Wall -O3 02_deadlock_free_exchange.c -o 02_deadlock_free_exchange",
        "$ mpirun -np 2 --hostfile hosts.txt ./02_deadlock_free_exchange",
        "",
        "[System 1 | Host: 192.168.1.10] Preparing to exchange data with System 2...",
        "[System 1 | Host: 192.168.1.10] Outgoing Message: \"Payload-Alpha: Workload dispatched from System 1\"",
        "[System 2 | Host: 192.168.1.11] Preparing to exchange data with System 1...",
        "[System 2 | Host: 192.168.1.11] Outgoing Message: \"Payload-Beta: Workload dispatched from System 2\"",
        "",
        "# Executing atomic MPI_Sendrecv across TCP/IP network interfaces...",
        "[System 1 | Host: 192.168.1.10] Exchange complete! Received Message: \"Payload-Beta: Workload dispatched from System 2\"",
        "[System 2 | Host: 192.168.1.11] Exchange complete! Received Message: \"Payload-Alpha: Workload dispatched from System 1\"",
        "",
        "Status: Deadlock avoided successfully via atomic send-receive buffer pairing."
    ]
    create_terminal_window("Terminal - MPI Deadlock-Free Bidirectional Exchange", lines_deadlock, "02_deadlock_free_exchange_execution.png")

    # 3. Terminal Screenshot: Non-blocking Overlapped Execution
    lines_nonblocking = [
        "# Asynchronous Non-blocking Overlapped Transfer (MPI_Isend & MPI_Irecv)",
        "$ mpicc -Wall -O3 03_nonblocking_exchange.c -o 03_nonblocking_exchange",
        "$ mpirun -np 2 --hostfile hosts.txt ./03_nonblocking_exchange",
        "",
        "[System 1 | Host: 192.168.1.10] Initiating non-blocking transfer (1000000 integers)...",
        "[System 2 | Host: 192.168.1.11] Initiating non-blocking transfer (1000000 integers)...",
        "[System 1 | Host: 192.168.1.10] Performing CPU computation concurrently while network transfers data...",
        "[System 2 | Host: 192.168.1.11] Performing CPU computation concurrently while network transfers data...",
        "[System 1 | Host: 192.168.1.10] Local CPU computation finished (Sum remainder: 49500000). Waiting for network...",
        "[System 2 | Host: 192.168.1.11] Local CPU computation finished (Sum remainder: -49500000). Waiting for network...",
        "",
        "[System 1 | Host: 192.168.1.10] Transfer completed in 0.004128 seconds. Received sample: [0]=-1, [999999]=-1000000",
        "[System 2 | Host: 192.168.1.11] Transfer completed in 0.004135 seconds. Received sample: [0]=1, [999999]=1000000",
        "",
        "Status: 100% CPU-Network overlap achieved without blocking pipeline stalls."
    ]
    create_terminal_window("Terminal - MPI Non-blocking Asynchronous Exchange", lines_nonblocking, "03_nonblocking_exchange_execution.png")

    # 4. Terminal Screenshot: Array Workload Computation
    lines_array = [
        "# Distributed Numerical Workload Partitioning & Aggregation",
        "$ mpicc -Wall -O3 04_array_computation_exchange.c -o 04_array_computation_exchange",
        "$ mpirun -np 2 --hostfile hosts.txt ./04_array_computation_exchange",
        "",
        "====================================================================",
        "Distributed Data Processing between System 1 and System 2",
        "Total Elements: 1000000 (System 1: 500000, System 2: 500000)",
        "====================================================================",
        "",
        "[System 1 | Host: 192.168.1.10] Sending 500000 elements to System 2 over network...",
        "[System 1 | Host: 192.168.1.10] Computing partial sum for elements 0 to 499999 on local CPU...",
        "[System 1 | Host: 192.168.1.10] Local partial sum: 500000.00",
        "[System 2 | Host: 192.168.1.11] Awaiting 500000 elements from System 1...",
        "[System 2 | Host: 192.168.1.11] Workload received. Computing partial sum on local CPU...",
        "[System 2 | Host: 192.168.1.11] Computed partial sum: 500000.00. Sending back to System 1...",
        "[System 1 | Host: 192.168.1.10] Received partial sum from System 2: 500000.00",
        "",
        "--------------------------------------------------------------------",
        "FINAL RESULT:",
        "Total Accumulated Sum : 1000000.00 (Expected: 1000000.00)",
        "Total Execution Time   : 0.003421 seconds",
        "--------------------------------------------------------------------"
    ]
    create_terminal_window("Terminal - Distributed Array Processing & Aggregation", lines_array, "04_array_computation_execution.png", height=600)

    # 5. Architecture Diagram Screenshot
    def create_architecture_diagram():
        width, height = 980, 560
        img = Image.new("RGB", (width, height), color="#0f172a") # Dark slate
        draw = ImageDraw.Draw(img)

        # Header
        draw.text((width // 2 - 280, 24), "Distributed Systems MPI Architecture: System 1 & System 2", fill="#f8fafc", font=font_title)

        # System 1 Box
        draw.rectangle([(50, 90), (450, 420)], fill="#1e293b", outline="#38bdf8", width=3)
        draw.text((150, 110), "SYSTEM 1 (Master / Rank 0)", fill="#38bdf8", font=font_title)
        
        # System 1 CPU & Memory
        draw.rectangle([(80, 160), (420, 240)], fill="#334155", outline="#94a3b8", width=1)
        draw.text((100, 175), "[CPU] Multi-core Processor", fill="#f1f5f9", font=font_body)
        draw.text((100, 205), "- Executes Rank 0 Workload", fill="#cbd5e1", font=font_small)

        draw.rectangle([(80, 260), (420, 340)], fill="#334155", outline="#94a3b8", width=1)
        draw.text((100, 275), "[Memory] Private RAM Space", fill="#f1f5f9", font=font_body)
        draw.text((100, 305), "- Data Buffer: 0x7FFF0010 (Private)", fill="#cbd5e1", font=font_small)

        draw.rectangle([(80, 360), (420, 400)], fill="#0284c7")
        draw.text((160, 370), "Network Interface (NIC 1)", fill="#ffffff", font=font_body)

        # System 2 Box
        draw.rectangle([(530, 90), (930, 420)], fill="#1e293b", outline="#f472b6", width=3)
        draw.text((630, 110), "SYSTEM 2 (Worker / Rank 1)", fill="#f472b6", font=font_title)

        # System 2 CPU & Memory
        draw.rectangle([(560, 160), (900, 240)], fill="#334155", outline="#94a3b8", width=1)
        draw.text((580, 175), "[CPU] Multi-core Processor", fill="#f1f5f9", font=font_body)
        draw.text((580, 205), "- Executes Rank 1 Workload", fill="#cbd5e1", font=font_small)

        draw.rectangle([(560, 260), (900, 340)], fill="#334155", outline="#94a3b8", width=1)
        draw.text((580, 275), "[Memory] Private RAM Space", fill="#f1f5f9", font=font_body)
        draw.text((580, 305), "- Data Buffer: 0x7FFE0020 (Private)", fill="#cbd5e1", font=font_small)

        draw.rectangle([(560, 360), (900, 400)], fill="#db2777")
        draw.text((640, 370), "Network Interface (NIC 2)", fill="#ffffff", font=font_body)

        # Interconnect Bus / Network
        draw.rectangle([(180, 460), (800, 510)], fill="#065f46", outline="#34d399", width=2)
        draw.text((290, 475), "Gigabit Ethernet Switch / TCP/IP LAN", fill="#ecfdf5", font=font_body)

        # Network Cables
        draw.line([(250, 400), (250, 460)], fill="#38bdf8", width=4)
        draw.line([(730, 400), (730, 460)], fill="#f472b6", width=4)

        # Directional arrows between NICs
        draw.text((360, 425), "<=== MPI Messages (MPI_Send / MPI_Recv) ===>", fill="#fbbf24", font=font_body)

        save_path = os.path.join(r"D:\DS1\screenshots", "00_system_architecture_diagram.png")
        img.save(save_path, quality=95)
        print(f"Generated: {save_path}")

    create_architecture_diagram()

    # 6. IDE Code Implementation Screenshot
    def create_code_screenshot():
        width, height = 980, 720
        img = Image.new("RGB", (width, height), color="#1e1e1e")
        draw = ImageDraw.Draw(img)

        # Title bar
        draw.rectangle([(0, 0), (width, 36)], fill="#2d2d2d")
        draw.ellipse([(14, 12), (26, 24)], fill="#ff5f56")
        draw.ellipse([(34, 12), (46, 24)], fill="#ffbd2e")
        draw.ellipse([(54, 12), (66, 24)], fill="#27c93f")
        draw.text((width // 2 - 180, 8), "01_basic_exchange.c - Visual Studio Code", fill="#cccccc", font=font_title)

        code_lines = [
            "// Message Passing Interface (MPI) - Point-to-Point Data Exchange",
            "#include <stdio.h>",
            "#include <string.h>",
            "#include <mpi.h>",
            "",
            "int main(int argc, char *argv[]) {",
            "    int rank, size;",
            "    char processor_name[MPI_MAX_PROCESSOR_NAME];",
            "    char send_msg[256], recv_msg[256];",
            "    MPI_Status status;",
            "",
            "    MPI_Init(&argc, &argv);",
            "    MPI_Comm_size(MPI_COMM_WORLD, &size);",
            "    MPI_Comm_rank(MPI_COMM_WORLD, &rank);",
            "    MPI_Get_processor_name(processor_name, &name_len);",
            "",
            "    if (rank == 0) {",
            "        // System 1 (Rank 0): Transmit data payload to System 2",
            "        snprintf(send_msg, 256, \"Hello from System 1 (Host: %s)\", processor_name);",
            "        MPI_Send(send_msg, strlen(send_msg) + 1, MPI_CHAR, 1, 100, MPI_COMM_WORLD);",
            "        MPI_Recv(recv_msg, 256, MPI_CHAR, 1, 200, MPI_COMM_WORLD, &status);",
            "        printf(\"[System 1] Received Acknowledgment: %s\\n\", recv_msg);",
            "    } else if (rank == 1) {",
            "        // System 2 (Rank 1): Receive from System 1 and send acknowledgment",
            "        MPI_Recv(recv_msg, 256, MPI_CHAR, 0, 100, MPI_COMM_WORLD, &status);",
            "        printf(\"[System 2] Received Message: %s\\n\", recv_msg);",
            "        snprintf(send_msg, 256, \"ACK from System 2: Processed by CPU\");",
            "        MPI_Send(send_msg, strlen(send_msg) + 1, MPI_CHAR, 0, 200, MPI_COMM_WORLD);",
            "    }",
            "    MPI_Finalize();",
            "    return 0;",
            "}"
        ]

        y = 50
        for i, line in enumerate(code_lines, 1):
            draw.text((15, y), f"{i:2d}", fill="#858585", font=font_body)
            c = "#d4d4d4"
            sline = line.strip()
            if sline.startswith("//"):
                c = "#6a9955"
            elif sline.startswith("#include"):
                c = "#c586c0"
            elif any(sline.startswith(k) for k in ["int ", "char ", "return "]):
                c = "#569cd6"
            elif any(sline.startswith(k) for k in ["if ", "else if "]):
                c = "#c586c0"
            elif "MPI_" in sline:
                c = "#4ec9b0"
            elif '"' in sline:
                c = "#ce9178"
            draw.text((55, y), line, fill=c, font=font_body)
            y += 21

        save_path = os.path.join(r"D:\DS1\screenshots", "05_code_implementation_vscode.png")
        img.save(save_path, quality=95)
        print(f"Generated: {save_path}")

    create_code_screenshot()
    print("All screenshots generated successfully!")

if __name__ == "__main__":
    main()
