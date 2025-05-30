## Recon & Report

### Tooling

1. **[iRecon](#irecon)** - `nmap` scan, the basis of chainsaw. 
2. **[Chainsaw](#chainsaw)** - Heavy recon, monitoring & cyberpunk report.
3. **[Chainsaw-ng](#chainsaw-ng)** - Enumeration, escalation & professional report. 

# CHAINSAW

![image](https://github.com/user-attachments/assets/59cac8e8-d20d-43fe-aa38-c139fd220cdb)

**Network Security Assessment Report Generation**
---

<img src="https://github.com/user-attachments/assets/858c125a-e15c-47f6-ae04-25b8f47840b1" width="70%" align="center">

## Installation
(All tools are optionally auto-installed on launch)

```bash
git clone https://github.com/lukeswitz/iRecon.git && cd iRecon && chmod +x chainsaw.py
```


## Usage
`python3 chainsaw.py <target> [options]`

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
--continuous - Run and make an hourly monitoring script for later use
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
- Executive summaries for management
- Create a script to run as a continuous monitor using 
---

# Chainsaw-ng
Gets to the findings in a clear concise manner. Use with or without credentials (- u username -p password flags)

## Features 
Uses the same tooling as the first. Packed with domain extraction, service enumeration and attack vector hints. 

### Report
<img src="https://github.com/user-attachments/assets/c6246643-2f0d-4057-bcdb-804caafd9c02" width="70%" align="center">

### Pathfinding

<img src="https://github.com/user-attachments/assets/6e45b0b9-017b-4e6e-9f9d-f61b52bc2e2a" width="90%" align="center">


- *Note: No continuous monitoring/webhooks*
  


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

