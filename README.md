# Automated Scan Tools

1. [iRecon](#irecon) nmap report
2. [CyScan](#cyscan) scan & enumeration


# CyScan

A penetration testing automation tool with reporting, comprehensive service enumeration, and smart fallback mechanisms.

## Features

- 🔍 **Full Port Enumeration** with Nmap
- 🛡 **Service-Specific Checks** for 15+ protocols
- 🔄 **Smart Fallback Mechanisms** for failed connections
- 💻 **CrackMapExec Integration** for credential testing
- 📊 **Cyberpunk HTML Reports** with interactive elements
- ⚡ **Concurrent Execution** for faster scanning

## Installation

### Dependencies

**Core Requirements:**
```bash
# Kali Linux
sudo apt update && sudo apt install -y \
  nmap \
  crackmapexec \
  gobuster \
  feroxbuster \
  smbclient \
  evil-winrm \
  snmp \
  ldap-utils \
  mysql-client \
  postgresql-client \
  xfreerdp \
  socat

# Impacket (Python)
git clone https://github.com/SecureAuthCorp/impacket.git
cd impacket && pip install . && cd ..

# Python Packages
pip install concurrent.futures html
```

**Ubuntu/Debian:**
```bash
sudo apt install -y \
  python3-pip \
  libssl-dev \
  libffi-dev \
  python3-dev \
  build-essential
```

### Get CyberScan
```bash
git clone https://github.com/lukeswitz/iRecon.git
cd iRecon
chmod +x cyberscan.py
```

## Usage

### Basic Scan
```bash
./cyberscan.py 10.0.0.1
```

### Authenticated Scan
```bash
./cyberscan.py 10.0.0.1 -u admin -p 'P@ssw0rd!'
```

### Custom Wordlist
```bash
./cyberscan.py 10.0.0.1 --wordlist ~/custom_wordlist.txt
```

### Output
- Report saved as `cyberscan_<IP>_<TIMESTAMP>.html`
- Automatically opens in default browser

## Configuration

### Tool Paths (Edit script directly)
```python
TOOL_PATHS = {
    'nmap': '/usr/bin/nmap',
    'cme': '/usr/bin/crackmapexec',
    'gobuster': '/usr/bin/gobuster',
    'feroxbuster': '/usr/bin/feroxbuster',
    'impacket': '/opt/impacket/examples/'
}
```

### Service Checks
Modify `SERVICE_CHECKS` dictionary to:
- Add new service checks
- Customize enumeration commands
- Adjust timeouts (default: 30s)

## Features Breakdown

### Service Coverage
| Port  | Service       | Checks Performed                      |
|-------|---------------|----------------------------------------|
| 21    | FTP           | Anonymous auth, Nmap scripts           |
| 22    | SSH           | Credential auth, Security checks       |
| 80    | HTTP          | Directory busting, Vulnerability scan  |
| 443   | HTTPS         | SSL checks, Web enumeration            |
| 445   | SMB           | Share enumeration, CrackMapExec        |
| 3389  | RDP           | Security audit, Client testing         |
| 5985  | WinRM         | PowerShell access, Alternative methods |

### Fallback Mechanisms
- **WinRM** → WMIExec, NTLM auth
- **SMB** → RPC client, Impacket tools
- **HTTP** → Alternate directory busting
- **Generic** → SSL/TLS detection, raw socket

## FAQ

**Q: Tools not found?**  
A: Verify paths in `TOOL_PATHS` and install missing packages

**Q: Scan taking too long?**  
A: Adjust `timeout` in `run_cmd()` or reduce thread count

**Q: Report not generating?**  
A: Check write permissions and HTML escaping

**Q: Commands failing?**  
A: Ensure all dependencies are installed and in PATH

## Disclaimer

⚠️ **Use Responsibly**  
This tool should only be used on systems you own or have explicit permission to test. Unauthorized scanning is illegal.

```bash
# Legal Notice
echo "By using CyberScan, you agree to use it only for lawful purposes"
```

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

