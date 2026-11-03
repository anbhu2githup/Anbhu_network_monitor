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
    except Exception:
        return False

def force_admin_elevation():
    try:
        script_path = os.path.abspath(sys.argv[0])
        params = subprocess.list2cmdline([script_path] + sys.argv[1:])
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, os.path.dirname(script_path), 1)
        if result <= 32:
            print("[-] Administrator elevation failed.")
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"[-] Elevation error: {e}")
        sys.exit(1)

def log_message(text):
    timestamp_full = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp_full} {text}"
    print(log_line, flush=True)
    try:
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(log_dir, f"network_log_{date_str}.txt")
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"[-] Logging failed: {e}")

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def get_hardware_descriptions():
    hardware_map = {}
    try:
        cmd = 'wmic path win32_pnpsigneddriver where "DeviceClass=\'NET\'" get DeviceName, FriendlyName /format:list'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=15)
        current_name = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("DeviceName="):
                parts = line.split("=", 1)
                if len(parts) > 1:
                    current_name = parts[1]
            elif line.startswith("FriendlyName=") and current_name:
                parts = line.split("=", 1)
                if len(parts) > 1:
                    friendly = parts[1]
                    clean_key = friendly.split(" - ")[0].strip()
                    hardware_map[clean_key] = current_name
                    current_name = None
    except Exception:
        pass
    return hardware_map

def get_profiled_adapters():
    wifi_adapters = []
    lan_adapters = []
    other_adapters = []
    hw_descriptions = get_hardware_descriptions()
    try:
        result = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, shell=False, timeout=15)
        for line in result.stdout.splitlines():
            if "Connected" in line or "Disconnected" in line or "Enabled" in line or "Disabled" in line:
                parts = line.split()
                if len(parts) >= 4:
                    status = parts[0]
                    name = " ".join(parts[3:])
                    lower_name = name.lower()
                    hardware_model = "Unknown Device"
                    for key, val in hw_descriptions.items():
                        if name in key or key in name or name.lower() in val.lower():
                            hardware_model = val
                            break
                    if hardware_model == "Unknown Device" and len(hw_descriptions) > 0:
                        if "wi-fi" in lower_name or "wifi" in lower_name:
                            matched = [v for k, v in hw_descriptions.items() if "wireless" in v.lower() or "wi-fi" in v.lower() or "802.11" in v.lower()]
                            if matched: hardware_model = matched[0]
                        elif "ethernet" in lower_name:
                            matched = [v for k, v in hw_descriptions.items() if "ethernet" in v.lower() or "gigabit" in v.lower() or "pcie" in v.lower()]
                            if matched: hardware_model = matched[0]
                    entry = f"'{name}' [Hardware: {hardware_model}] (Status: {status})"
                    if "wi-fi" in lower_name or "wifi" in lower_name or "wireless" in lower_name or "wlan" in lower_name:
                        wifi_adapters.append(entry)
                    elif "ethernet" in lower_name or "lan" in lower_name:
                        lan_adapters.append(entry)
                    else:
                        other_adapters.append(entry)
    except Exception as e:
        log_message(f"[-] Adapter profiling error: {e}")
    return wifi_adapters, lan_adapters, other_adapters

def display_hardware_profile():
    log_message("=== SYSTEM HARDWARE PROFILING ===")
    wifi, lan, other = get_profiled_adapters()
    log_message("[DETECTED ADAPTER CATEGORIES]")
    if wifi:
        for w in wifi: log_message(f"   -> [Wi-Fi] {w}")
    else:
        log_message("   -> [Wi-Fi] No active wireless hardware mapped.")
    if lan:
        for l in lan: log_message(f"   -> [LAN/Ethernet] {l}")
    else:
        log_message("   -> [LAN/Ethernet] No active wired hardware mapped.")
    if other:
        for o in other: log_message(f"   -> [OTHER/VIRTUAL] {o}")
    else:
        log_message("   -> [OTHER/VIRTUAL] No additional interfaces detected.")
    log_message("=================================\n")

def get_all_interface_names():
    adapters = []
    try:
        result = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, shell=False, timeout=15)
        for line in result.stdout.splitlines():
            if "Connected" in line or "Disconnected" in line or "Enabled" in line or "Disabled" in line:
                parts = line.split()
                if len(parts) >= 4:
                    adapter_name = " ".join(parts[3:])
                    if adapter_name: adapters.append(adapter_name)
    except Exception as e:
        log_message(f"[-] Could not retrieve interfaces: {e}")
    return adapters if adapters else ["Wi-Fi", "Ethernet"]

def repair_sequence():
    log_message("[!] Internet issue detected! Launching automatic repairs...")
    log_message("[*] Flushing DNS cache and renewing IP configurations...")
    commands = [
        ["ipconfig", "/flushdns"],
        ["ipconfig", "/release"],
        ["ipconfig", "/renew"],
        ["netsh", "int", "ip", "reset"],
        ["netsh", "winsock", "reset"]
    ]
    for command in commands:
        try:
            subprocess.run(command, capture_output=True, shell=False, timeout=60)
        except Exception as e:
            log_message(f"[-] Command error {command}: {e}")
    time.sleep(2)
    log_message("[*] Resetting hardware interfaces...")
    adapters = get_all_interface_names()
    for adapter in adapters:
        log_message(f" -> Cycling interface: '{adapter}'")
        try:
            subprocess.run(["netsh", "interface", "set", "interface", adapter, "admin=disabled"], capture_output=True, shell=False, timeout=30)
            time.sleep(3)
            subprocess.run(["netsh", "interface", "set", "interface", adapter, "admin=enabled"], capture_output=True, shell=False, timeout=30)
            time.sleep(3)
        except Exception as e:
            log_message(f"[-] Adapter reset failed for '{adapter}': {e}")
    log_message("[*] Verifying network stability...")
    time.sleep(5)
    if check_internet():
        log_message("[+] Success! Internet connectivity has been automatically restored.")
    else:
        log_message("[-] Automated repairs failed. Running diagnostic check...")
        display_hardware_profile()

def main():
    if not is_admin():
        print("[*] Insufficient permissions. Launching Windows administrative prompt...")
        force_admin_elevation()
    print("==================================================")
    print("    BACKGROUND NETWORK MONITOR ACTIVATED")
    print("    Checking status every 60 seconds...")
    print("==================================================")
    log_message("[SYSTEM] Monitor initialization complete under administrative shell context.")
    display_hardware_profile()
    try:
        while True:
            if check_internet():
                log_message("[OK] Internet connection is stable.")
            else:
                repair_sequence()
            time.sleep(60)
    except KeyboardInterrupt:
        log_message("[SYSTEM] Background monitor terminated by user.")

if __name__ == "__main__":
    main()
