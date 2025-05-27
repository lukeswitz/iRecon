#!/usr/bin/env python3
import argparse
import subprocess
import os
import webbrowser
import json
from html import escape
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
import platform
import shutil
import signal
import sys
import atexit
import re

def check_and_install_tools():
    """Check for required tools and install if missing"""
    tool_aliases = {
        'crackmapexec': ['nxc', 'netexec', 'crackmapexec'],
        'testssl': ['testssl', 'testssl.sh'],
        'enum4linux': ['enum4linux', 'enum4linux-ng'],
        'smbclient': ['smbclient'],
        'redis-cli': ['redis-cli', 'redis-client'],
        'mysql': ['mysql', 'mysql-client'],
        'psql': ['psql', 'postgresql-client'],
        'telnet': ['telnet']
    }
    
    required_tools = {
        'nmap': 'nmap',
        'gobuster': 'gobuster',
        'nikto': 'nikto',
        'feroxbuster': 'feroxbuster',
        'smbclient': 'smbclient',
        'enum4linux': 'enum4linux-ng',
        'nxc': 'netexec',
        'evil-winrm': 'evil-winrm',
        'testssl': 'testssl.sh',
        'redis-cli': 'redis-tools',
        'mysql': 'mysql-client',
        'psql': 'postgresql-client',
        'hydra': 'hydra',
        'telnet': 'telnet'
    }
    
    missing_tools = []
    found_tools = []
    
    for tool, package in required_tools.items():
        aliases = tool_aliases.get(tool, [tool])
        found = False
        
        for alias in aliases:
            if shutil.which(alias):
                found_tools.append(f"{tool} (found as '{alias}')")
                found = True
                break
        
        if not found:
            missing_tools.append((tool, package))
    
    if found_tools:
        print(f"[+] Found tools: {found_tools}")
    
    if missing_tools:
        print(f"[!] Missing tools: {[tool for tool, _ in missing_tools]}")
    
    return True

# Professional color scheme (Hunt.io inspired)
class Colors:
    PRIMARY = '#2D3748'     # Dark blue-grey
    SECONDARY = '#4A5568'   # Medium grey
    SUCCESS = '#38A169'     # Green
    WARNING = '#D69E2E'     # Orange
    DANGER = '#E53E3E'      # Red
    INFO = '#3182CE'        # Blue
    LIGHT = '#F7FAFC'       # Light grey
    ACCENT = '#805AD5'      # Purple

# Clean, modern CSS
MODERN_CSS = f"""
<style>
    body {{
        background: linear-gradient(135deg, {Colors.LIGHT} 0%, #EDF2F7 100%);
        color: {Colors.PRIMARY};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin: 0;
        padding: 2rem;
        line-height: 1.6;
    }}
    
    .container {{
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }}
    
    .header {{
        background: linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.SECONDARY} 100%);
        color: white;
        padding: 2rem;
        text-align: center;
    }}
    
    .header h1 {{
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }}
    
    .header h2 {{
        margin: 0.5rem 0 0 0;
        font-size: 1.25rem;
        opacity: 0.9;
        font-weight: 400;
    }}
    
    .status-bar {{
        background: {Colors.LIGHT};
        padding: 1rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .status-item {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
    }}
    
    .badge {{
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }}
    
    .badge-success {{ background: {Colors.SUCCESS}; color: white; }}
    .badge-warning {{ background: {Colors.WARNING}; color: white; }}
    .badge-danger {{ background: {Colors.DANGER}; color: white; }}
    .badge-info {{ background: {Colors.INFO}; color: white; }}
    
    .content {{
        padding: 2rem;
    }}
    
    .summary-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }}
    
    .summary-card {{
        background: {Colors.LIGHT};
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid {Colors.INFO};
    }}
    
    .summary-card.critical {{ border-left-color: {Colors.DANGER}; }}
    .summary-card.high {{ border-left-color: {Colors.WARNING}; }}
    .summary-card.medium {{ border-left-color: {Colors.INFO}; }}
    .summary-card.low {{ border-left-color: {Colors.SUCCESS}; }}
    
    .summary-card h3 {{
        margin: 0 0 1rem 0;
        font-size: 1.125rem;
        font-weight: 600;
        color: {Colors.PRIMARY};
    }}
    
    .summary-card .metric {{
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .summary-card .label {{
        font-size: 0.875rem;
        color: {Colors.SECONDARY};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .findings-section {{
        background: linear-gradient(135deg, rgba(229, 62, 62, 0.05) 0%, rgba(229, 62, 62, 0.1) 100%);
        border: 1px solid rgba(229, 62, 62, 0.2);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
    }}
    
    .findings-section h2 {{
        margin: 0 0 1rem 0;
        color: {Colors.DANGER};
        font-size: 1.5rem;
        font-weight: 600;
    }}
    
    .finding-item {{
        background: white;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid {Colors.DANGER};
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }}
    
    .service-section {{
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        margin: 1.5rem 0;
        overflow: hidden;
    }}
    
    .service-header {{
        background: {Colors.LIGHT};
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .service-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {Colors.PRIMARY};
    }}
    
    .risk-score {{
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
    }}
    
    .risk-critical {{ background: {Colors.DANGER}; color: white; }}
    .risk-high {{ background: {Colors.WARNING}; color: white; }}
    .risk-medium {{ background: {Colors.INFO}; color: white; }}
    .risk-low {{ background: {Colors.SUCCESS}; color: white; }}
    
    .service-content {{
        padding: 1.5rem;
    }}
    
    .command-result {{
        margin-bottom: 1.5rem;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }}
    
    .command-header {{
        background: {Colors.SECONDARY};
        color: white;
        padding: 0.75rem 1rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.875rem;
    }}
    
    .command-output {{
        background: #F8F9FA;
        padding: 1rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.875rem;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 400px;
        overflow-y: auto;
        border-top: 1px solid #E2E8F0;
    }}
    
    .success {{ color: {Colors.SUCCESS}; }}
    .warning {{ color: {Colors.WARNING}; }}
    .danger {{ color: {Colors.DANGER}; }}
    .info {{ color: {Colors.INFO}; }}
    
    .port-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }}
    
    .port-card {{
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }}
    
    .port-number {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {Colors.PRIMARY};
    }}
    
    .port-service {{
        font-size: 0.875rem;
        color: {Colors.SECONDARY};
        margin-bottom: 0.5rem;
    }}
    
    @media (max-width: 768px) {{
        .summary-grid {{
            grid-template-columns: 1fr;
        }}
        
        .status-bar {{
            flex-direction: column;
            align-items: stretch;
        }}
        
        .port-grid {{
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        }}
    }}
</style>
"""

DEFAULT_WORDLISTS = {
    'dirbuster': '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
    'feroxbuster': '/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt',
    'snmp': '/usr/share/wordlists/dict.txt',
    'users': 'users.txt',
    'passwords': 'passwords.txt',
    'api': '/usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints.txt',
    'subdomains': '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt'
}

# OPTIMIZED SERVICE CHECKS - Fixed commands based on output analysis
ENHANCED_SERVICE_CHECKS = {
    21: {
        'name': 'FTP',
        'risk_base': 7.0,
        'enumeration': [
            'nxc ftp {ip} -u "" -p ""',
            'nxc ftp {ip} -u "anonymous" -p ""',
            'nxc ftp {ip} -u "ftp" -p "ftp"'
        ],
        'authentication': ['nxc ftp {ip} -u {user} -p {pass}'],
        'escalation': [
            'nxc ftp {ip} -u {user} -p {pass} --ls',
            'nxc ftp {ip} -u {user} -p {pass} --get-file /etc/passwd passwd_{ip}.txt'
        ]
    },
    
    22: {
        'name': 'SSH',
        'risk_base': 5.0,
        'enumeration': [
            'ssh-keyscan -T 10 {ip}',
            'nxc ssh {ip} -u "" -p ""'
        ],
        'authentication': [
            'nxc ssh {ip} -u {user} -p {pass}',
            'nxc ssh {ip} -u {user} -p {pass} -x "id; hostname; pwd"'
        ]
    },
    
    23: {
        'name': 'Telnet',
        'risk_base': 8.0,
        'enumeration': [
            'echo "quit" | timeout 10 telnet {ip} 23'
        ],
        'authentication': [
            'hydra -l {user} -p {pass} telnet://{ip}'
        ]
    },
    
    25: {
        'name': 'SMTP',
        'risk_base': 6.0,
        'enumeration': [
            'nxc smtp {ip} -u "" -p ""',
            'smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/Names/names.txt -t {ip}'
        ],
        'authentication': ['nxc smtp {ip} -u {user} -p {pass}']
    },
    
    53: {
        'name': 'DNS',
        'risk_base': 6.0,
        'enumeration': [
            'dig @{ip} version.bind chaos txt',
            'dig @{ip} {domain} any',
            'dig @{ip} {domain} axfr'
        ],
        'escalation': [
            'gobuster dns -d {domain} -r {ip} -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --timeout 10s -q'
        ]
    },
    
    80: {
        'name': 'HTTP',
        'risk_base': 4.0,
        'enumeration': [
            'curl -sI http://{ip} --max-time 10',
            'whatweb http://{ip}',
            'curl -s http://{ip}/robots.txt'
        ],
        'escalation': [
            'feroxbuster -u http://{ip} -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 50 --silent --depth 2 -x php,txt,html,asp,aspx,jsp',
            'nikto -h http://{ip} -timeout 30'
        ]
    },
    
    88: {
        'name': 'Kerberos',
        'risk_base': 7.0,
        'enumeration': [
            'nxc ldap {ip} -u "" -p "" -d {domain}',
            'kerbrute userenum --dc {ip} -d {domain} /usr/share/seclists/Usernames/Names/names.txt'
        ],
        'authentication': [
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --users --groups',
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --kerberoasting /tmp/kerb_{ip}.txt',
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --asreproast /tmp/asrep_{ip}.txt'
        ],
        'escalation': [
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --bloodhound --collection All --dns-server {ip}',
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --admin-count',
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --trusted-for-delegation'
        ]
    },
    
    135: {
        'name': 'RPC-MSRPC',
        'risk_base': 7.0,
        'enumeration': [
            'rpcclient -U "" -N {ip} -c "enumdomusers;enumdomgroups"',
            'rpcinfo -p {ip}',
            'impacket-rpcmap {ip}'
        ],
        'authentication': [
            'rpcclient -U {user}%{pass} {ip} -c "enumdomusers;enumdomgroups;queryuser administrator"'
        ]
    },
    
    139: {
        'name': 'NetBIOS',
        'risk_base': 7.0,
        'enumeration': [
            'enum4linux-ng -A {ip}',
            'smbclient -L //{ip}/ -N',
            'nbtscan {ip}',
            'nmblookup -A {ip}'
        ],
        'authentication': [
            'nxc smb {ip} -u {user} -p {pass} -d {domain} --shares',
            'smbclient -L //{ip}/ -U {user}%{pass}'
        ],
        'escalation': [
            'smbmap -H {ip} -d {domain} -u {user} -p {pass} -R',
            'nxc smb {ip} -u {user} -p {pass} -M spider_plus -o READ_ONLY=false OUTPUT_FOLDER=/tmp/smb_files_{ip}'
        ]
    },
    
    161: {
        'name': 'SNMP',
        'risk_base': 8.0,
        'enumeration': [
            'snmpwalk -v2c -c public {ip} 2>/dev/null | head -20',
            'onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt {ip}',
            'snmpget -v2c -c public {ip} 1.3.6.1.2.1.1.5.0'
        ],
        'escalation': [
            'snmpwalk -v2c -c public {ip} 1.3.6.1.4.1.77.1.2.25',
            'snmpwalk -v2c -c public {ip} 1.3.6.1.2.1.25.1.6.0'
        ]
    },
    
    389: {
        'name': 'LDAP',
        'risk_base': 6.5,
        'enumeration': [
            'ldapsearch -x -H ldap://{ip} -s base',
            'nxc ldap {ip} -u "" -p "" -d {domain}',
            'ldapsearch -x -H ldap://{ip} -b "DC={domain_dc}" "(objectClass=*)" | head -50'
        ],
        'authentication': [
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --users --groups',
            'ldapsearch -x -H ldap://{ip} -D "{user}@{domain}" -w {pass} -b "DC={domain_dc}" "(objectClass=user)"'
        ],
        'escalation': [
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --kerberoasting /tmp/kerb_{ip}.txt',
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --asreproast /tmp/asrep_{ip}.txt',
            'nxc ldap {ip} -u {user} -p {pass} -d {domain} --bloodhound --collection All --dns-server {ip}'
        ]
    },
    
    443: {
        'name': 'HTTPS',
        'risk_base': 3.0,
        'enumeration': [
            'curl -sIk https://{ip} --max-time 10',
            'sslscan {ip}:443',
            'curl -sk https://{ip}/robots.txt'
        ],
        'escalation': [
            'feroxbuster -u https://{ip} -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -k -t 30 --silent --depth 2',
            'gobuster dir -u https://{ip} -w /usr/share/seclists/Discovery/Web-Content/common.txt -k -x php,html,txt,asp,aspx'
        ]
    },
    
    445: {
        'name': 'SMB',
        'risk_base': 9.0,
        'enumeration': [
            'nxc smb {ip} -u "" -p "" --shares',
            'smbclient -L //{ip}/ -N',
            'enum4linux-ng -A {ip}',
            'smbmap -H {ip} -u null -p null'
        ],
        'authentication': [
            'nxc smb {ip} -u {user} -p {pass} -d {domain} --shares',
            'smbclient -L //{ip}/ -U {user}%{pass}'
        ],
        'escalation': [
            'nxc smb {ip} -u {user} -p {pass} -d {domain} --sam --lsa',
            'smbmap -H {ip} -d {domain} -u {user} -p {pass} -R',
            'nxc smb {ip} -u {user} -p {pass} -M spider_plus -o READ_ONLY=false OUTPUT_FOLDER=/tmp/smb_files_{ip}',
            'nxc smb {ip} -u {user} -p {pass} --spider ADMIN\$ --pattern ".*\\.(txt|ini|cfg|conf|xml|log)$"',
            'nxc smb {ip} -u {user} -p {pass} --spider C\$ --pattern ".*\\.(txt|ini|cfg|conf|xml|log)$"',
            'nxc smb {ip} -u {user} -p {pass} --spider SYSVOL --pattern ".*\\.(txt|ini|cfg|conf|xml|log|bat|ps1)$"'
        ],
        'vulnerabilities': [
            'nxc smb {ip} -u "" -p "" -M zerologon',
            'nxc smb {ip} -u "" -p "" -M petitpotam',
            'nxc smb {ip} -u "" -p "" -M ms17-010'
        ]
    },
    
    1433: {
        'name': 'MSSQL',
        'risk_base': 8.0,
        'enumeration': ['nxc mssql {ip} -u "" -p ""'],
        'authentication': [
            'nxc mssql {ip} -u {user} -p {pass}',
            'nxc mssql {ip} -u {user} -p {pass} -q "SELECT @@version"'
        ],
        'escalation': [
            'nxc mssql {ip} -u {user} -p {pass} -q "SELECT name FROM master.dbo.sysdatabases"',
            'nxc mssql {ip} -u {user} -p {pass} --local-auth'
        ]
    },
    
    3306: {
        'name': 'MySQL',
        'risk_base': 7.0,
        'enumeration': ['nxc mysql {ip} -u "" -p ""'],
        'authentication': [
            'nxc mysql {ip} -u {user} -p {pass}',
            'mysql -h {ip} -u {user} -p{pass} -e "SELECT version();"'
        ]
    },
    
    3389: {
        'name': 'RDP',
        'risk_base': 8.5,
        'enumeration': [
            'nxc rdp {ip} -u "" -p ""',
            'rdesktop-vrdp {ip}'
        ],
        'authentication': [
            'nxc rdp {ip} -u {user} -p {pass}',
            'nxc rdp {ip} -u {user} -p {pass} --screenshot'
        ]
    },
    
    5432: {
        'name': 'PostgreSQL',
        'risk_base': 7.0,
        'enumeration': ['nxc postgres {ip} -u "" -p ""'],
        'authentication': [
            'nxc postgres {ip} -u {user} -p {pass}',
            'psql -h {ip} -U {user} -d postgres -c "SELECT version();"'
        ]
    },
    
    5985: {
        'name': 'WinRM',
        'risk_base': 7.5,
        'enumeration': [
            'nxc winrm {ip} -u "" -p ""',
            'curl -s http://{ip}:5985/wsman'
        ],
        'authentication': [
            'nxc winrm {ip} -u {user} -p {pass}',
            'evil-winrm -i {ip} -u {user} -p {pass}'
        ],
        'escalation': [
            'nxc winrm {ip} -u {user} -p {pass} -x "whoami /all"',
            'nxc winrm {ip} -u {user} -p {pass} -x "systeminfo"',
            'nxc winrm {ip} -u {user} -p {pass} -x "net localgroup administrators"'
        ]
    },
    
    6379: {
        'name': 'Redis',
        'risk_base': 9.0,
        'enumeration': [
            'redis-cli -h {ip} -p 6379 info',
            'nxc redis {ip}'
        ],
        'escalation': [
            'redis-cli -h {ip} -p 6379 config get "*"',
            'redis-cli -h {ip} -p 6379 keys "*"'
        ]
    }
}

GENERIC_CHECKS = {
    'name': 'Generic',
    'risk_base': 5.0,
    'enumeration': ['nc -v -n -w 5 {ip} {port}']
}

class GracefulShutdown:
    def __init__(self):
        self.shutdown = False
        self.cleanup_files = []
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        atexit.register(self.cleanup)
        
    def exit_gracefully(self, signum, frame):
        print(f"\n[!] Shutdown signal received...")
        self.shutdown = True
        self.cleanup()
        sys.exit(0)
        
    def cleanup(self):
        for filepath in self.cleanup_files:
            try:
                if os.path.exists(filepath) and os.path.getsize(filepath) < 1000:
                    os.remove(filepath)
            except:
                pass
                
    def add_cleanup_file(self, filepath):
        self.cleanup_files.append(filepath)

class EnterpriseScanner:
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.risk_scores = {}
        self.nmap_intelligence = {}
        self.start_time = datetime.now()
        self.shutdown_handler = GracefulShutdown()
        self.attack_paths = []
        self.findings = set()  # Use set to avoid duplicates
        self.processed_findings = set()  # Track processed findings to avoid duplicates
        
    def banner(self):
        """Display professional banner"""
        print(f"""
\033[96m┌─────────────────────────────────────────────────────────────┐
│                          CHAINSAW                           │
│                         CTF Scanner                         │
│                      v2.0 Professional                      │
└─────────────────────────────────────────────────────────────┘\033[0m

Target: {self.args.ip}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """)

    def clean_output(self, output):
        """Clean command output to remove junk text and duplicates"""
        if not output or len(output.strip()) < 3:
            return "No meaningful output"
        
        lines = output.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        # Filter out noise and duplicates
        noise_patterns = [
            r'working on it',
            r'please wait', 
            r'loading',
            r'^\s*$',
            r'^\s*\.*\s*$',
            r'connection.*timeout',
            r'no route to host',
            r'network is unreachable',
            r'Error retrieving os arch',
            r'Traceback \(most recent call last\)',
            r'Exception while calling proto_flow',
            r'╭──.*?─+╮',
            r'│.*?│',
            r'╰──.*?─+╯'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip if we've seen this line before
            if line in seen_lines:
                continue
            seen_lines.add(line)
            
            # Check if line matches noise patterns
            is_noise = False
            for pattern in noise_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_noise = True
                    break
            
            if not is_noise and len(line) > 2:
                cleaned_lines.append(line)
                
        # Limit output to reasonable size
        if len(cleaned_lines) > 30:
                cleaned_lines = cleaned_lines[:20] + ['... (output truncated for readability) ...'] + cleaned_lines[-5:]
            
        result = '\n'.join(cleaned_lines)
        return result if result.strip() else "Command executed but produced no meaningful output"
    
    def extract_findings(self, output, command, port):
        """Extract key findings from command output - deduplicated"""
        findings = []
        output_lower = output.lower()
        
        # Create unique finding identifier
        finding_key = f"{port}_{command.split()[0] if command.split() else 'unknown'}"
        
        # SMB findings
        if 'smb' in command.lower():
                if 'signing:false' in output_lower or 'message signing disabled' in output_lower:
                    finding = f"SMB Signing Disabled (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
                if 'guest account' in output_lower or 'guest login' in output_lower:
                    finding = f"SMB Guest Access Enabled (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
                if 'ipc$' in output_lower and 'read' in output_lower:
                    finding = f"IPC$ Share Accessible (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
                if ('admin$' in output_lower or 'c$' in output_lower) and ('read' in output_lower or 'write' in output_lower):
                    finding = f"Administrative Shares Found (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
        # Authentication success findings
        if any(success in output_lower for success in ['pwn3d!', '[+]', 'success', 'authenticated']):
                if self.args.user and self.args.password:  # Only show if we provided creds
                    finding = f"Authentication Successful - {self.args.user} (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
        # Domain Controller findings
        if 'domain controller' in output_lower or ('ldap' in command.lower() and 'dc=' in output_lower):
                finding = f"Domain Controller Identified (Port {port})"
                if finding not in self.processed_findings:
                    findings.append(finding)
                    self.processed_findings.add(finding)
                    
        # Kerberos findings
        if ('kerberoast' in output_lower or 'asreproast' in output_lower) and 'total of records returned' in output_lower:
                finding = f"Kerberos Attack Vectors Available (Port {port})"
                if finding not in self.processed_findings:
                    findings.append(finding)
                    self.processed_findings.add(finding)
                    
        # Web findings
        if any(web in command.lower() for web in ['http', 'curl', 'feroxbuster', 'gobuster']):
                if '200' in output and 'admin' in output_lower:
                    finding = f"Admin Panel Found (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
                if 'login' in output_lower and '200' in output:
                    finding = f"Login Portal Found (Port {port})"
                    if finding not in self.processed_findings:
                        findings.append(finding)
                        self.processed_findings.add(finding)
                        
        # Database findings
        if any(db in command.lower() for db in ['mysql', 'mssql', 'postgres']) and '[+]' in output:
                finding = f"Database Access Granted (Port {port})"
                if finding not in self.processed_findings:
                    findings.append(finding)
                    self.processed_findings.add(finding)
                    
        return findings
    
    def run_cmd_enhanced(self, cmd, timeout=30):
        """Enhanced command execution with better error handling"""
        try:
                if self.shutdown_handler.shutdown:
                    return {'command': cmd, 'output': 'Interrupted', 'success': False}
            
                # Handle interactive commands
                if any(interactive_cmd in cmd.lower() for interactive_cmd in ['ssh', 'telnet', 'nc -nv', 'nc -v']):
                    if 'ssh' in cmd:
                        cmd += ' -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no'
                    elif 'telnet' in cmd:
                        cmd = f'timeout {min(timeout, 15)} {cmd}'
                    elif 'nc' in cmd and '-v' in cmd:
                        if '-w' not in cmd:
                                cmd = cmd.replace('-v', '-v -w 5')
                            
                # Add quiet flags to reduce noise
                if 'smbmap' in cmd and '-q' not in cmd:
                    cmd += ' 2>/dev/null'
                    
                # Handle ntds dumping prompt
                if '--ntds' in cmd and '--users' not in cmd:
                    cmd = cmd.replace('--ntds', '--ntds --users')
                    
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    stdin=subprocess.DEVNULL
                )
            
                # Clean the output
                raw_output = f"{result.stdout}\n{result.stderr}".strip()
                cleaned_output = self.clean_output(raw_output)
            
                return {
                    'command': cmd,
                    'output': cleaned_output,
                    'success': result.returncode == 0,
                    'return_code': result.returncode
                }
        except subprocess.TimeoutExpired:
                return {
                    'command': cmd,
                    'output': f"Command timed out after {timeout} seconds",
                    'success': False,
                    'return_code': -1
                }
        except Exception as e:
                return {
                    'command': cmd,
                    'output': f"Error: {str(e)}",
                    'success': False,
                    'return_code': -2
                }
        
    def fast_nmap_scan(self, ip):
        """FAST nmap scan with proper domain extraction"""
        print(f"[*] Running nmap scan on {ip}...")
        
        # More targeted nmap scan
        nmap_cmd = f"nmap -T4 --top-ports 1000 -sV {ip}"
        nmap_result = self.run_cmd_enhanced(nmap_cmd, timeout=300)
        
        # Store nmap intelligence
        self.nmap_intelligence = {
                'raw_output': nmap_result['output'],
                'command': nmap_result['command'],
                'timestamp': datetime.now()
        }
        
        # Extract domain and ports
        discovered_domain = self.extract_domain_from_scan(nmap_result['output'])
        open_ports = self.parse_nmap_enhanced(nmap_result['output'])
        
        if not open_ports:
                print("[!] No open ports found. Exiting.")
                return [], None
        
        print(f"[+] Discovered {len(open_ports)} open ports: {[p[0] for p in open_ports]}")
        if discovered_domain:
                print(f"[+] Discovered domain: {discovered_domain}")
        else:
                print(f"[!] No domain discovered, using IP for domain-specific attacks")
            
        return open_ports, discovered_domain
    
    def parse_nmap_enhanced(self, output):
        """Parse nmap output to extract open ports"""
        open_ports = []
        lines = output.split('\n')
        
        for line in lines:
                if '/tcp' in line and ('open' in line or 'filtered' in line):
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                                port_proto = parts[0]
                                port = int(port_proto.split('/')[0])
                                service = parts[2] if len(parts) > 2 else 'unknown'
                                open_ports.append((port, service))
                        except:
                                continue
                        
        return open_ports
    
    def extract_domain_from_scan(self, nmap_output):
        """Extract domain from nmap service detection output"""
        
        # Look for LDAP service lines with domain info
        pattern = r'Microsoft Windows Active Directory LDAP \(Domain:\s*([^,\)]+)'
        
        matches = re.findall(pattern, nmap_output, re.IGNORECASE)
        
        for match in matches:
            domain = match.strip()
            
            # Clean up the domain - remove trailing "0." and other artifacts
            domain = re.sub(r'0\.$', '', domain)  # Remove "0." at end
            domain = domain.rstrip('.')           # Remove any trailing dots
            domain = domain.strip()               # Remove whitespace
            
            # Validate it's a real domain
            if domain and '.' in domain and len(domain) > 3:
                print(f"[+] Found domain: {domain}")
                return domain
            
        print("[!] No domain found in nmap output")
        return None
    
    def calculate_risk_score(self, port, service_results):
        """Calculate risk scores based on findings"""
        config = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS)
        base_score = config.get('risk_base', 5.0)
        
        # Increase score for successful authentication
        auth_success = any(result.get('success', False) and 'auth' in str(result.get('command', ''))
                                for result in service_results)
        if auth_success:
                base_score += 1.5
            
        # Increase score for specific findings
        if any('admin' in str(result.get('output', '')).lower() for result in service_results):
                base_score += 1.0
            
        return min(base_score, 10.0)
    
    def analyze_attack_paths(self, results):
        """Analyze attack paths"""
        attack_paths = []
        open_ports = list(results.keys())
        
        # Check for credential reuse opportunities
        login_services = [p for p in open_ports if p in [21, 22, 445, 3389, 5985]]
        if len(login_services) > 1:
                attack_paths.append({
                    'type': 'CREDENTIAL_REUSE',
                    'description': f'Multiple authentication services detected on ports {login_services}',
                    'severity': 'HIGH',
                    'ports': login_services
                })
            
        # Check for domain controller services
        if 88 in open_ports and 389 in open_ports and 445 in open_ports:
                attack_paths.append({
                    'type': 'DOMAIN_CONTROLLER',
                    'description': 'Domain Controller detected - high value target',
                    'severity': 'CRITICAL',
                    'ports': [88, 389, 445]
                })
            
        return attack_paths
    
    def service_checks_enhanced(self, ip, port, user=None, password=None, replacements=None):
        """Enhanced service-specific testing with deduplication"""
        config = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS)
        results = []
        
        print(f"[*] Testing port {port} ({config.get('name', 'Unknown')})...")
        
        # Set up replacements
        if replacements:
                replacements['user'] = user if user else ""
                replacements['pass'] = password if password else ""
                if not replacements.get('domain') or replacements['domain'] == ip:
                    replacements['domain'] = ip
                    
                # Set up domain_dc for LDAP queries
                if replacements.get('domain') and replacements['domain'] != ip:
                    replacements['domain_dc'] = ','.join([f"DC={part}" for part in replacements['domain'].split('.')])
                else:
                    replacements['domain_dc'] = ''
                    
        # Only run enumeration if no creds provided, or auth/escalation if creds provided
        check_types = ['enumeration']
        if user and password:
                check_types.extend(['authentication', 'escalation', 'vulnerabilities'])
            
        executed_commands = set()  # Track executed commands to avoid duplicates
        
        for check_type in check_types:
                if check_type in config:
                    checks = config[check_type] if isinstance(config[check_type], list) else [config[check_type]]
                    
                    for check in checks:
                        try:
                                # Validate tool exists
                                tool = check.split()[0]
                                if not shutil.which(tool):
                                    continue
                            
                                processed_cmd = check.format(**replacements)
                            
                                # Skip duplicate commands
                                if processed_cmd in executed_commands:
                                    continue
                                executed_commands.add(processed_cmd)
                            
                                result = self.run_cmd_enhanced(processed_cmd, timeout=60)
                            
                                # Only add result if it has meaningful output
                                if result['output'] and "No meaningful output" not in result['output']:
                                    results.append(result)
                                    
                                # Extract findings from output
                                port_findings = self.extract_findings(result['output'], processed_cmd, port)
                                self.findings.update(port_findings)
                            
                        except KeyError as e:
                                continue
                        except Exception as e:
                                continue
                        
                        if self.shutdown_handler.shutdown:
                                break
                        
                    if self.shutdown_handler.shutdown:
                        break
                    
        print(f"[+] Completed {len(results)} tests on port {port}")
        return results
    
    def get_risk_class(self, score):
        """Get CSS risk class based on score"""
        if score >= 9.0:
                return 'critical'
        elif score >= 7.0:
                return 'high'
        elif score >= 5.0:
                return 'medium'
        else:
                return 'low'
        
    def get_overall_threat_level(self):
        """Calculate overall threat level"""
        if not self.risk_scores:
                return 'LOW', 'ACCEPTABLE'
        
        max_score = max(self.risk_scores.values())
        critical_count = sum(1 for score in self.risk_scores.values() if score >= 9.0)
        high_count = sum(1 for score in self.risk_scores.values() if score >= 7.0)
        
        if critical_count > 0 or max_score >= 9.0:
                return 'CRITICAL', 'COMPROMISED'
        elif high_count > 1 or max_score >= 8.0:
                return 'HIGH', 'ELEVATED'
        elif high_count > 0 or max_score >= 7.0:
                return 'ELEVATED', 'CONCERNING'
        else:
                return 'LOW', 'ACCEPTABLE'
        
    def generate_enhanced_report(self, results, ip):
        """Generate clean, professional HTML report"""
        threat_level, status = self.get_overall_threat_level()
        
        # Calculate statistics
        total_ports = len(results)
        critical_ports = [p for p, score in self.risk_scores.items() if score >= 9.0]
        high_ports = [p for p, score in self.risk_scores.items() if score >= 7.0 and score < 9.0]
        medium_ports = [p for p, score in self.risk_scores.items() if score >= 5.0 and score < 7.0]
        low_ports = [p for p, score in self.risk_scores.items() if score < 5.0]
        
        # Service summary
        service_summary = {}
        for port in results.keys():
                service_name = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'Generic')
                if service_name not in service_summary:
                    service_summary[service_name] = []
                service_summary[service_name].append(port)
            
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Chainsaw Scan - {ip}</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
                {MODERN_CSS}
        </head>
        <body>
                <div class="container">
                    <div class="header">
                        <h1>Chainsaw Results</h1>
                        <h2>Network Security Assessment</h2>
                    </div>
                    
                    <div class="status-bar">
                        <div class="status-item">
                                <strong>Target:</strong> {ip}
                        </div>
                        <div class="status-item">
                                <strong>Scan Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                        </div>
                        <div class="status-item">
                                <strong>Duration:</strong> {datetime.now() - self.start_time}
                        </div>
                        <div class="status-item">
                                <span class="badge badge-{'danger' if threat_level in ['CRITICAL'] else 'warning' if threat_level in ['HIGH', 'ELEVATED'] else 'success'}">
                                    {threat_level} RISK
                                </span>
                        </div>
                    </div>
                    
                    <div class="content">
                        <div class="summary-grid">
                                <div class="summary-card">
                                    <h3>Ports Discovered</h3>
                                    <div class="metric">{total_ports}</div>
                                    <div class="label">Total Open Ports</div>
                                </div>
                                
                                <div class="summary-card critical">
                                    <h3>Critical Risk</h3>
                                    <div class="metric danger">{len(critical_ports)}</div>
                                    <div class="label">Ports Requiring Immediate Attention</div>
                                </div>
                                
                                <div class="summary-card high">
                                    <h3>High Risk</h3>
                                    <div class="metric warning">{len(high_ports)}</div>
                                    <div class="label">Ports with Significant Exposure</div>
                                </div>
                                
                                <div class="summary-card low">
                                    <h3>Key Findings</h3>
                                    <div class="metric info">{len(self.findings)}</div>
                                    <div class="label">Security Issues Identified</div>
                                </div>
                        </div>
                        
                        <h2>Port Overview</h2>
                        <div class="port-grid">
        """
        
        # Add port cards
        for port in sorted(results.keys()):
                service_name = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'Generic')
                risk_score = self.risk_scores.get(port, 5.0)
                risk_class = self.get_risk_class(risk_score)
            
                html += f"""
                                <div class="port-card">
                                    <div class="port-number">{port}</div>
                                    <div class="port-service">{service_name}</div>
                                    <div class="risk-score risk-{risk_class}">{risk_score:.1f}/10</div>
                                </div>
                """
            
        html += """
                        </div>
        """
        
        # Key findings section
        if self.findings:
                html += f"""
                        <div class="findings-section">
                                <h2>Key Security Findings</h2>
                                <p>The following critical security issues were identified during the assessment:</p>
                """
            
                for i, finding in enumerate(sorted(self.findings), 1):
                    html += f"""
                                <div class="finding-item">
                                    <strong>#{i}</strong> {escape(finding)}
                                </div>
                    """
                    
                html += """
                        </div>
                """
            
        # Attack paths
        if self.attack_paths:
                html += """
                        <div class="findings-section">
                                <h2>Attack Vectors</h2>
                """
            
                for path in self.attack_paths:
                    html += f"""
                                <div class="finding-item">
                                    <strong>{path['type']} - {path['severity']}</strong><br>
                                    {escape(path['description'])}<br>
                                    <em>Affected Ports: {', '.join(map(str, path['ports']))}</em>
                                </div>
                    """
                    
                html += """
                        </div>
                """
            
        # Detailed service analysis
        for port, checks in results.items():
                if not checks:  # Skip ports with no meaningful results
                    continue
        
                service_name = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'UNKNOWN')
                risk_score = self.risk_scores.get(port, 5.0)
                risk_class = self.get_risk_class(risk_score)
        
                html += f"""
                        <div class="service-section">
                                <div class="service-header">
                                    <div class="service-title">Port {port} - {service_name}</div>
                                    <div class="risk-score risk-{risk_class}">Risk: {risk_score:.1f}/10</div>
                                </div>
                                <div class="service-content">
                """
        
                for check in checks:
                    if check.get('output') and "No meaningful output" not in check.get('output'):
                        html += f"""
                                    <div class="command-result">
                                        <div class="command-header">
                                                {escape(check.get('command', 'unknown'))}
                                        </div>
                                        <div class="command-output">{escape(check.get('output', 'NO OUTPUT')[:1500])}</div>
                                    </div>
                        """
                        
                html += """
                                </div>
                        </div>
                """
        
        # Footer
        html += f"""
                    </div>
                </div>
        </body>
        </html>
        """
        
        return html
    
    def run_scan(self):
        """Main scanning logic"""
        self.banner()
        
        # Single nmap scan
        open_ports, discovered_domain = self.fast_nmap_scan(self.args.ip)
        
        if not open_ports:
                return
        
        # Configure replacements
        domain_dc = ""
        if discovered_domain:
                domain_dc = ','.join([f"DC={part}" for part in discovered_domain.split('.')])
            
        replacements = {
                'ip': self.args.ip,
                'user': self.args.user or '',
                'pass': self.args.password or '',
                'domain': discovered_domain or self.args.ip,
                'domain_dc': domain_dc,
                'wordlist': self.args.wordlist or DEFAULT_WORDLISTS['dirbuster'],
                'port': '',
        }
        
        print(f"[*] Using domain: {replacements['domain']}")
        print(f"[*] Credentials provided: {'YES' if self.args.user and self.args.password else 'NO'}")
        
        # Parallel service scanning
        with ThreadPoolExecutor(max_workers=6) as executor:
                try:
                    futures = {}
                    for port, service in open_ports:
                        if self.shutdown_handler.shutdown:
                                break
                        
                        port_replacements = replacements.copy()
                        port_replacements['port'] = port
                        
                        future = executor.submit(
                                self.service_checks_enhanced, 
                                self.args.ip, port, self.args.user, self.args.password, port_replacements
                        )
                        futures[port] = future
                        
                    for port, future in futures.items():
                        try:
                                self.results[port] = future.result(timeout=120)
                                self.risk_scores[port] = self.calculate_risk_score(port, self.results[port])
                        except Exception as e:
                                print(f"[!] Error scanning port {port}: {str(e)}")
                                self.results[port] = []
                                self.risk_scores[port] = 0.0
                            
                except KeyboardInterrupt:
                    print("[!] Shutting down gracefully...")
                    executor.shutdown(wait=False)
                    raise
                    
        # Analyze attack paths
        self.attack_paths = self.analyze_attack_paths(self.results)
        
        # Print summary
        if self.findings:
                print(f"\n[!] Key Findings:")
                for i, finding in enumerate(sorted(self.findings), 1):
                    print(f"  #{i} {finding}")
                    
        # Generate report
        report = self.generate_enhanced_report(self.results, self.args.ip)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"chainsaw_scan_{self.args.ip}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
                self.shutdown_handler.add_cleanup_file(filename)
                f.write(report)
            
        print(f"\n[+] Chainsaw complete: {filename}")
        print(f"[+] Found {len(self.findings)} security issues across {len(self.results)} ports")
        
        # Open browser if requested
        if not self.args.no_browser:
                webbrowser.open(f"file://{os.path.abspath(filename)}")
            
def main():
    try:
        # Check tools
        check_and_install_tools()
        
        parser = argparse.ArgumentParser(
                description='Chainsaw CTF Network Scanner v2.0',
                epilog="""
Examples: 
python3 chainsaw.py 192.168.1.1 --no-browser -w wordlist.txt
python3 chainsaw.py target.com -u admin -p password 
                """
        )
        
        parser.add_argument('ip', help='Target IP address or hostname')
        parser.add_argument('-u', '--user', help='Username for authentication')
        parser.add_argument('-p', '--password', help='Password for authentication')
        parser.add_argument('-w', '--wordlist', help='Custom wordlist path')
        parser.add_argument('--no-browser', action='store_true', help='Do not open report in browser')
        
        args = parser.parse_args()
        
        # Create and run scanner
        scanner = EnterpriseScanner(args)
        scanner.run_scan()
        
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")
        
if __name__ == '__main__':
    main()
