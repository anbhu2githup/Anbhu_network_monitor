# Background Network Monitor & Auto-Fixer

### 📘 Project Overview
The **Background Network Monitor & Auto-Fixer** is a dedicated Windows utility designed to maintain continuous internet connectivity through real-time automation. Operating as a silent background process, the application tests the system's internet status every 60 seconds using direct socket handshakes. By automating the diagnostic and repair workflow, it removes the need for manual troubleshooting or complex command-line interventions, providing an immediate resolution the moment an unexpected drop in connectivity occurs.

When an outage is detected, the program triggers an immediate multi-stage repair sequence to address both software and hardware communication layers. It flushes the local DNS cache, drops the active IP address configuration, requests a new assignment from the gateway, and clears the Windows network socket layers (Winsock). Following this, it targets the physical connection by locating active network adapters—including integrated Wi-Fi chipsets and Ethernet cards—and cycles them down and back up to re-establish clean authentication with the local gateway or router.

A defining capability of this utility is its advanced diagnostic reporting framework. If internet access is not restored after the structural repair cycle, the tool checks low-level hardware states to log the precise point of failure. It generates a definitive status report identifying whether an adapter is missing its core device drivers, if an Ethernet wire is unplugged, or if the system is connected to a local router that lacks an uplink to the service provider. Featuring automated daily logging, every event, recovery execution, and hardware exception is recorded into an audit file for long-term troubleshooting. This provides a resilient, set-it-and-forget-it watchdog solution for any workstation or server requiring constant network uptime.

## 🚀 Key Features

- **Continuous 60-Second Loop:** Monitors internet stability via low-level socket connections every minute.
- **RTL8188FTV Adapter Verification:** Uses Windows WMI queries to check if the specific Realtek RTL8188FTV chipset is installed.
- **Structured Interface Profiling:** Categorizes all communication hardware into active `Wi-Fi`, `LAN/Ethernet`, or `Other/Virtual` pipelines.
- **Robust Multi-Stage Repair:** Automatically triggers DNS flushes, IP lease renewals, and adapter level resets via elevated `netsh` pipelines.
- **Persistent Text Logging:** Handles pathing strings dynamically (checking for compiled or frozen states) to generate daily `.txt` logs.
- **Elevated Privileges Request:** Enforces structural execution integrity by automatically prompting for Windows Administrator rights (`runas`).

## 🛠️ How to Setup and Install

You only need **two files** to deploy this tool on your machine: `network_fixer.py` and `build_exe.bat`. Follow these steps to install and compile the tool:

### 1. File Setup
1. Create a dedicated folder on your Windows computer (for example: `C:\NetworkMonitor`).
2. Download or save the **`network_fixer.py`** source code inside that folder.
3. Download or save the **`build_exe.bat`** automation script inside the exact same folder.

### 2. Compiling the Executable
1. Double-click the **`build_exe.bat`** script.
2. A command prompt window will open and automatically execute the following sequence:
   - Upgrades or installs `pyinstaller` via your system's Python pip module.
   - Automatically runs a structural syntax check over `network_fixer.py` to prevent compilation faults.
   - Compiles the source script into a standalone binary with embedded User Account Control (`--uac-admin`) permission demands.
3. Wait until you see the `BUILD SUCCESSFUL!` verification message in the console.

### 3. Deploying the Program
Once finished, look inside your project folder. You will find a brand new directory named `dist`. 
1. Open the **`dist`** folder.
2. Double-click **`NetworkFixer.exe`** to start the continuous monitor dashboard. 
3. Click **Yes** on the Windows UAC screen to grant the utility access to cycle hardware adapters.

## 📊 Directory Architecture
When active, the folder manages its dependencies and daily text logs within this layout:
```text
📂 NetworkMonitor/
 ├── 📂 dist/
 │    └── 📄 NetworkFixer.exe   <-- Run this standalone tool
 ├── 📂 logs/
 │    └── 📄 network_log_YYYY-MM-DD.txt  <-- Daily network audit logs
 ├── 📄 network_fixer.py
 └── 📄 build_exe.bat
```

## 🛑 How to Uninstall or Terminate
- To temporarily stop the monitor loop, simply close the active Command Prompt terminal or press `Ctrl + C` inside it.
- To completely delete the program, delete the parent `NetworkMonitor` directory from your computer. No background registry entries are modified.

## ⚖️ License
This project is licensed under the terms of the MIT License.
