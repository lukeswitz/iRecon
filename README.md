# Auto Recon Scanners

1. [iRecon](#irecon) - Simple `nmap` Report
2. [CHAINSAW](#chainsaw) - Advanced scan & enumeration

# CHAINSAW


![image](https://github.com/user-attachments/assets/59cac8e8-d20d-43fe-aa38-c139fd220cdb)

**Network Security Assessment Tool with auto report generation**
---

<img src="https://github.com/user-attachments/assets/858c125a-e15c-47f6-ae04-25b8f47840b1" width="70%" align="center">

## Installation
(All tools are optionally auto-installed on launch)

```bash
git clone https://github.com/lukeswitz/iRecon.git && cd iRecon && chmod +x chainsaw.py
```

## Usage
`bashpython3 chainsaw.py <target> [options]`

### Examples
```bash
python3 chainsaw.py 192.168.1.1
python3 chainsaw.py target.com --evasion --api-test --export-json
python3 chainsaw.py server.com -u admin -p pass --continuous
python3 chainsaw.py site.com --integrations discord_notify --discord-webhook "URL"
```

### Key Options
```bash
--evasion - Stealth techniques
--api-test - API endpoint testing
--continuous - 24/7 monitoring
--export-json - JSON output
--integrations - Slack/Discord/Teams/IFTTT/Jira notifications
```

## Features

- 20+ service tests (FTP, SSH, HTTP, SMB, databases, containers)
- Risk scoring (0-10 CVSS-like scale)
- Attack path analysis (lateral movement, privilege escalation)
- HTML reports with executive summaries
- Multi-platform notifications and SIEM integration


## Output

- Interactive HTML reports with animations
- JSON export for automation/SIEM
- Real-time console progress
- Executive summaries for management

---

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

