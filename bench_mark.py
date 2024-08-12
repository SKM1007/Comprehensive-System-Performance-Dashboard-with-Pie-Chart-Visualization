import os
import platform
import subprocess
import re
import time
import matplotlib.pyplot as plt

def single_core_task():
    result = 0
    for _ in range(1, 1000000):
        result += 1
    return result

def multi_core_task():
    results = []
    for _ in range(4):
        t = time.time()
        single_core_task()
        results.append(time.time() - t)
    return max(results)  # Use the longest execution time as the score

def get_system_info():
    system_info = {
        "Operating System": platform.system(),
        "OS Version": platform.release(),
        "Architecture": platform.architecture(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
    }
    return system_info

def get_cpu_info():
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output("wmic cpu get Name, NumberOfCores, NumberOfLogicalProcessors /format:list", shell=True).decode("utf-8")
            cpu_info = {}
            for line in result.strip().split('\n'):
                if "=" in line:
                    key, value = line.split("=", 1)
                    cpu_info[key.strip()] = value.strip()
            return cpu_info
        except Exception:
            return {"Error": "Failed to retrieve CPU information."}
    elif platform.system() == "Linux":
        try:
            result = subprocess.check_output("lscpu", shell=True).decode("utf-8")
            cpu_info = {}
            for line in result.strip().split('\n'):
                if ":" in line:
                    key, value = line.split(":", 1)
                    cpu_info[key.strip()] = value.strip()
            return cpu_info
        except Exception:
            return {"Error": "Failed to retrieve CPU information."}
    return {"Error": "Unsupported OS for CPU info retrieval."}

def get_memory_info():
    memory_info = {}
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("wmic memorychip get Capacity", shell=True).decode("utf-8")
            total_memory = sum([int(capacity) for capacity in result.strip().split('\n')[1:] if capacity.isdigit()])
            memory_info["Total Memory (GB)"] = total_memory / (1024 ** 3)
        elif platform.system() == "Linux":
            result = subprocess.check_output("free -g", shell=True).decode("utf-8")
            lines = result.strip().split("\n")
            columns = lines[0].split()
            values = lines[1].split()
            for i in range(len(columns)):
                if columns[i] == "total":
                    memory_info["Total Memory (GB)"] = int(values[i])
        else:
            memory_info = {"Error": "Unsupported OS for memory info retrieval."}
    except Exception:
        memory_info = {"Error": "Failed to retrieve memory information."}
    return memory_info

def get_storage_info():
    storage_info = {}
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("wmic diskdrive get Caption, Size /format:list", shell=True).decode("utf-8")
            drives = result.strip().split("\n\n")
            for drive_info in drives:
                info = drive_info.strip().split('\n')
                drive = {}
                for line in info:
                    if "=" in line:
                        key, value = line.split("=", 1)
                        drive[key.strip()] = value.strip()
                storage_info[drive["Caption"]] = int(re.search(r'^\d+', drive["Size"]).group()) / (1024 ** 3)
        elif platform.system() == "Linux":
            result = subprocess.check_output("df -h", shell=True).decode("utf-8")
            lines = result.strip().split('\n')[1:]
            for line in lines:
                columns = line.split()
                storage_info[columns[5]] = int(columns[1].replace("G", ""))
        else:
            storage_info = {"Error": "Unsupported OS for storage info retrieval."}
    except Exception:
        storage_info = {"Error": "Failed to retrieve storage information."}
    return storage_info

def get_motherboard_info():
    motherboard_info = {}
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("wmic baseboard get Product, Manufacturer /format:list", shell=True).decode("utf-8")
            for line in result.strip().split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    motherboard_info[key.strip()] = value.strip()
        elif platform.system() == "Linux":
            result = subprocess.check_output("dmidecode -t baseboard | grep -E 'Product|Manufacturer'", shell=True).decode("utf-8")
            lines = result.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    motherboard_info[key.strip()] = value.strip()
        else:
            motherboard_info = {"Error": "Unsupported OS for motherboard info retrieval."}
    except Exception:
        motherboard_info = {"Error": "Failed to retrieve motherboard information."}
    return motherboard_info

def calculate_overall_score(cpu_score, memory_score, storage_score):
    weights = {
        "CPU": 0.4,
        "Memory": 0.2,
        "Storage": 0.2,
    }
    total_weight = sum(weights.values())
    return (weights["CPU"] * cpu_score + weights["Memory"] * memory_score +
            weights["Storage"] * storage_score) / total_weight

def plot_pie_chart(cpu_score, memory_score, storage_score):
    labels = ['CPU Performance', 'Memory (GB)', 'Storage (GB)']
    sizes = [cpu_score, memory_score, storage_score]
    colors = ['gold', 'lightcoral', 'lightskyblue']
    explode = (0.1, 0, 0)  # explode the 1st slice (CPU)

    plt.figure(figsize=(10, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('System Performance Overview')
    plt.show()

def main():
    system_info = get_system_info()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()
    storage_info = get_storage_info()
    motherboard_info = get_motherboard_info()

    print("System Information:")
    for key, value in system_info.items():
        print(f"{key}: {value}")

    print("\nCPU Information:")
    for key, value in cpu_info.items():
        print(f"{key}: {value}")

    print("\nMemory Information:")
    for key, value in memory_info.items():
        print(f"{key}: {value} GB")

    print("\nStorage Information:")
    for key, value in storage_info.items():
        print(f"{key}: {value} GB")

    print("\nMotherboard Information:")
    for key, value in motherboard_info.items():
        print(f"{key}: {value}")

    # Calculate overall score
    cpu_score = multi_core_task()  # Use single_core_task() if preferred
    memory_score = memory_info.get("Total Memory (GB)", 0)
    storage_score = sum(storage_info.values())
    overall_score = calculate_overall_score(cpu_score, memory_score, storage_score)
    print(f"\nOverall System Score: {overall_score:.2f}")

    # Plot the pie chart
    plot_pie_chart(cpu_score, memory_score, storage_score)

if __name__ == "__main__":
    main()
