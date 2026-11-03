
import os
import sys
import time
import socket
import subprocess
import ctypes
import shlex
from datetime import datetime


# ============================================================
# ADMINISTRATOR PRIVILEGES
# ============================================================

def is_admin():
    """Check whether the script has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def force_admin_elevation():
    """Restart the script with Windows administrator privileges."""
    try:
        script_path = os.path.abspath(sys.argv[0])

        # Properly quote arguments, including paths containing spaces.
        params = subprocess.list2cmdline(
            [script_path] + sys.argv[1:]
        )

        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            params,
            os.path.dirname(script_path),
            1
        )

        if result <= 32:
            print("[-] Administrator elevation failed.")
            print("[-] Please run this program as Administrator.")
            input("Press Enter to exit...")
            sys.exit(1)

        sys.exit(0)

    except Exception as e:
        print(f"[-] Elevation error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


# ============================================================
# LOGGING SYSTEM
# ============================================================

def log_message(text):
    """Display messages and save them to daily log files."""

    timestamp_full = datetime.now().strftime(
        "[%Y-%m-%d %H:%M:%S]"
    )

    log_line = f"{timestamp_full} {text}"
    print(log_line, flush=True)

    try:
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(
                os.path.abspath(sys.executable)
            )
        else:
            base_dir = os.path.dirname(
                os.path.abspath(__file__)
            )

        log_dir = os.path.join(base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")

        log_file_path = os.path.join(
            log_dir,
            f"network_log_{date_str}.txt"
        )

        with open(
            log_file_path,
            "a",
            encoding="utf-8"
        ) as f:
            f.write(log_line + "\n")

    except Exception as e:
        print(f"[-] Logging failed: {e}")


# ============================================================
# INTERNET CONNECTIVITY CHECK
# ============================================================

def check_internet(
    host="8.8.8.8",
    port=53,
    timeout=3
):
    """Check internet connectivity using a TCP connection."""

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout
        ):
            return True

    except OSError:
        return False


# ============================================================
# RTL8188FTV HARDWARE DETECTION
# ============================================================

def check_rtl8188ftv_hardware():
    """Check for RTL8188FTV wireless adapter using Windows WMI."""

    try:
        cmd = (
            'wmic path win32_pnpsigneddriver '
            'where "DeviceName like \'%RTL8188FTV%\'" '
            'get DeviceName /format:list'
        )

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            timeout=15
        )

        if "RTL8188FTV" in result.stdout.upper():
            return (
                "[FOUND] RTL8188FTV Wireless LAN "
                "adapter is installed on this system."
            )

        return (
            "[NOT FOUND] RTL8188FTV Wireless LAN "
            "adapter was not detected."
        )

    except Exception:
        return (
            "[UNKNOWN] Could not verify RTL8188FTV "
            "hardware status."
        )


# ============================================================
# NETWORK ADAPTER PROFILING
# ============================================================

def get_profiled_adapters():
    """Categorize Windows network interfaces."""

    wifi_adapters = []
    lan_adapters = []
    other_adapters = []

    try:
        result = subprocess.run(
            [
                "netsh",
                "interface",
                "show",
                "interface"
            ],
            capture_output=True,
            text=True,
            shell=False,
            timeout=15
        )

        lines = result.stdout.splitlines()

        for line in lines:

            if (
                "Connected" in line
                or "Disconnected" in line
                or "Enabled" in line
                or "Disabled" in line
            ):

                parts = line.split()

                if len(parts) >= 4:

                    status = parts[0]
                    name = " ".join(parts[3:])

                    lower_name = name.lower()

                    entry = (
                        f"'{name}' (Status: {status})"
                    )

                    if (
                        "wi-fi" in lower_name
                        or "wifi" in lower_name
                        or "wireless" in lower_name
                        or "wlan" in lower_name
                    ):

                        wifi_adapters.append(entry)

                    elif (
                        "ethernet" in lower_name
                        or "lan" in lower_name
                    ):

                        lan_adapters.append(entry)

                    else:
                        other_adapters.append(entry)

    except Exception as e:
        log_message(
            f"[-] Adapter profiling error: {e}"
        )

    return (
        wifi_adapters,
        lan_adapters,
        other_adapters
    )


# ============================================================
# HARDWARE PROFILE DISPLAY
# ============================================================

def display_hardware_profile():

    log_message(
        "=== SYSTEM HARDWARE PROFILING ==="
    )

    rtl_status = check_rtl8188ftv_hardware()

    log_message(
        f"[CHIPSET] {rtl_status}"
    )

    wifi, lan, other = get_profiled_adapters()

    log_message(
        "[ADAPTER CATEGORIES]"
    )

    # Wi-Fi adapters
    if wifi:

        for w in wifi:
            log_message(
                f"   -> [Wi-Fi] {w}"
            )

    else:

        log_message(
            "   -> [Wi-Fi] "
            "No active wireless interfaces mapped."
        )

    # LAN / Ethernet adapters
    if lan:

        for l in lan:
            log_message(
                f"   -> [LAN/Ethernet] {l}"
            )

    else:

        log_message(
            "   -> [LAN/Ethernet] "
            "No active wired interfaces mapped."
        )

    # FIXED: Correct indentation of the OTHER adapter block
    if other:

        for o in other:
            log_message(
                f"   -> [OTHER/VIRTUAL] {o}"
            )

    else:

        log_message(
            "   -> [OTHER/VIRTUAL] "
            "No additional interfaces detected."
        )

    log_message(
        "=================================\n"
    )


# ============================================================
# GET ALL NETWORK INTERFACE NAMES
# ============================================================

def get_all_interface_names():
    """Return the names of available network interfaces."""

    adapters = []

    try:

        result = subprocess.run(
            [
                "netsh",
                "interface",
                "show",
                "interface"
            ],
            capture_output=True,
            text=True,
            shell=False,
            timeout=15
        )

        for line in result.stdout.splitlines():

            if (
                "Connected" in line
                or "Disconnected" in line
                or "Enabled" in line
                or "Disabled" in line
            ):

                parts = line.split()

                if len(parts) >= 4:

                    adapter_name = " ".join(
                        parts[3:]
                    )

                    if adapter_name:
                        adapters.append(
                            adapter_name
                        )

    except Exception as e:

        log_message(
            f"[-] Could not retrieve interfaces: {e}"
        )

    if not adapters:

        return [
            "Wi-Fi",
            "Ethernet"
        ]

    return adapters


# ============================================================
# AUTOMATIC NETWORK REPAIR SEQUENCE
# ============================================================

def repair_sequence():

    log_message(
        "[!] Internet issue detected! "
        "Launching automatic repairs..."
    )

    # --------------------------------------------------------
    # STEP 1: Flush DNS and reset IP configuration
    # --------------------------------------------------------

    log_message(
        "[*] Flushing DNS cache and renewing IP configurations..."
    )

    commands = [

        ["ipconfig", "/flushdns"],

        ["ipconfig", "/release"],

        ["ipconfig", "/renew"],

        [
            "netsh",
            "int",
            "ip",
            "reset"
        ],

        [
            "netsh",
            "winsock",
            "reset"
        ]

    ]

    for command in commands:

        try:

            subprocess.run(
                command,
                capture_output=True,
                shell=False,
                timeout=60
            )

        except subprocess.TimeoutExpired:

            log_message(
                f"[-] Command timed out: {command}"
            )

        except Exception as e:

            log_message(
                f"[-] Command error {command}: {e}"
            )

    time.sleep(2)

    # --------------------------------------------------------
    # STEP 2: Reset network interfaces
    # --------------------------------------------------------

    log_message(
        "[*] Resetting hardware interfaces..."
    )

    adapters = get_all_interface_names()

    for adapter in adapters:

        log_message(
            f" -> Cycling interface: '{adapter}'"
        )

        try:

            subprocess.run(
                [
                    "netsh",
                    "interface",
                    "set",
                    "interface",
                    adapter,
                    "admin=disabled"
                ],
                capture_output=True,
                shell=False,
                timeout=30
            )

            time.sleep(3)

            subprocess.run(
                [
                    "netsh",
                    "interface",
                    "set",
                    "interface",
                    adapter,
                    "admin=enabled"
                ],
                capture_output=True,
                shell=False,
                timeout=30
            )

            time.sleep(3)

        except Exception as e:

            log_message(
                f"[-] Adapter reset failed "
                f"for '{adapter}': {e}"
            )

    # --------------------------------------------------------
    # STEP 3: Verify internet connectivity
    # --------------------------------------------------------

    log_message(
        "[*] Verifying network stability..."
    )

    time.sleep(5)

    if check_internet():

        log_message(
            "[+] Success! Internet connectivity "
            "has been automatically restored."
        )

    else:

        log_message(
            "[-] Automated repairs failed. "
            "Running diagnostic check..."
        )

        display_hardware_profile()


# ============================================================
# MAIN NETWORK MONITOR
# ============================================================

def main():

    # --------------------------------------------------------
    # STEP 1: Administrator verification
    # --------------------------------------------------------

    if not is_admin():

        print(
            "[*] Insufficient permissions. "
            "Launching Windows administrative prompt..."
        )

        force_admin_elevation()

    # --------------------------------------------------------
    # STEP 2: Initialize monitoring
    # --------------------------------------------------------

    print(
        "=================================================="
    )

    print(
        "    BACKGROUND NETWORK MONITOR ACTIVATED"
    )

    print(
        "    Checking status every 60 seconds..."
    )

    print(
        "=================================================="
    )

    log_message(
        "[SYSTEM] Monitor initialization complete "
        "under administrative shell context."
    )

    # --------------------------------------------------------
    # STEP 3: Display hardware profile
    # --------------------------------------------------------

    display_hardware_profile()

    # --------------------------------------------------------
    # STEP 4: Continuous internet monitoring
    # --------------------------------------------------------

    try:

        while True:

            if check_internet():

                log_message(
                    "[OK] Internet connection is stable."
                )

            else:

                repair_sequence()

            time.sleep(60)

    except KeyboardInterrupt:

        log_message(
            "[SYSTEM] Background monitor terminated by user."
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
