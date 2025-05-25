#!/usr/bin/env python3
import argparse
import subprocess
import os
import webbrowser
import re
import json
import asyncio
import aiohttp
from html import escape
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
import threading
from pathlib import Path

# =====================
#  STYLING
# =====================
class CyberColors:
    NEON_GREEN = '#39FF14'
    NEON_PINK = '#FF10F0'
    NEON_BLUE = '#00F3FF'
    MATRIX_GREEN = '#20C20E'
    DARK_BG = '#0A0A0A'
    NEON_ORANGE = '#FF4500'
    CYBER_PURPLE = '#8A2BE2'

TERMINAL_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu+Mono&family=Press+Start+2P&family=Orbitron:wght@400;700&display=swap');
    
    body {{
        background-color: {CyberColors.DARK_BG};
        background-image: 
            radial-gradient(circle at 25% 25%, #001100 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, #000033 0%, transparent 50%);
        color: {CyberColors.NEON_GREEN};
        font-family: 'Ubuntu Mono', monospace;
        margin: 2rem;
        min-height: 100vh;
    }}
    
    .glitch {{
        font-family: 'Orbitron', 'Press Start 2P', cursive;
        color: {CyberColors.NEON_BLUE};
        text-shadow: 3px 3px {CyberColors.NEON_PINK}, -2px -2px {CyberColors.NEON_ORANGE};
        animation: glitch 2s infinite;
        font-weight: 700;
    }}
    
    @keyframes glitch {{
        0% {{ text-shadow: 3px 3px {CyberColors.NEON_PINK}, -2px -2px {CyberColors.NEON_ORANGE}; }}
        25% {{ text-shadow: -3px 3px {CyberColors.NEON_ORANGE}, 2px -2px {CyberColors.NEON_PINK}; }}
        50% {{ text-shadow: 3px -3px {CyberColors.NEON_BLUE}, -2px 2px {CyberColors.NEON_GREEN}; }}
        75% {{ text-shadow: -3px -3px {CyberColors.NEON_GREEN}, 2px 2px {CyberColors.NEON_BLUE}; }}
        100% {{ text-shadow: 3px 3px {CyberColors.NEON_PINK}, -2px -2px {CyberColors.NEON_ORANGE}; }}
    }}
    
    .service {{
        background: linear-gradient(135deg, rgba(10, 10, 10, 0.9), rgba(0, 20, 20, 0.8));
        border: 2px solid {CyberColors.NEON_BLUE};
        border-radius: 10px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 
            0 0 20px {CyberColors.NEON_BLUE},
            inset 0 0 20px rgba(0, 243, 255, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .service::before {{
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, {CyberColors.NEON_BLUE}, {CyberColors.NEON_PINK}, {CyberColors.NEON_GREEN});
        z-index: -1;
        border-radius: 10px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .service:hover {{
        transform: translateX(15px) scale(1.02);
        box-shadow: 
            0 0 30px {CyberColors.NEON_PINK},
            inset 0 0 30px rgba(255, 16, 240, 0.1);
    }}
    
    .service:hover::before {{
        opacity: 0.7;
    }}
    
    .risk-critical {{
        border-color: {CyberColors.NEON_PINK} !important;
        box-shadow: 0 0 25px {CyberColors.NEON_PINK} !important;
    }}
    
    .risk-high {{
        border-color: {CyberColors.NEON_ORANGE} !important;
        box-shadow: 0 0 20px {CyberColors.NEON_ORANGE} !important;
    }}
    
    .risk-medium {{
        border-color: {CyberColors.NEON_BLUE} !important;
    }}
    
    .risk-low {{
        border-color: {CyberColors.NEON_GREEN} !important;
    }}
    
    pre {{
        background: linear-gradient(135deg, #001100, #000022);
        color: {CyberColors.MATRIX_GREEN};
        padding: 1.5rem;
        border-left: 4px solid {CyberColors.NEON_GREEN};
        border-radius: 5px;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'Ubuntu Mono', monospace;
        box-shadow: inset 0 0 10px rgba(32, 194, 14, 0.1);
    }}
    
    .success {{
        color: {CyberColors.NEON_GREEN} !important;
        text-shadow: 0 0 15px {CyberColors.NEON_GREEN};
        font-weight: bold;
    }}
    
    .fail {{
        color: {CyberColors.NEON_PINK} !important;
        text-shadow: 0 0 15px {CyberColors.NEON_PINK};
        font-weight: bold;
    }}
    
    .warning {{
        color: {CyberColors.NEON_ORANGE} !important;
        text-shadow: 0 0 15px {CyberColors.NEON_ORANGE};
        font-weight: bold;
    }}
    
    .scan-line {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            to bottom,
            rgba(57, 255, 20, 0) 0%,
            rgba(57, 255, 20, 0.05) 48%,
            rgba(57, 255, 20, 0.1) 50%,
            rgba(57, 255, 20, 0.05) 52%,
            rgba(57, 255, 20, 0) 100%
        );
        animation: scan 6s linear infinite;
        pointer-events: none;
        z-index: 1000;
    }}
    
    @keyframes scan {{
        0% {{ transform: translateY(-100vh); }}
        100% {{ transform: translateY(100vh); }}
    }}
    
    .terminal-header {{
        border: 3px solid {CyberColors.NEON_BLUE};
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.1), rgba(255, 16, 240, 0.1));
        padding: 2rem;
        margin-bottom: 3rem;
        position: relative;
        border-radius: 10px;
        box-shadow: 0 0 30px {CyberColors.NEON_BLUE};
    }}
    
    .terminal-header::before {{
        content: "▲▼▲▼ CYBERSCAN NETWORK ANALYSIS ▲▼▲▼";
        position: absolute;
        top: -20px;
        left: 30px;
        background: {CyberColors.DARK_BG};
        padding: 0 15px;
        font-size: 0.9em;
        font-family: 'Orbitron', cursive;
        color: {CyberColors.NEON_BLUE};
        text-shadow: 0 0 10px {CyberColors.NEON_BLUE};
    }}
    
    .attack-path {{
        background: linear-gradient(135deg, rgba(255, 16, 240, 0.2), rgba(255, 69, 0, 0.1));
        border: 2px dashed {CyberColors.NEON_PINK};
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 10px {CyberColors.NEON_PINK}; }}
        50% {{ box-shadow: 0 0 25px {CyberColors.NEON_PINK}; }}
        100% {{ box-shadow: 0 0 10px {CyberColors.NEON_PINK}; }}
    }}
    
    .risk-score {{
        font-size: 1.5em;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem;
        font-family: 'Orbitron', cursive;
    }}
    
    .executive-summary {{
        background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(0, 243, 255, 0.1));
        border: 3px solid {CyberColors.CYBER_PURPLE};
        padding: 2rem;
        margin: 2rem 0;
        border-radius: 15px;
        box-shadow: 0 0 25px {CyberColors.CYBER_PURPLE};
    }}
</style>
"""

# =====================
# ENHANCED PENTEST CONFIGURATION
# =====================
DEFAULT_WORDLISTS = {
    'dirbuster': '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
    'feroxbuster': '/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt',
    'snmp': '/usr/share/wordlists/dict.txt',
    'users': 'users.txt',
    'passwords': 'passwords.txt',
    'api': '/usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints.txt',
    'subdomains': '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt'
}

API_ENDPOINTS = [
    '/api/v1/', '/api/v2/', '/api/v3/', '/graphql', '/swagger/', '/swagger.json',
    '/health', '/metrics', '/.well-known/', '/admin/', '/debug/', '/dev/',
    '/actuator/', '/jolokia/', '/management/', '/status'
]

# Enhanced service configuration with modern protocols
ENHANCED_SERVICE_CHECKS = {
    # Traditional services
    21: {
        'name': 'FTP',
        'risk_base': 8.5,
        'anon': [
            'curl -v ftp://{ip} --max-time 10',
            'ftp -inv {ip} <<< "user anonymous anonymous"',
            'nmap --script=ftp-anon -p 21 {ip}'
        ],
        'auth': 'ftp -inv {ip} -u {user} -p {pass}',
        'enum': [
            'nmap --script=ftp-* -p 21 {ip}',
            'wget -m ftp://{user}:{pass}@{ip} --timeout=10'
        ],
        'fallback': [
            'nc -vn {ip} 21 <<< "USER anonymous"'
        ]
    },
    
    22: {
        'name': 'SSH',
        'risk_base': 6.0,
        'auth': 'ssh {user}@{ip} -o PasswordAuthentication=yes -o ConnectTimeout=10',
        'enum': [
            'ssh -v {user}@{ip} -o ConnectTimeout=10',
            'nmap --script=ssh-* -p 22 {ip}',
            'ssh-keyscan -p 22 {ip}'
        ],
        'fallback': [
            'hydra -L {users} -P {passwords} ssh://{ip} -t 4 -f'
        ]
    },
    
    # Web services
    80: {
        'name': 'HTTP',
        'risk_base': 5.0,
        'enum': [
            'gobuster dir -u http://{ip} -w {dirbuster_wordlist} -t 50 --timeout 10s',
            'nikto -h http://{ip} -timeout 10',
            'whatweb -a3 http://{ip}',
            'curl -I http://{ip} --max-time 5'
        ],
        'fallback': [
            'feroxbuster -u http://{ip} -w {ferox_wordlist} -t 50'
        ]
    },
    
    443: {
        'name': 'HTTPS',
        'risk_base': 5.0,
        'enum': [
            'testssl.sh {ip} --fast',
            'gobuster dir -u https://{ip} -w {dirbuster_wordlist} -k -t 50',
            'sslscan {ip}:443',
            'curl -I https://{ip} -k --max-time 5'
        ],
        'fallback': [
            'openssl s_client -connect {ip}:443 -servername {ip}'
        ]
    },
    
    # Alternative HTTP ports
    8080: {
        'name': 'HTTP-Proxy',
        'risk_base': 6.0,
        'enum': [
            'gobuster dir -u http://{ip}:8080 -w {dirbuster_wordlist} -t 50',
            'curl -I http://{ip}:8080 --max-time 5',
            'gobuster dir -u http://{ip}:8080/api -w {api_wordlist} -t 50'
        ],
        'fallback': [
            'feroxbuster -u http://{ip}:8080 -w {ferox_wordlist} -t 50'
        ]
    },
    
    8443: {
        'name': 'HTTPS-Alt',
        'risk_base': 6.0,
        'enum': [
            'testssl.sh {ip}:8443 --fast',
            'curl -I https://{ip}:8443 -k --max-time 5'
        ]
    },
    
    # SMB/NetBIOS
    445: {
        'name': 'SMB',
        'risk_base': 9.0,
        'anon': [
            'smbclient -L //{ip}/ -N --timeout=10',
            'crackmapexec smb {ip} --shares -u "" -p "" --timeout 10',
            'nmap --script=smb-os-discovery -p 445 {ip}'
        ],
        'auth': 'crackmapexec smb {ip} -u {user} -p {pass} --shares',
        'enum': [
            'enum4linux -a {ip}',
            'nmap --script=smb-* -p 445 {ip}',
            'smbmap -H {ip} -u null'
        ],
        'fallback': [
            'rpcclient -U "{user}%{pass}" {ip}',
            'python3 -c "import subprocess; subprocess.run([\'impacket-smbexec\', \'{user}:{pass}@{ip}\'])"'
        ]
    },
    
    # Remote access
    3389: {
        'name': 'RDP',
        'risk_base': 7.5,
        'enum': [
            'nmap --script=rdp-* -p 3389 {ip}',
            'crackmapexec rdp {ip} -u {user} -p {pass} --timeout 10'
        ],
        'fallback': [
            'xfreerdp /v:{ip} /u:{user} /p:{pass} +auth-only /timeout:10000'
        ]
    },
    
    5985: {
        'name': 'WinRM',
        'risk_base': 8.0,
        'auth': [
            'evil-winrm -i {ip} -u {user} -p {pass}',
            'crackmapexec winrm {ip} -u {user} -p {pass} -x "whoami"'
        ],
        'fallback': [
            'python3 -c "import subprocess; subprocess.run([\'impacket-wmiexec\', \'{user}:{pass}@{ip}\'])"'
        ]
    },
    
    # Databases
    3306: {
        'name': 'MySQL',
        'risk_base': 7.0,
        'auth': 'mysql -h {ip} -u {user} -p{pass} -e "SHOW DATABASES;" --connect-timeout=10',
        'enum': [
            'nmap --script=mysql-* -p 3306 {ip}',
            'crackmapexec mysql {ip} -u {user} -p {pass}'
        ],
        'fallback': [
            'mysqldump -h {ip} -u {user} -p{pass} --all-databases --single-transaction'
        ]
    },
    
    5432: {
        'name': 'PostgreSQL',
        'risk_base': 7.0,
        'auth': 'psql -h {ip} -U {user} -c "\\l" --set=statement_timeout=10s',
        'enum': [
            'nmap --script=pgsql-* -p 5432 {ip}',
            'crackmapexec postgres {ip} -u {user} -p {pass}'
        ]
    },
    
    # NoSQL databases
    27017: {
        'name': 'MongoDB',
        'risk_base': 8.0,
        'anon': [
            'mongo {ip}:27017 --eval "db.stats()" --quiet',
            'nmap --script=mongodb-* -p 27017 {ip}'
        ],
        'enum': [
            'mongo {ip}:27017/{user} --eval "db.runCommand({{connectionStatus : 1}})"'
        ]
    },
    
    6379: {
        'name': 'Redis',
        'risk_base': 9.0,
        'anon': [
            'redis-cli -h {ip} -p 6379 info',
            'nmap --script=redis-* -p 6379 {ip}'
        ],
        'enum': [
            'redis-cli -h {ip} -p 6379 --scan',
            'redis-cli -h {ip} -p 6379 CONFIG GET "*"'
        ]
    },
    
    # Search engines
    9200: {
        'name': 'Elasticsearch',
        'risk_base': 8.5,
        'anon': [
            'curl http://{ip}:9200/_cluster/health --max-time 5',
            'curl http://{ip}:9200/_cat/indices --max-time 5'
        ],
        'enum': [
            'nmap --script=http-elasticsearch-info -p 9200 {ip}'
        ]
    },
    
    # Container/Cloud services
    2375: {
        'name': 'Docker',
        'risk_base': 9.5,
        'anon': [
            'docker -H tcp://{ip}:2375 info',
            'curl http://{ip}:2375/version --max-time 5'
        ],
        'enum': [
            'docker -H tcp://{ip}:2375 ps -a',
            'nmap --script=docker-version -p 2375 {ip}'
        ]
    },
    
    2376: {
        'name': 'Docker-TLS',
        'risk_base': 7.0,
        'enum': [
            'docker --tlsverify -H tcp://{ip}:2376 info',
            'openssl s_client -connect {ip}:2376'
        ]
    },
    
    # Other services
    161: {
        'name': 'SNMP',
        'risk_base': 6.0,
        'anon': [
            'snmpwalk -v1 -c public {ip} --timeout=10',
            'onesixtyone -c {snmp_wordlist} {ip}',
            'nmap --script=snmp-* -p 161 {ip}'
        ],
        'fallback': [
            'snmp-check {ip} -c public'
        ]
    },
    
    389: {
        'name': 'LDAP',
        'risk_base': 6.5,
        'anon': [
            'ldapsearch -x -H ldap://{ip} -s base',
            'crackmapexec ldap {ip} --timeout 10'
        ],
        'fallback': [
            'nmap --script=ldap-* -p 389 {ip}'
        ]
    }
}

GENERIC_CHECKS = {
    'name': 'Generic',
    'risk_base': 5.0,
    'enum': [
        'nc -v -n -w 5 {ip} {port}',
        'curl -I http://{ip}:{port} --max-time 5',
        'nmap -sV -p {port} --script="banner,(safe or default) and not broadcast" {ip}'
    ],
    'fallback': [
        'telnet {ip} {port}',
        'socat - TCP:{ip}:{port},connect-timeout=5'
    ]
}

# Integration configurations
INTEGRATION_COMMANDS = {
    'slack_notify': 'curl -X POST -H "Content-type: application/json" --data \'{"text":"🔥 CyberScan complete for {ip} - {critical_count} critical findings"}\' {slack_webhook}',
    'jira_ticket': 'curl -X POST -u {jira_user}:{jira_token} -H "Content-Type: application/json" --data \'{"fields": {"project": {"key": "SEC"}, "summary": "Security vulnerabilities found on {ip}", "description": "Automated scan found {total_issues} issues"}}\' {jira_url}/rest/api/2/issue/',
    'teams_notify': 'curl -X POST -H "Content-Type: application/json" --data \'{"text": "CyberScan Alert: {critical_count} critical vulnerabilities found on {ip}"}\' {teams_webhook}',
    'discord_notify': 'curl -X POST -H "Content-Type: application/json" --data \'{"embeds": [{"title": "🔥 CyberScan Alert", "description": "Target: {ip}\\nCritical Issues: {critical_count}\\nTotal Issues: {total_issues}", "color": 15548997, "footer": {"text": "CyberScan Network Analysis"}}]}\' {discord_webhook}',
    'ifttt_trigger': 'curl -X POST -H "Content-Type: application/json" --data \'{"value1": "{ip}", "value2": "{critical_count}", "value3": "{total_issues}"}\' https://maker.ifttt.com/trigger/{ifttt_event}/with/key/{ifttt_key}'
}

class CyberScanner:
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.attack_paths = []
        self.risk_scores = {}
        self.start_time = datetime.now()
        
    def banner(self):
        banner_text = f"""
    {chr(27)}[91m
                        ██████╗ ██╗  ██╗ █████╗ ██╗███╗   ██╗███████╗ █████╗ ██╗    ██╗
                        ██╔════╝██║  ██║██╔══██╗██║████╗  ██║██╔════╝██╔══██╗██║    ██║
                        ██║     ███████║███████║██║██╔██╗ ██║███████╗███████║██║ █╗ ██║
                        ██║     ██╔══██║██╔══██║██║██║╚██╗██║╚════██║██╔══██║██║███╗██║
                        ╚██████╗██║  ██║██║  ██║██║██║ ╚████║███████║██║  ██║╚███╔███╔╝
                        ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ 

                              ⚡ AUTOMATED NETWORK TESTING FRAMEWORK ⚡
    {chr(27)}[0m{chr(27)}[93m
                            ────────────────────────────────────────
                              [!] TARGET ACQUIRED - INITIATING SCAN
                            ────────────────────────────────────────
    {chr(27)}[0m
            """
        print(banner_text)
        print(banner_text)
        
    def run_cmd_enhanced(self, cmd, timeout=30):
        """Enhanced command execution with better error handling"""
        try:
            # Add evasion delays if enabled
            if self.args.evasion:
                time.sleep(random.uniform(0.5, 3.0))
                
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'command': cmd,
                'output': f"{result.stdout}\n{result.stderr}".strip(),
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'execution_time': time.time()
            }
        except subprocess.TimeoutExpired:
            return {
                'command': cmd,
                'output': f"Command timed out after {timeout} seconds",
                'success': False,
                'return_code': -1,
                'execution_time': time.time()
            }
        except Exception as e:
            return {
                'command': cmd,
                'output': f"Error: {str(e)}",
                'success': False,
                'return_code': -2,
                'execution_time': time.time()
            }

    def parse_nmap_enhanced(self, output):
        """Enhanced nmap output parsing"""
        open_ports = []
        lines = output.split('\n')
        
        for line in lines:
          if '/tcp' in line and ('open' in line or 'filtered' in line):
            parts = line.split()
            if len(parts) >= 3:
              port_proto = parts[0]
              port = int(port_proto.split('/')[0])
              service = parts[2] if len(parts) > 2 else 'unknown'
              open_ports.append((port, service))
              
        return open_ports

    def adaptive_scanning(self, ip, port):
        """Implement adaptive timing and evasion techniques"""
        if not self.args.evasion:
            return []
            
        evasion_commands = []
        
        # Randomized decoy scanning
        evasion_commands.append(f"nmap -D RND:10 -sS -p {port} {ip}")
        
        # Fragment packets
        evasion_commands.append(f"nmap -f -p {port} {ip}")
        
        # Slow timing
        evasion_commands.append(f"nmap -T1 -p {port} {ip}")
        
        return evasion_commands

    def test_api_endpoints(self, ip, port):
        """Test for exposed APIs and microservices"""
        if not self.args.api_test:
            return []
            
        results = []
        protocol = 'https' if port in [443, 8443] else 'http'
        
        for endpoint in API_ENDPOINTS:
            cmd = f"curl -k -s -I {protocol}://{ip}:{port}{endpoint} --max-time 5"
            result = self.run_cmd_enhanced(cmd, timeout=10)
            if result['success'] and '200' in result['output']:
                result['severity'] = 'HIGH'
                result['finding'] = f"Exposed API endpoint: {endpoint}"
            results.append(result)
            
        return results

    def calculate_risk_score(self, port, service_results):
        """Calculate CVSS-like risk scores"""
        config = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS)
        base_score = config.get('risk_base', 5.0)
        
        # Increase score for successful anonymous access
        anon_success = any('anon' in str(result.get('command', '')) and result.get('success', False) 
                          for result in service_results)
        if anon_success:
            base_score += 2.0
            
        # Increase score for successful authentication
        auth_success = any('auth' in str(result.get('command', '')) and result.get('success', False) 
                          for result in service_results)
        if auth_success:
            base_score += 1.5
            
        # Increase score for exposed sensitive endpoints
        sensitive_found = any('admin' in result.get('output', '').lower() or 
                             'config' in result.get('output', '').lower() or
                             'debug' in result.get('output', '').lower()
                             for result in service_results)
        if sensitive_found:
            base_score += 1.0
            
        return min(base_score, 10.0)

    def analyze_attack_paths(self, results):
        """AI-enhanced vulnerability analysis for attack path discovery"""
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
            
        # Check for lateral movement vectors
        if 445 in open_ports and 22 in open_ports:
            attack_paths.append({
                'type': 'LATERAL_MOVEMENT',
                'description': 'SMB + SSH combination enables potential lateral movement',
                'severity': 'CRITICAL',
                'ports': [445, 22]
            })
            
        # Check for privilege escalation vectors
        if 5985 in open_ports or 3389 in open_ports:
            attack_paths.append({
                'type': 'PRIVILEGE_ESCALATION',
                'description': 'Remote administration services detected',
                'severity': 'HIGH',
                'ports': [p for p in [5985, 3389] if p in open_ports]
            })
            
        # Check for data exfiltration opportunities
        db_ports = [p for p in open_ports if p in [3306, 5432, 27017, 6379, 9200]]
        if db_ports:
            attack_paths.append({
                'type': 'DATA_EXFILTRATION',
                'description': f'Database services exposed on ports {db_ports}',
                'severity': 'CRITICAL',
                'ports': db_ports
            })
            
        # Check for container escape opportunities
        if 2375 in open_ports:
            attack_paths.append({
                'type': 'CONTAINER_ESCAPE',
                'description': 'Unprotected Docker daemon detected',
                'severity': 'CRITICAL',
                'ports': [2375]
            })
            
        return attack_paths

    def service_checks_enhanced(self, ip, port, user=None, password=None, replacements=None):
        """Enhanced service-specific testing"""
        config = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS)
        results = []
        
        # Add API testing for web services
        if port in [80, 443, 8080, 8443]:
            api_results = self.test_api_endpoints(ip, port)
            results.extend(api_results)
            
        # Add evasion techniques if enabled
        if self.args.evasion:
            evasion_results = self.adaptive_scanning(ip, port)
            for cmd in evasion_results:
                result = self.run_cmd_enhanced(cmd.format(**replacements))
                results.append(result)
        
        # Run standard checks with enhanced error handling
        for check_type in ['anon', 'auth', 'enum']:
            if check_type in config:
                checks = config[check_type] if isinstance(config[check_type], list) else [config[check_type]]
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for check in checks:
                        if check_type == 'auth' and (not user or not password):
                            continue
                        processed_cmd = check.format(**replacements)
                        future = executor.submit(self.run_cmd_enhanced, processed_cmd)
                        futures.append(future)
                    
                    for future in as_completed(futures):
                        try:
                            result = future.result(timeout=30)
                            results.append(result)
                        except Exception as e:
                            results.append({
                                'command': 'unknown',
                                'output': f'Error: {str(e)}',
                                'success': False
                            })
        
        # Run fallbacks if no successes
        if 'fallback' in config and not any(res.get('success', False) for res in results):
            fallbacks = config['fallback'] if isinstance(config['fallback'], list) else [config['fallback']]
            for fallback in fallbacks:
                processed_cmd = fallback.format(**replacements)
                result = self.run_cmd_enhanced(processed_cmd)
                results.append(result)
        
        return results

    def generate_executive_summary(self, results, ip):
        """Generate executive-friendly summary with metrics"""
        total_ports = len(results)
        critical_issues = sum(1 for port_results in results.values() 
                  for result in port_results 
                  if result.get('severity') == 'CRITICAL' or 
                    self.risk_scores.get(list(results.keys())[list(results.values()).index(port_results)], 0) >= 9.0)
        
        high_issues = sum(1 for port_results in results.values() 
                for result in port_results 
                if result.get('severity') == 'HIGH' or 
                  (7.0 <= self.risk_scores.get(list(results.keys())[list(results.values()).index(port_results)], 0) < 9.0))
        
        # Generate discovered services list
        discovered_services = []
        for port in sorted(results.keys()):
          service_name = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'UNKNOWN')
          risk_score = self.risk_scores.get(port, 0.0)
          discovered_services.append(f"Port {port} ({service_name}) - Risk: {risk_score:.1f}/10.0")
          
        services_list = '\n        '.join(discovered_services)
        
        exec_summary = f"""
          EXECUTIVE SUMMARY - {ip}
          Scan Duration: {datetime.now() - self.start_time}
          
          RISK METRICS:
          • Total Attack Surface: {total_ports} exposed services
          • Critical Vulnerabilities: {critical_issues}
          • High Risk Issues: {high_issues}
          • Attack Paths Identified: {len(self.attack_paths)}
          
          DISCOVERED SERVICES:
          {services_list}
          
          IMMEDIATE THREATS:
          {self.format_attack_paths()}
          
          RECOMMENDED ACTIONS:
          1. Immediate patching required for critical findings
          2. Implement network segmentation
          3. Enable monitoring for suspicious activities
          4. Review access controls and authentication mechanisms
          """
        
        return exec_summary
    def format_attack_paths(self):
        """Format attack paths for display"""
        if not self.attack_paths:
            return "• No immediate attack paths identified"
            
        formatted = []
        for path in self.attack_paths:
            formatted.append(f"• {path['type']}: {path['description']} (Severity: {path['severity']})")
        
        return '\n        '.join(formatted)

    def get_risk_class(self, score):
        """Get CSS risk class based on score"""
        if score >= 9.0:
            return 'risk-critical'
        elif score >= 7.0:
            return 'risk-high'
        elif score >= 5.0:
            return 'risk-medium'
        else:
            return 'risk-low'

    def get_risk_color(self, score):
        """Get risk score color"""
        if score >= 9.0:
            return CyberColors.NEON_PINK
        elif score >= 7.0:
            return CyberColors.NEON_ORANGE
        elif score >= 5.0:
            return CyberColors.NEON_BLUE
        else:
            return CyberColors.NEON_GREEN

    def generate_enhanced_report(self, results, ip):
        """Generate comprehensive cyberpunk-styled HTML report"""
        exec_summary = self.generate_executive_summary(results, ip)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>CYBERSCAN NETWORK ANALYSIS :: {ip}</title>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          {TERMINAL_CSS}
        </head>
        <body>
          <div class="scan-line"></div>
          <div class="terminal-header">
            <h1 class="glitch">// CYBERSCAN NETWORK ANALYSIS</h1>
            <h2>TARGET ACQUIRED: {ip}</h2>
            <h3>{datetime.now().strftime('[%Y-%m-%d %H:%M:%S UTC]')}</h3>
            <div style="margin-top: 1rem;">
              <span class="success">SCAN STATUS: COMPLETE</span> | 
              <span class="warning">DURATION: {datetime.now() - self.start_time}</span> | 
              <span class="fail">THREAT LEVEL: {'CRITICAL' if any(score >= 9.0 for score in self.risk_scores.values()) else 'ELEVATED'}</span>
            </div>
          </div>
          
          <div class="executive-summary">
            <h2 class="glitch">EXECUTIVE THREAT ASSESSMENT</h2>
            
            <div style="margin: 2rem 0;">
              <h3 class="warning">SCAN DURATION: {datetime.now() - self.start_time}</h3>
            </div>
            
            <div style="margin: 2rem 0;">
              <h3 class="success">RISK METRICS:</h3>
              <div style="margin-left: 2rem; color: {CyberColors.NEON_GREEN};">
                <p>► Total Attack Surface: <span class="warning">{len(results)} exposed services</span></p>
                <p>► Critical Vulnerabilities: <span class="{'fail' if sum(1 for score in self.risk_scores.values() if score >= 9.0) > 0 else 'success'}">{sum(1 for score in self.risk_scores.values() if score >= 9.0)}</span></p>
                <p>► High Risk Issues: <span class="{'warning' if sum(1 for score in self.risk_scores.values() if score >= 7.0) > 0 else 'success'}">{sum(1 for score in self.risk_scores.values() if score >= 7.0)}</span></p>
                <p>► Attack Paths Identified: <span class="{'fail' if len(self.attack_paths) > 0 else 'success'}">{len(self.attack_paths)}</span></p>
              </div>
            </div>
            
            <div style="margin: 2rem 0;">
              <h3 class="success">DISCOVERED SERVICES:</h3>
              <div style="margin-left: 2rem;">
        """
        
        # Add discovered services with color coding
        for port in sorted(results.keys()):
          service_name = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'UNKNOWN')
          risk_score = self.risk_scores.get(port, 0.0)
          color_class = 'fail' if risk_score >= 9.0 else 'warning' if risk_score >= 7.0 else 'success'
          
          html += f"""
                <p>► Port <span class="warning">{port}</span> ({service_name}) - Risk: <span class="{color_class}">{risk_score:.1f}/10.0</span></p>
          """
          
        html += f"""
              </div>
            </div>
            
            <div style="margin: 2rem 0;">
              <h3 class="fail">IMMEDIATE THREATS:</h3>
              <div style="margin-left: 2rem; color: {CyberColors.NEON_GREEN};">
        """
        
        # Add attack paths or no threats message
        if self.attack_paths:
          for path in self.attack_paths:
            html += f"""
                <p>► <span class="fail">{path['type']}</span>: {path['description']} (Severity: <span class="fail">{path['severity']}</span>)</p>
            """
        else:
          html += f"""
                <p>► <span class="success">No immediate attack paths identified</span></p>
          """
          
        html += f"""
              </div>
            </div>
            
            <div style="margin: 2rem 0;">
              <h3 class="success">RECOMMENDED ACTIONS:</h3>
              <div style="margin-left: 2rem; color: {CyberColors.NEON_GREEN};">
                <p>1. Immediate patching required for critical findings</p>
                <p>2. Implement network segmentation</p>
                <p>3. Enable monitoring for suspicious activities</p>
                <p>4. Review access controls and authentication mechanisms</p>
              </div>
            </div>
          </div>
        """
        
        # Add attack paths section
        if self.attack_paths:
          html += f"""
          <div class="service">
            <h3 class="glitch">IDENTIFIED ATTACK VECTORS</h3>
            <div class="command-results">
          """
          
          for path in self.attack_paths:
            html += f"""
            <div class="attack-path">
              <h4 class="fail">{path['type']} - {path['severity']}</h4>
              <p>{escape(path['description'])}</p>
              <p><strong>Affected Ports:</strong> {', '.join(map(str, path['ports']))}</p>
            </div>
            """
            
          html += """
            </div>
          </div>
          """
          
        # Add detailed service analysis
        for port, checks in results.items():
          service_name = ENHANCED_SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'UNKNOWN')
          risk_score = self.risk_scores.get(port, 5.0)
          risk_class = self.get_risk_class(risk_score)
          risk_color = self.get_risk_color(risk_score)
          
          html += f"""
          <div class="service {risk_class}">
            <h3 class="glitch">PORT {port} :: {service_name}</h3>
            <div class="risk-score" style="background: {risk_color}; color: #000;">
              RISK SCORE: {risk_score:.1f}/10.0
            </div>
            <div class="command-results">
          """
          
          for check in checks:
            status_class = 'success' if check.get('success', False) else 'fail'
            severity = check.get('severity', '')
            finding = check.get('finding', '')
            
            html += f"""
            <div class="command">
              <span class="{status_class}">► {escape(check.get('command', 'unknown'))}</span>
              {f'<span class="warning">[{severity}] {finding}</span>' if severity else ''}
              <pre>{escape(check.get('output', 'NO OUTPUT')) or 'NO OUTPUT'}</pre>
            </div>
            """
            
          html += """
            </div>
          </div>
          """
          
        # Add JSON export section if requested
        if self.args.export_json:
          json_data = {
            'target': ip,
            'scan_time': datetime.now().isoformat(),
            'duration': str(datetime.now() - self.start_time),
            'results': results,
            'risk_scores': self.risk_scores,
            'attack_paths': self.attack_paths,
            'executive_summary': exec_summary
          }
          
          json_filename = f"cyberscan_{ip}_{datetime.now().strftime('%Y%m%d%H%M')}.json"
          with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
            
          html += f"""
          <div class="service">
            <h3 class="glitch">EXPORT DATA</h3>
            <pre class="success">JSON Export: {json_filename}</pre>
          </div>
          """
          
        html += f"""
          <div class="service">
            <h3 class="glitch">// END OF TRANSMISSION</h3>
            <pre class="{'success' if not any(score >= 9.0 for score in self.risk_scores.values()) else 'fail'}">
      [!] SYSTEM SECURITY STATUS: {'ACCEPTABLE' if not any(score >= 9.0 for score in self.risk_scores.values()) else 'COMPROMISED'}
      [!] CHAINSAW ANALYSIS COMPLETE
      [!] STAY VIGILANT IN THE DIGITAL SHADOWS
            </pre>
          </div>
        </body>
        </html>
        """
        return html

    def send_notifications(self, ip, results):
        """Send notifications to configured integrations"""
        if not hasattr(self.args, 'integrations') or not self.args.integrations:
            return
            
        critical_count = sum(1 for score in self.risk_scores.values() if score >= 9.0)
        total_issues = len([r for port_results in results.values() for r in port_results])
        
        replacements = {
            'ip': ip,
            'critical_count': critical_count,
            'total_issues': total_issues,
            'slack_webhook': getattr(self.args, 'slack_webhook', ''),
            'teams_webhook': getattr(self.args, 'teams_webhook', ''),
            'jira_user': getattr(self.args, 'jira_user', ''),
            'jira_token': getattr(self.args, 'jira_token', ''),
            'jira_url': getattr(self.args, 'jira_url', ''),
            'discord_webhook': getattr(self.args, 'discord_webhook', ''),
            'ifttt_key': getattr(self.args, 'ifttt_key', ''),
            'ifttt_event': getattr(self.args, 'ifttt_event', '')
        }
        
        for integration in self.args.integrations:
            if integration in INTEGRATION_COMMANDS:
                cmd = INTEGRATION_COMMANDS[integration].format(**replacements)
                result = self.run_cmd_enhanced(cmd)
                if result['success']:
                  print(f"[+] {integration} notification sent successfully")
                else:
                  print(f"[!] Failed to send {integration} notification: {result['output']}")

    def run_scan(self):
        """Main scanning logic with enhanced features"""
        self.banner()
        
        # Configure replacements
        replacements = {
            'ip': self.args.ip,
            'user': self.args.user or '',
            'pass': self.args.password or '',
            'dirbuster_wordlist': self.args.wordlist or DEFAULT_WORDLISTS['dirbuster'],
            'ferox_wordlist': self.args.wordlist or DEFAULT_WORDLISTS['feroxbuster'],
            'api_wordlist': DEFAULT_WORDLISTS['api'],
            'snmp_wordlist': self.args.wordlist or DEFAULT_WORDLISTS['snmp'],
            'users': self.args.users or DEFAULT_WORDLISTS['users'],
            'passwords': self.args.passwords or DEFAULT_WORDLISTS['passwords']
        }

        print(f"[*] Initializing network scan on {self.args.ip}...")
        print(f"[*] Evasion mode: {'ENABLED' if self.args.evasion else 'DISABLED'}")
        print(f"[*] API testing: {'ENABLED' if self.args.api_test else 'DISABLED'}")
        
        # Enhanced nmap scanning
        nmap_opts = "-T3 --top-ports 1000"  # Changed from -p-
        if self.args.evasion:
            nmap_opts = "-Pn -T1 --top-ports 1000"  # Changed from -p- -f
        
        nmap_cmd = f"nmap {nmap_opts} {self.args.ip}"
        print(f"[*] Running: {nmap_cmd}")
        nmap_result = self.run_cmd_enhanced(nmap_cmd, timeout=600)
        open_ports = self.parse_nmap_enhanced(nmap_result['output'])
        
        if not open_ports:
            print("[!] No open ports found. Exiting.")
            return
            
        print(f"[+] Discovered {len(open_ports)} open ports: {[p[0] for p in open_ports]}")
        
        # Parallel service scanning
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for port, service in open_ports:
                future = executor.submit(
                    self.service_checks_enhanced, 
                    self.args.ip, port, self.args.user, self.args.password, replacements
                )
                futures[port] = future
            
            for port, future in futures.items():
                try:
                    self.results[port] = future.result(timeout=120)
                    self.risk_scores[port] = self.calculate_risk_score(port, self.results[port])
                    print(f"[+] Completed scan for port {port} (Risk: {self.risk_scores[port]:.1f})")
                except Exception as e:
                    print(f"[!] Error scanning port {port}: {str(e)}")
                    self.results[port] = []
                    self.risk_scores[port] = 0.0
        
        # Analyze attack paths
        self.attack_paths = self.analyze_attack_paths(self.results)
        print(f"[+] Identified {len(self.attack_paths)} potential attack paths")
        
        # Generate report
        report = self.generate_enhanced_report(self.results, self.args.ip)
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        filename = f"cyscan_{self.args.ip}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"[+] Network analysis complete: {filename}")
        
        # Send notifications
        self.send_notifications(self.args.ip, self.results)
        
        # Open report in browser
        if not self.args.no_browser:
            webbrowser.open(f"file://{os.path.abspath(filename)}")
        
        # Setup continuous monitoring if requested
        if self.args.continuous:
            self.setup_continuous_monitoring()

    def setup_continuous_monitoring(self):
        """Setup continuous monitoring for target"""
        monitor_script = f"""#!/bin/bash
# Cyberscan Continuous Monitor for {self.args.ip}
while true; do
    echo "[$(date)] Running continuous scan..."
    python3 {os.path.abspath(__file__)} {self.args.ip} --no-browser
    sleep 3600  # Run every hour
done
"""
        monitor_filename = f"cyberscan_monitor_{self.args.ip}.sh"
        with open(monitor_filename, 'w') as f:
            f.write(monitor_script)
        os.chmod(monitor_filename, 0o755)
        print(f"[+] Continuous monitoring script created: {monitor_filename}")

def main():
    parser = argparse.ArgumentParser(
        description='CyberScan Network Penetration Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cyberscan.py 192.168.1.1
  python3 cyberscan.py target.com --evasion --api-test
  python3 cyberscan.py server.com -u admin -p pass --continuous --export-json
  python3 cyberscan.py site.com --integrations discord_notify --discord-webhook "URL"
  python3 cyberscan.py 10.0.0.1 --integrations slack_notify ifttt_trigger --slack-webhook "URL" --ifttt-key "KEY" --ifttt-event "alert"
  python3 cyberscan.py target.com --evasion --api-test --risk-score --export-json --no-browser
        """
    )
  
    # Basic arguments
    parser.add_argument('ip', help='Target IP address or hostname')
    parser.add_argument('-u', '--user', help='Username for authentication')
    parser.add_argument('-p', '--password', help='Password for authentication')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist path')
    parser.add_argument('--users', help='Custom user list for brute-force')
    parser.add_argument('--passwords', help='Custom password list for brute-force')
  
    # Enhanced features
    parser.add_argument('--evasion', action='store_true', 
                       help='Enable evasion techniques (slower but stealthier)')
    parser.add_argument('--api-test', action='store_true',
                       help='Enable comprehensive API endpoint testing')
    parser.add_argument('--continuous', action='store_true',
                       help='Setup continuous monitoring')
    parser.add_argument('--export-json', action='store_true',
                       help='Export results to JSON format')
    parser.add_argument('--risk-score', action='store_true',
                       help='Calculate and display risk scores')
    parser.add_argument('--no-browser', action='store_true',
                       help='Do not open report in browser')
  
    # Integration options
    parser.add_argument('--integrations', nargs='+', 
                        choices=['slack_notify', 'jira_ticket', 'teams_notify', 'discord_notify', 'ifttt_trigger'],
                        metavar='INTEGRATION',
                        help='Enable integrations for notifications (choices: slack_notify, discord_notify, teams_notify, ifttt_trigger, jira_ticket)')
    parser.add_argument('--slack-webhook', help='Slack webhook URL')
    parser.add_argument('--teams-webhook', help='Microsoft Teams webhook URL')
    parser.add_argument('--jira-url', help='Jira base URL')
    parser.add_argument('--jira-user', help='Jira username')
    parser.add_argument('--jira-token', help='Jira API token')
    parser.add_argument('--discord-webhook', help='Discord webhook URL')
    parser.add_argument('--ifttt-key', help='IFTTT Webhook service key')
    parser.add_argument('--ifttt-event', help='IFTTT event name to trigger')
  
    args = parser.parse_args()
  
    # Create and run scanner
    scanner = CyberScanner(args)
    scanner.run_scan()

if __name__ == '__main__':
    main()
