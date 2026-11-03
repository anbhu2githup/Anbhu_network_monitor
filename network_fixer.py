import os
import sys
import time
import socket
import subprocess
import ctypes
from datetime import datetime

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def log_message(text):
    """Prints a message to the console and writes it to a daily rolling log file."""
    timestamp_full = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp_full} {text}"
    print(log_line)
    
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(log_dir, f"network_log_{date_str}.txt")
        
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"[-] Logging failed: {e}")

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False

def diagnose_hardware():
    report = []
    try:
        result = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        
        has_connected_hardware = False
        adapter_count = 0
        
        for line in lines:
            if "Connected" in line or "Disconnected" in line:
                adapter_count += 1
                parts = line.split()
                if len(parts) >= 4:
                    status = parts[1]
                    name = " ".join(parts[3:])
                    report.append(f"   - Adapter '{name}': Status is {status}")
                    if status == "Connected":
                        has_connected_hardware = True
                        
        if adapter_count == 0:
            return "CRITICAL REPORT: No physical Wi-Fi or Ethernet network hardware could be found on this machine."
        elif not has_connected_hardware:
            return "CRITICAL REPORT: Wireless/Wired hardware exists, but ALL network adapters are physically disconnected (e.g., Cable unplugged or Wi-Fi turned off entirely)."
        else:
            return "REPORT: Network hardware is physically connected, but there is an authentication, IP configuration, or ISP routing issue."
            
    except Exception as e:
        return f"[-] Hardware diagnostics failed: {e}"

def get_active_adapters():
    adapters = []
    try:
        result = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, shell=True)
        for line in result.stdout.split('\n'):
            if "Connected" in line or "Disconnected" in line:
                parts = line.split()
                if len(parts) >= 4:
                    adapters.append(" ".join(parts[3:]))
    except:
        pass
    return adapters if adapters else ["Wi-Fi", "Ethernet"]

def repair_sequence():
    log_message("[!] Internet issue detected! Launching automatic repairs...")
    
    log_message("[*] Flushing DNS Cache and renewing IP configurations...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)
    subprocess.run(["ipconfig", "/release"], capture_output=True, shell=True)
    subprocess.run(["ipconfig", "/renew"], capture_output=True, shell=True)
    subprocess.run(["netsh", "int", "ip", "reset"], capture_output=True, shell=True)
    subprocess.run(["netsh", "winsock", "reset"], capture_output=True, shell=True)
    time.sleep(2)

    log_message("[*] Resetting hardware interfaces...")
    adapters = get_active_adapters()
    for adapter in adapters:
        log_message(f" -> Cycling: '{adapter}'")
        subprocess.run(["netsh", "interface", "set", "interface", adapter, "admin=disabled"], capture_output=True, shell=True)
        time.sleep(3)
        subprocess.run(["netsh", "interface", "set", "interface", adapter, "admin=enabled"], capture_output=True, shell=True)
        time.sleep(3)

    log_message("[*] Verifying stability...")
    time.sleep(5)
    if check_internet():
        log_message("[+] Success! Internet connectivity has been automatically restored.")
    else:
        log_message("[-] Automated repairs failed to establish internet.")
        hardware_status = diagnose_hardware()
        log_message(f"\n==================================================\n{hardware_status}\n==================================================")

if __name__ == "__main__":
    if not is_admin():
        print("[*] Requesting Administrator Privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print("==================================================")
        print("    BACKGROUND NETWORK MONITOR ACTIVATED          ")
        print("    Checking status every 60 seconds...           ")
        print("==================================================")
        log_message("[SYSTEM] Monitor initialization complete.")
        
        try:
            while True:
                if check_internet():
                    log_message("[OK] Internet connection is stable.")
                else:
                    repair_sequence()
                
                time.sleep(60)
        except KeyboardInterrupt:
            log_message("[SYSTEM] Background monitor terminated by user.")
