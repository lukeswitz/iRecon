# Auto Recon Scanners

1. [iRecon](#irecon) nmap report
2. [CyScan](#cyscan) scan & enumeration

# CyScan 

Next-gen penetration testing automation with adaptive enumeration. Based on iRecon. 

## Features

- 🔍 **Smart Port Discovery** with Nmap integration
- 🛡 **Protocol-Specific Tactics** for 20+ services
- 🔄 **Adaptive Fallbacks** with tool alternatives
- 🔑 **Credential Testing** with CrackMapExec/Impacket
- 📊 **Holographic HTML Reports** with scan artifacts
- ⚡ **Parallel Execution** engine

## Installation

### Core Requirements
```bash
# Kali Linux Base
sudo apt update && sudo apt install -y \
  nmap crackmapexec gobuster feroxbuster \
  smbclient evil-winrm snmp ldap-utils \
  mysql-client postgresql-client xfreerdp \
  socat python3-pip

# Impacket (Python)
git clone https://github.com/SecureAuthCorp/impacket.git
cd impacket && pip install . && cd ..
```

### Optional Enhancements
```bash
# Enhanced Wordlists
sudo apt install -y seclists wordlists
```

### Get CyScan
```bash
git clone https://github.com/lukeswitz/iRecon.git
cd iRecon
chmod +x cyberscan.py
```

## Operational Manual

### Basic Reconnaissance
```bash
./cyberscan.py 10.0.0.1
```

### Credential Assault
```bash
./cyberscan.py 10.0.0.1 -u admin -p 'P@ssw0rd!'
```

### Custom Enumeration
```bash
./cyberscan.py 10.0.0.1 \
  --wordlist ~/nuke_list.txt \
  --users ~/corp_users.txt \
  --passwords ~/breached_pass.txt
```

### Output System
- HTML report: `cyberscan_<TARGET>_<TIMESTAMP>.html`
- Auto-launches in default browser
- Full command output preservation

## Service Matrix

| Port  | Protocol      | Assault Vectors                          |
|-------|---------------|------------------------------------------|
| 21    | FTP           | Anonymous auth, Wget mirroring           |
| 22    | SSH           | Hydra integration, Security audits       |  
| 80    | HTTP          | Dual directory busting, Nikto scans      |
| 443   | HTTPS         | SSL/TLS analysis, Content discovery      |
| 445   | SMB           | Share storming, Impacket toolchain       |
| 3389  | RDP           | FreeRDP testing, Credential spraying     |
| 5985  | WinRM         | PowerShell remoting, WMI fallbacks       |
| 3306  | MySQL         | Database dumping, Auth testing           |
| 5432  | PostgreSQL    | Schema extraction, Cred attacks          |
| 161   | SNMP          | Community string brute-forcing           |
| 389   | LDAP          | Anonymous binds, Schema mapping          |

## Adaptive Fallback System

1. **Primary Tactics**  
   Protocol-specific ideal commands

2. **Secondary Measures**  
   Alternative tools/methods

3. **Nuclear Options**  
   Raw socket manipulation  
   SSL/TLS fingerprint forging  
   Impacket "getsystem" equivalents

## Customization Guide

### Wordlist Management
```bash
# Use custom lists
./cyberscan.py 10.0.0.1 \
  --wordlist ~/custom/dirs.txt \
  --users ~/custom/users.txt \
  --passwords ~/custom/pass.txt

# Default Paths (modify in script):
DEFAULT_WORDLISTS = {
    'dirbuster': '/usr/share/seclists/Discovery/Web-Content/raft-large-words.txt',
    'feroxbuster': '/usr/share/wordlists/dirb/big.txt',
    'snmp': '/usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt'
}
```

### Timeout Configuration
```python
# In run_cmd() function:
timeout=30  # ← Adjust scan command timeout
```

## Compliance

🚨 **Legal Imperative**  
CyScan shall only be deployed against systems with explicit written authorization. Unauthorized network intrusion violates international cyber laws. By executing CyScan, you affirm legal right to test the target system

## QRG (Quick Reference Guide)

### Error: Missing Tools
```bash
# Verify PATH contains:
which nmap crackmapexec gobuster feroxbuster
```

### Scan Too Slow?
```python
# Reduce thread workers:
ThreadPoolExecutor(max_workers=5)  # ← Default is 10
```

### Command Failures
```bash
# Test impacket installation:
python3 -m impacket.examples.smbexec
```

### Report Issues
```bash
# Enable debug mode (add to script):
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

![CyScan Matrix](https://i.imgur.com/3Yh7B2G.gif)  
*"The scanner that adapts like a human operator" - BlackHat EU 2024*


---

**Happy (Ethical) Hacking!** 🎮🔓


# iRecon

iRecon is an automated Nmap-based reconnaissance script designed to speed up the initial enumeration phase during CTFs or real-world pentests. It's especially useful for platforms like Hack The Box, where time and efficiency are key.

## Installation
Prerequisites
```bash
sudo apt install nmap xsltproc python3 wget bat firefox-esr lolcat xclip -y
```
Installing the tool
```bash
wget https://raw.githubusercontent.com/Gzzcoo/iRecon/refs/heads/main/iRecon
chmod +x iRecon
sudo mv iRecon /usr/local/bin/iRecon
```

## Usage
```bash
iRecon <IP>
```

## 🚀 Features

  - Performs a full port scan (-p-) using Nmap to detect open ports.

  - Automatically extracts open ports and copies them to your clipboard.

  - Detects service versions and runs basic reconnaissance scripts (-sCV) on discovered ports.

  - Generates a full Nmap XML report, transforms it into HTML, and opens it in your browser automatically.

  - Temporarily hosts the report using Python's HTTP server and releases the port right after.

  - Clean, quiet execution with colored terminal output (if added to your .zshrc or bash script).

## 📌 Why use iRecon?

While iRecon runs in the background automating tedious steps, you can focus on exploring services, web apps, or other vectors in parallel. This workflow dramatically reduces downtime and boosts productivity during reconnaissance.
No more wasting time typing repetitive Nmap commands or organizing reports manually — iRecon takes care of it all, and your port 6969 stays clean and free afterward 😉

## 🛠️ Perfect For

  - Hack The Box

  - TryHackMe

  - Offensive Security Labs

  - Red Team internal recon

  - Any scenario where speed and output clarity matter

## 📸 Preview

![imagen](https://github.com/user-attachments/assets/04c5c804-669f-4714-9ab4-10453bf10659)


https://github.com/user-attachments/assets/a98b0c4b-a0da-4168-81d3-2bc8c72cf709

