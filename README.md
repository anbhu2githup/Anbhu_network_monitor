# Anbhu_network_monitor
Background Network Monitor &amp; Auto-Fixer is a silent Windows utility that checks internet connectivity every 60 seconds. If a drop occurs, it flushes DNS cache, renews IP leases, resets Winsock, and cycles Wi-Fi/Ethernet adapters to restore connections. It records diagnostics and missing hardware to automated daily audit logs.
# Background Network Monitor & Auto-Fixer

### 📘 Project Overview
The **Background Network Monitor & Automated Auto-Fixer** is a robust, lightweight Windows infrastructure utility designed to ensure maximum network uptime through proactive, hands-free troubleshooting. Written natively in Python and packaged into a self-contained executable file, this utility runs continuously in the background, checking internet stability via a dedicated socket loop precisely every 60 seconds. Instead of forcing users to manually interact with Windows diagnostic prompts or command-line scripts when connections fail, this software handles the entire network lifecycle completely automated, stepping in only when a real connectivity drop is verified.

When a drop in internet connectivity is flagged, the tool immediately initializes a comprehensive, three-step system triage sequence that mirrors the actions of an expert network engineer. First, it targets the operating system's software communication layers by clearing out stagnant routing data; it clears the local DNS cache, drops the active IP address lease, requests a fresh configuration from the local gateway, and completely flushes the system’s Winsock socket API architecture. Second, it cycles the physical communication hardware layers by mapping every active network adapter on the computer—such as wireless radios and integrated Ethernet cards—and momentarily shifting them to an administratively disabled status before toggling them back online to force clean access point handshakes.

What elevates this utility beyond a basic reboot mechanism is its advanced post-repair hardware reporting framework. If internet connectivity fails to return after running the core repair protocols, the software runs deep low-level system checks on the physical device interfaces. It then presents a diagnostic readout revealing the root structural bottleneck—explicitly calling out whether an interface is entirely missing its hardware drivers, whether an Ethernet cable is physically unplugged from its port, or if the system remains bound to a working router that lacks external ISP internet delivery. Complete with an embedded administrative manifest that ensures proper UAC privileges upon execution, this tool serves as a permanent set-it-and-forget-it automated guardian for Windows systems requiring absolute internet dependability.

## 🚀 Key Features

- **Continuous 60-Second Loop:** Runs persistently, checking internet stability via low-level socket connections every minute.
- **Automated Text Logging:** Automatically creates a `/logs` folder and writes daily timestamped `.txt` archives detailing stability updates, hardware faults, and fixes.
- **Automated Network Stack Repair:** Automatically flushes the system DNS cache, releases/renews IP configurations, and resets the Winsock stack when offline.
- **Hardware Interface Cycling:** Programmatically disables and re-enables all active network adapters (Wi-Fi, Ethernet) to force hardware re-authentication.
- **Advanced Diagnostics & Hardware Reporting:** Captures and reports states like physical wire disconnects or missing Wi-Fi hardware.
- **Elevated UAC Manifest:** Automatically requests the necessary Windows Administrator privileges needed to interact with hardware interfaces.

## 🛠️ Installation & Compilation Instructions

### Step 1: Create the Python File
1. Create a directory named `NetworkMonitor`.
2. Save the modified `network_fixer.py` script inside it.

### Step 2: Compiling to a Standalone Executable (.EXE)
1. In the same folder, run a batch script containing:
   ```batch
   pip install pyinstaller && pyinstaller --onefile --uac-admin network_fixer.py
   ```
2. Navigate into the newly created `dist/` directory.
3. Launch **`network_fixer.exe`**.

## 📊 File Audit Structure
When running, the application structures data dynamically inside its deployment root directory:
```text
📂 NetworkMonitor/
 ├── 📂 dist/
 │    └── 📄 network_fixer.exe  <-- Run This 
 ├── 📂 logs/
 │    └── 📄 network_log_2026-11-03.txt  <-- Daily Log Outputs
 ├── 📄 network_fixer.py
 └── 📄 README.md
