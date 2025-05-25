#!/usr/bin/env python3
import argparse
import subprocess
import os
import webbrowser
import re
from html import escape
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# =====================
#  STYLING
# =====================
class CyberColors:
    NEON_GREEN = '#39FF14'
    NEON_PINK = '#FF10F0'
    NEON_BLUE = '#00F3FF'
    MATRIX_GREEN = '#20C20E'
    DARK_BG = '#0A0A0A'

TERMINAL_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu+Mono&family=Press+Start+2P&display=swap');
    
    body {{
        background-color: {CyberColors.DARK_BG};
        color: {CyberColors.NEON_GREEN};
        font-family: 'Ubuntu Mono', monospace;
        margin: 2rem;
    }}
    
    .glitch {{
        font-family: 'Press Start 2P', cursive;
        color: {CyberColors.NEON_BLUE};
        text-shadow: 3px 3px {CyberColors.NEON_PINK};
        animation: glitch 2s infinite;
    }}
    
    @keyframes glitch {{
        2% {{ text-shadow: 2px 2px {CyberColors.NEON_PINK}; }}
        4% {{ text-shadow: -2px -2px {CyberColors.NEON_PINK}; }}
        5% {{ text-shadow: 3px 3px {CyberColors.NEON_PINK}; }}
    }}
    
    .service {{
        background: rgba(10, 10, 10, 0.9);
        border: 1px solid {CyberColors.NEON_BLUE};
        border-radius: 5px;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 0 15px {CyberColors.NEON_BLUE};
        transition: transform 0.3s;
    }}
    
    .service:hover {{
        transform: translateX(10px);
        box-shadow: 0 0 25px {CyberColors.NEON_PINK};
    }}
    
    pre {{
        background: #001100;
        color: {CyberColors.MATRIX_GREEN};
        padding: 1rem;
        border-left: 3px solid {CyberColors.NEON_GREEN};
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    
    .success {{
        color: {CyberColors.NEON_GREEN} !important;
        text-shadow: 0 0 10px {CyberColors.NEON_GREEN};
    }}
    
    .fail {{
        color: {CyberColors.NEON_PINK} !important;
        text-shadow: 0 0 10px {CyberColors.NEON_PINK};
    }}
    
    .scan-line {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            to bottom,
            rgba(255, 255, 255, 0) 0%,
            rgba(255, 255, 255, 0.1) 10%,
            rgba(255, 255, 255, 0) 100%
        );
        animation: scan 4s linear infinite;
        pointer-events: none;
    }}
    
    @keyframes scan {{
        0% {{ transform: translateY(-100%); }}
        100% {{ transform: translateY(100%); }}
    }}
    
    .terminal-header {{
        border: 3px solid {CyberColors.NEON_BLUE};
        padding: 1rem;
        margin-bottom: 2rem;
        position: relative;
    }}
    
    .terminal-header::before {{
        content: "▲▼▲▼ TERMINAL OUTPUT ▲▼▲▼";
        position: absolute;
        top: -15px;
        left: 20px;
        background: {CyberColors.DARK_BG};
        padding: 0 10px;
        font-size: 0.8em;
    }}
</style>
"""

# =====================
# PENTEST CONFIGURATION
# =====================
DEFAULT_WORDLISTS = {
    'dirbuster': '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
    'feroxbuster': '/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt',
    'snmp': '/usr/share/wordlists/dict.txt',
    'users': 'users.txt',
    'passwords': 'passwords.txt'
}

SERVICE_CHECKS = {
    # FTP
    21: {
        'name': 'FTP',
        'anon': [
            'curl -v ftp://{ip}',
            'ftp -inv {ip} <<< "user anonymous"'
        ],
        'auth': 'ftp -inv {ip} -u {user} -p {pass}',
        'enum': [
            'nmap --script=ftp-* -p 21 {ip}',
            'wget -m ftp://{user}:{pass}@{ip}'
        ],
        'fallback': [
            'nc -vn {ip} 21 <<< "USER anonymous"'
        ]
    },
    
    # SSH
    22: {
        'name': 'SSH',
        'auth': 'ssh {user}@{ip} -o PasswordAuthentication=yes',
        'enum': [
            'ssh -v {user}@{ip}',
            'nmap --script=ssh-* -p 22 {ip}'
        ],
        'fallback': [
            'hydra -L {users} -P {passwords} ssh://{ip}'
        ]
    },
    
    # HTTP
    80: {
        'name': 'HTTP',
        'enum': [
            'gobuster dir -u http://{ip} -w {dirbuster_wordlist}',
            'nikto -h http://{ip}',
            'whatweb -a3 http://{ip}'
        ],
        'fallback': [
            'feroxbuster -u http://{ip} -w {ferox_wordlist}'
        ]
    },
    
    # HTTPS
    443: {
        'name': 'HTTPS',
        'enum': [
            'testssl.sh {ip}',
            'gobuster dir -u https://{ip} -w {dirbuster_wordlist}'
        ],
        'fallback': [
            'sslscan {ip}'
        ]
    },
    
    # SMB
    445: {
        'name': 'SMB',
        'anon': [
            'smbclient -L //{ip}/ -N',
            'crackmapexec smb {ip} --shares -u "" -p ""'
        ],
        'auth': 'crackmapexec smb {ip} -u {user} -p {pass} --shares',
        'enum': [
            'enum4linux -a {ip}',
            'nmap --script=smb-* -p 445 {ip}'
        ],
        'fallback': [
            'rpcclient -U "{user}%{pass}" {ip}',
            'python3 -m impacket.examples.smbexec {user}:{pass}@{ip}'
        ]
    },
    
    # WinRM
    5985: {
        'name': 'WinRM',
        'auth': [
            'evil-winrm -i {ip} -u {user} -p {pass}',
            'crackmapexec winrm {ip} -u {user} -p {pass} -x "whoami"'
        ],
        'fallback': [
            'python3 -m impacket.examples.wmiexec {user}:{pass}@{ip}',
            'crackmapexec winrm {ip} -u {user} -p {pass} --ntlm'
        ]
    },
    
    # MySQL
    3306: {
        'name': 'MySQL',
        'auth': 'mysql -h {ip} -u {user} -p{pass} -e "SHOW DATABASES;"',
        'enum': [
            'nmap --script=mysql-* -p 3306 {ip}',
            'crackmapexec mysql {ip} -u {user} -p {pass}'
        ],
        'fallback': [
            'mysqldump -h {ip} -u {user} -p{pass} --all-databases'
        ]
    },
    
    # RDP
    3389: {
        'name': 'RDP',
        'enum': [
            'nmap --script=rdp-* -p 3389 {ip}',
            'crackmapexec rdp {ip} -u {user} -p {pass}'
        ],
        'fallback': [
            'xfreerdp /v:{ip} /u:{user} /p:{pass} +auth-only'
        ]
    },
    
    # PostgreSQL
    5432: {
        'name': 'PostgreSQL',
        'auth': 'psql -h {ip} -U {user} -c "\l"',
        'enum': [
            'nmap --script=pgsql-* -p 5432 {ip}',
            'crackmapexec postgres {ip} -u {user} -p {pass}'
        ],
        'fallback': [
            'pg_dump -h {ip} -U {user} --all'
        ]
    },
    
    # SNMP
    161: {
        'name': 'SNMP',
        'anon': [
            'snmpwalk -v1 -c public {ip}',
            'onesixtyone -c {snmp_wordlist} {ip}'
        ],
        'fallback': [
            'snmp-check {ip} -c public'
        ]
    },
    
    # LDAP
    389: {
        'name': 'LDAP',
        'anon': [
            'ldapsearch -x -H ldap://{ip} -s base',
            'crackmapexec ldap {ip}'
        ],
        'fallback': [
            'nmap --script=ldap-* -p 389 {ip}'
        ]
    }
}

GENERIC_CHECKS = {
    'name': 'Generic',
    'enum': [
        'nc -v -n {ip} {port}',
        'curl -I http://{ip}:{port}',
        'nmap -sV -p {port} --script="banner,(safe or default) and not broadcast" {ip}'
    ],
    'fallback': [
        'openssl s_client -connect {ip}:{port} -quiet',
        'socat - TCP:{ip}:{port}'
    ]
}

def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'command': cmd,
            'output': f"{result.stdout}\n{result.stderr}".strip(),
            'success': result.returncode == 0
        }
    except Exception as e:
        return {
            'command': cmd,
            'output': f"Error: {str(e)}",
            'success': False
        }

def parse_nmap(output):
    return [
        (int(line.split('/')[0]), line.split()[2])
        for line in output.split('\n') 
        if '/tcp' in line and 'open' in line
    ]

def service_checks(ip, port, user=None, password=None, replacements=None):
    config = SERVICE_CHECKS.get(port, GENERIC_CHECKS)
    results = []
    
    # Run standard checks
    for check_type in ['anon', 'auth', 'enum']:
        if check_type in config:
            checks = config[check_type] if isinstance(config[check_type], list) else [config[check_type]]
            with ThreadPoolExecutor() as executor:
                processed = [c.format(**replacements) for c in checks]
                results.extend(list(executor.map(run_cmd, processed)))
    
    # Run fallbacks if no successes
    if 'fallback' in config and not any(res['success'] for res in results):
        fallbacks = config['fallback'] if isinstance(config['fallback'], list) else [config['fallback']]
        with ThreadPoolExecutor() as executor:
            processed = [f.format(**replacements) for f in fallbacks]
            results.extend(list(executor.map(run_cmd, processed)))
    
    return results

def generate_cyber_report(results, ip):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CYBERSCAN :: {ip}</title>
        {TERMINAL_CSS}
    </head>
    <body>
        <div class="scan-line"></div>
        <div class="terminal-header">
            <h1 class="glitch">// SCAN REPORT</h1>
            <h2>TARGET: {ip}</h2>
            <h3>{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')}</h3>
        </div>
    """
    
    for port, checks in results.items():
        service_name = SERVICE_CHECKS.get(port, GENERIC_CHECKS).get('name', 'UNKNOWN')
        html += f"""
        <div class="service">
            <h3 class="glitch">PORT {port} :: {service_name}</h3>
            <div class="command-results">
        """
        
        for check in checks:
            status_class = 'success' if check['success'] else 'fail'
            html += f"""
            <div class="command">
                <span class="{status_class}">➜ {escape(check['command'])}</span>
                <pre>{escape(check['output']) or 'NO OUTPUT'}</pre>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
    
    html += """
        <div class="service">
            <h3 class="glitch">// END OF TRANSMISSION</h3>
            <pre class="success">[!] SYSTEM SECURITY STATUS: COMPROMISED</pre>
        </div>
    </body>
    </html>
    """
    return html

def main():
    parser = argparse.ArgumentParser(description='CyberScan Pentest Tool')
    parser.add_argument('ip', help='Target IP address')
    parser.add_argument('-u', '--user', help='Username for authentication')
    parser.add_argument('-p', '--password', help='Password for authentication')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist path')
    parser.add_argument('--users', help='Custom user list for brute-force')
    parser.add_argument('--passwords', help='Custom password list for brute-force')
    args = parser.parse_args()

    # Configure replacements
    replacements = {
        'ip': args.ip,
        'user': args.user or '',
        'pass': args.password or '',
        'dirbuster_wordlist': args.wordlist or DEFAULT_WORDLISTS['dirbuster'],
        'ferox_wordlist': args.wordlist or DEFAULT_WORDLISTS['feroxbuster'],
        'snmp_wordlist': args.wordlist or DEFAULT_WORDLISTS['snmp'],
        'users': args.users or DEFAULT_WORDLISTS['users'],
        'passwords': args.passwords or DEFAULT_WORDLISTS['passwords']
    }

    print(f"[*] Initializing cyber scan on {args.ip}...")
    nmap_cmd = f"nmap -p- -T4 -sV -O {args.ip}"
    nmap_result = run_cmd(nmap_cmd)
    open_ports = parse_nmap(nmap_result['output'])
    
    report_data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {port: executor.submit(service_checks, args.ip, port, args.user, args.password, replacements) 
                 for port, _ in open_ports}
        
        for port, future in futures.items():
            report_data[port] = future.result()
    
    report = generate_cyber_report(report_data, args.ip)
    filename = f"cyberscan_{args.ip}_{datetime.now().strftime('%Y%m%d%H%M')}.html"
    
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"[+] Report generated: {filename}")
    webbrowser.open(f"file://{os.path.abspath(filename)}")

if __name__ == '__main__':
    main()
