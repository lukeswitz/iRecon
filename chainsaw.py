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


def check_and_install_tools():
    """Check for required tools and install if missing"""
    
    # Tool aliases - check multiple possible command names
    tool_aliases = {
      'crackmapexec': ['crackmapexec', 'nxc', 'NetExec', 'netexec'],
      'testssl': ['testssl', 'testssl.sh'],
      'smbclient': ['smbclient', '/usr/bin/smbutil'],  # macOS alternative
      'redis-cli': ['redis-cli', 'redis-client'],
      'mysql': ['mysql', 'mysql-client'],
      'psql': ['psql', 'postgresql-client']
    }
    
    # Required tools mapping: command -> package_name
    required_tools = {
      'nmap': 'nmap',
      'gobuster': 'gobuster', 
      'nikto': 'nikto',
      'feroxbuster': 'feroxbuster',
      'smbclient': 'smbclient',
      'enum4linux': 'enum4linux',
      'crackmapexec': 'crackmapexec',  # Will be installed as nxc
      'evil-winrm': 'evil-winrm',
      'testssl': 'testssl',
      'redis-cli': 'redis-tools',
      'mysql': 'mysql-client',
      'psql': 'postgresql-client',
      'hydra': 'hydra'
    }
    
    # Detect OS
    system = platform.system().lower()
    distro = None
    
    if system == 'linux':
      try:
        with open('/etc/os-release', 'r') as f:
          content = f.read().lower()
          if 'ubuntu' in content or 'debian' in content:
            distro = 'debian'
          elif 'centos' in content or 'rhel' in content or 'fedora' in content:
            distro = 'redhat'
          elif 'arch' in content:
            distro = 'arch'
      except:
        distro = 'unknown'
        
    print(f"[*] Detected OS: {system} ({distro if distro else 'unknown'})")
    
    # Check for missing tools with alias support
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
        
    # Show what was found
    if found_tools:
      print(f"[+] Found tools: {found_tools}")
      
    if not missing_tools:
      print("[+] All required tools are installed!")
      return True
    
    print(f"[!] Missing tools: {[tool for tool, _ in missing_tools]}")
    
    # Ask user permission
    response = input("[?] Install missing tools? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
      print("[!] Continuing without installing tools (some scans may fail)")
      return False
    
    # Install based on OS
    if system == 'linux' and distro == 'debian':
      install_debian_tools(missing_tools)
    elif system == 'linux' and distro == 'redhat':
      install_redhat_tools(missing_tools)
    elif system == 'linux' and distro == 'arch':
      install_arch_tools(missing_tools)
    elif system == 'darwin':  # macOS
      install_macos_tools(missing_tools)
    else:
      print(f"[!] Automatic installation not supported for {system} ({distro})")
      print("[!] Please install tools manually:")
      for tool, package in missing_tools:
        print(f"    - {tool} ({package})")
      return False
    
    return True

def install_debian_tools(missing_tools):
  """Install tools on Debian/Ubuntu systems"""
  packages = []
  
  # Special cases for Debian/Ubuntu
  package_map = {
    'crackmapexec': 'python3-crackmapexec',
    'evil-winrm': 'evil-winrm',
    'feroxbuster': None,  # Not in default repos
    'testssl.sh': 'testssl.sh'
  }
  
  for tool, default_package in missing_tools:
    package = package_map.get(tool, default_package)
    if package:
      packages.append(package)
    elif tool == 'feroxbuster':
      print("[!] feroxbuster not in default repos - install manually from GitHub")
      
  if packages:
    cmd = f"sudo apt update && sudo apt install -y {' '.join(packages)}"
#   print(f"[*] Running: {cmd}")
    os.system(cmd)
    
def install_redhat_tools(missing_tools):
  """Install tools on RedHat/CentOS/Fedora systems"""
  packages = []
  
  # Check if dnf or yum
  pkg_manager = 'dnf' if shutil.which('dnf') else 'yum'
  
  for tool, package in missing_tools:
    if tool == 'crackmapexec':
      print("[!] crackmapexec - install via pip: pip3 install crackmapexec")
    elif tool == 'feroxbuster':
      print("[!] feroxbuster - install from GitHub releases")
    else:
      packages.append(package)
      
  if packages:
    cmd = f"sudo {pkg_manager} install -y {' '.join(packages)}"
    print(f"[*] Running: {cmd}")
    os.system(cmd)
    
def install_arch_tools(missing_tools):
  """Install tools on Arch Linux"""
  packages = []
  aur_packages = []
  
  for tool, package in missing_tools:
    if tool in ['crackmapexec', 'evil-winrm', 'feroxbuster']:
      aur_packages.append(package)
    else:
      packages.append(package)
      
  if packages:
    cmd = f"sudo pacman -S --noconfirm {' '.join(packages)}"
    print(f"[*] Running: {cmd}")
    os.system(cmd)
    
  if aur_packages:
    print(f"[!] AUR packages need manual install: {aur_packages}")
    
def install_macos_tools(missing_tools):
    """Advanced macOS tool installer using multiple package managers"""
    if not shutil.which('brew'):
      print("[!] Homebrew not found. Install from https://brew.sh/")
      return
    
    # Installation method mappings for macOS
    brew_packages = []
    cargo_packages = []
    pipx_packages = {}
    go_packages = {}
    gem_packages = []
    docker_commands = []
    manual_installs = []
    
    # Tool installation mappings
    tool_methods = {
      # Homebrew (easiest and most reliable)
      'nmap': {'method': 'brew', 'package': 'nmap'},
      'gobuster': {'method': 'brew', 'package': 'gobuster'},
      'nikto': {'method': 'brew', 'package': 'nikto'},
      'testssl': {'method': 'brew', 'package': 'testssl'},
      'redis-cli': {'method': 'brew', 'package': 'redis'},
      'mysql': {'method': 'brew', 'package': 'mysql-client'},
      'psql': {'method': 'brew', 'package': 'postgresql@14'},
      'hydra': {'method': 'brew', 'package': 'hydra'},
      'smbclient': {'method': 'brew', 'package': 'samba'},
      
      # Cargo (Rust) packages
      'feroxbuster': {'method': 'cargo', 'package': 'feroxbuster'},
      
      # pipx (Python) packages - isolated environments
      'crackmapexec': {'method': 'pipx', 'package': 'git+https://github.com/Pennyw0rth/NetExec'},
      'impacket-scripts': {'method': 'pipx', 'package': 'impacket'},
      
      # Go packages
      'subfinder': {'method': 'go', 'package': 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'},
      
      # Gem (Ruby) packages
      'evil-winrm': {'method': 'gem', 'package': 'evil-winrm'},
      
      # Docker alternatives for Linux-specific tools
      'enum4linux': {'method': 'docker', 'command': 'docker pull cddmp/enum4linux-ng'},
      'crackmapexec-alt': {'method': 'docker', 'command': 'docker pull byt3bl33d3r/crackmapexec'},
      
      # Manual installations from GitHub releases
      'nuclei': {'method': 'manual', 'url': 'https://github.com/projectdiscovery/nuclei/releases'},
    }
    
    # Categorize tools by installation method
    for tool, default_package in missing_tools:
      if tool in tool_methods:
        method_info = tool_methods[tool]
        method = method_info['method']
        
        if method == 'brew':
          brew_packages.append(method_info['package'])
        elif method == 'cargo':
          cargo_packages.append(method_info['package'])
        elif method == 'pipx':
          pipx_packages[tool] = method_info['package']
        elif method == 'go':
          go_packages[tool] = method_info['package']
        elif method == 'gem':
          gem_packages.append(method_info['package'])
        elif method == 'docker':
          docker_commands.append(method_info['command'])
        elif method == 'manual':
          manual_installs.append((tool, method_info.get('url', 'GitHub')))
      else:
        manual_installs.append((tool, 'Unknown installation method'))
        
    # Install via Homebrew
    if brew_packages:
      cmd = f"brew install {' '.join(sorted(set(brew_packages)))}"
      print(f"[*] Installing via Homebrew: {cmd}")
      os.system(cmd)
      
    # Install via Cargo (Rust)
    if cargo_packages:
      if not shutil.which('cargo'):
        print("[*] Installing Rust toolchain...")
        os.system("brew install rust")
        
      for package in cargo_packages:
        print(f"[*] Installing via Cargo: {package}")
        os.system(f"cargo install {package}")
        
    # Install via pipx (Python)
    if pipx_packages:
      if not shutil.which('pipx'):
        print("[*] Installing pipx...")
        os.system("brew install pipx")
        os.system("pipx ensurepath")
        
      for tool, package in pipx_packages.items():
        print(f"[*] Installing {tool} via pipx...")
        os.system(f"pipx install {package}")
        
    # Install via Go
    if go_packages:
      if not shutil.which('go'):
        print("[*] Installing Go...")
        os.system("brew install go")
        
      for tool, package in go_packages.items():
        print(f"[*] Installing {tool} via Go...")
        os.system(f"go install {package}")
        
    # Install via Gem (Ruby)
    if gem_packages:
      for package in gem_packages:
        print(f"[*] Installing via Gem: {package}")
        os.system(f"gem install {package}")
        
    # Setup Docker alternatives
    if docker_commands:
      if not shutil.which('docker'):
        print("[!] Docker not found. Install Docker Desktop for macOS")
        print("    Download from: https://docs.docker.com/desktop/mac/install/")
      else:
        for cmd in docker_commands:
          print(f"[*] Setting up Docker image: {cmd}")
          os.system(cmd)
          
      # Create wrapper scripts for Docker tools
      create_docker_wrappers()
      
    # Manual installations
    if manual_installs:
      print("\n[!] Manual installation required for:")
      for tool, source in manual_installs:
        print(f"    • {tool}: {source}")
        
    print("\n[+] macOS tool installation complete!")
    
def install_seclists_macos():
    """Install SecLists wordlists to user directory on macOS (no sudo needed)"""
    user_wordlists = os.path.expanduser("~/.chainsaw/wordlists")
    seclists_path = os.path.join(user_wordlists, "seclists")
    
    # Check if already installed
    if os.path.exists(seclists_path):
      print(f"[+] SecLists already installed at {seclists_path}")
      return True
    
    print("[*] Installing SecLists wordlists to user directory...")
    
    try:
      # Create wordlists directory
      os.makedirs(user_wordlists, exist_ok=True)
      
      # Clone SecLists to user directory (no sudo needed)
      clone_cmd = f"git clone --depth 1 https://github.com/danielmiessler/SecLists.git {seclists_path}"
      print(f"[*] Running: {clone_cmd}")
      result = os.system(clone_cmd)
      
      if result == 0:
        print(f"[+] SecLists installed successfully to {seclists_path}")
        return True
      else:
        print("[!] Failed to clone SecLists")
        return False
      
    except Exception as e:
      print(f"[!] Error installing SecLists: {str(e)}")
      return False
  
def download_specific_wordlists():
    """Download only the wordlists we actually use"""
    wordlist_dir = os.path.expanduser("~/.chainsaw/wordlists")
    os.makedirs(wordlist_dir, exist_ok=True)
    
    # Direct URLs to specific wordlists we use
    wordlist_urls = {
      'directory-list-2.3-medium.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt',
      'raft-large-directories.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-directories.txt',
      'api-endpoints.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/api/api-endpoints.txt',
      'subdomains-top1million-5000.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt',
      'common-snmp-community-strings.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/SNMP/common-snmp-community-strings.txt',
      'top-usernames-shortlist.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt',
      'top-100-passwords.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100.txt'
    }
    
    print("[*] Downloading essential wordlists...")
    downloaded = 0
    
    for filename, url in wordlist_urls.items():
      filepath = os.path.join(wordlist_dir, filename)
      
      # Skip if already exists
      if os.path.exists(filepath):
        print(f"[+] {filename} already exists")
        downloaded += 1
        continue
      
      try:
        print(f"[*] Downloading {filename}...")
        import urllib.request
        urllib.request.urlretrieve(url, filepath)
        
        # Verify download worked
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
          print(f"[+] Downloaded {filename} ({os.path.getsize(filepath)} bytes)")
          downloaded += 1
        else:
          print(f"[!] Failed to download {filename}")
          
      except Exception as e:
        print(f"[!] Error downloading {filename}: {str(e)}")
        
    if downloaded >= 4:  # At least got the key ones
      print(f"[+] Successfully downloaded {downloaded}/{len(wordlist_urls)} wordlists")
      return True
    else:
      print(f"[!] Only downloaded {downloaded}/{len(wordlist_urls)} wordlists")
      return False
    
def setup_macos_wordlists():
    """Setup wordlist paths for macOS with targeted downloads"""
    global DEFAULT_WORDLISTS
    
    wordlist_dir = os.path.expanduser("~/.chainsaw/wordlists")
    
    # Try to download specific wordlists
    download_success = download_specific_wordlists()
    
    if download_success:
      # Update paths to use downloaded wordlists
      DEFAULT_WORDLISTS.update({
        'dirbuster': os.path.join(wordlist_dir, 'directory-list-2.3-medium.txt'),
        'feroxbuster': os.path.join(wordlist_dir, 'raft-large-directories.txt'),
        'api': os.path.join(wordlist_dir, 'api-endpoints.txt'),
        'subdomains': os.path.join(wordlist_dir, 'subdomains-top1million-5000.txt'),
        'snmp': os.path.join(wordlist_dir, 'common-snmp-community-strings.txt'),
        'users': os.path.join(wordlist_dir, 'top-usernames-shortlist.txt'),
        'passwords': os.path.join(wordlist_dir, 'top-100-passwords.txt')
      })
      print("[+] Updated wordlist paths to use downloaded SecLists")
    else:
      # Fallback to basic wordlists
      print("[!] Download failed, creating basic wordlists...")
      create_basic_wordlists()
      
    return check_wordlists()
    
    
def create_basic_wordlists():
    """Create basic wordlists if SecLists not available"""
    wordlist_dir = os.path.expanduser("~/.chainsaw/wordlists")
    os.makedirs(wordlist_dir, exist_ok=True)
    
    # Create basic directory list
    basic_dirs = [
      'admin', 'api', 'app', 'backup', 'bin', 'cgi-bin', 'config', 'data',
      'db', 'debug', 'dev', 'docs', 'download', 'files', 'images', 'inc',
      'include', 'js', 'lib', 'log', 'logs', 'old', 'private', 'public',
      'scripts', 'src', 'static', 'temp', 'test', 'tmp', 'upload', 'uploads',
      'var', 'web', 'www', '.git', '.env', 'robots.txt', 'sitemap.xml'
    ]
    
    # Create basic subdomain list
    basic_subdomains = [
      'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
      'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'ns3', 'm', 'test',
      'admin', 'dev', 'staging', 'api', 'blog', 'shop', 'support', 'secure'
    ]
    
    # Write wordlists
    files_to_create = {
      'basic-directories.txt': basic_dirs,
      'basic-api.txt': ['/api/v1/', '/api/v2/', '/api/', '/graphql', '/swagger/', '/health', '/status', '/metrics'],
      'basic-subdomains.txt': basic_subdomains,
      'basic-users.txt': ['admin', 'administrator', 'root', 'user', 'test'],
      'basic-passwords.txt': ['password', '123456', 'admin', 'root', 'password123']
    }
    
    for filename, content in files_to_create.items():
      filepath = os.path.join(wordlist_dir, filename)
      with open(filepath, 'w') as f:
        f.write('\n'.join(content))
        
    # Update DEFAULT_WORDLISTS to use basic lists
    DEFAULT_WORDLISTS.update({
      'dirbuster': os.path.join(wordlist_dir, 'basic-directories.txt'),
      'feroxbuster': os.path.join(wordlist_dir, 'basic-directories.txt'),
      'api': os.path.join(wordlist_dir, 'basic-api.txt'),
      'subdomains': os.path.join(wordlist_dir, 'basic-subdomains.txt'),
      'snmp': os.path.join(wordlist_dir, 'basic-directories.txt'),
      'users': os.path.join(wordlist_dir, 'basic-users.txt'),
      'passwords': os.path.join(wordlist_dir, 'basic-passwords.txt')
    })
    
    print(f"[+] Created basic wordlists in {wordlist_dir}")
  
def check_wordlists():
    """Verify wordlists exist and show sizes"""
    print("[*] Verifying wordlists...")
    
    for name, path in DEFAULT_WORDLISTS.items():
      if os.path.exists(path):
        size = os.path.getsize(path)
        lines = sum(1 for _ in open(path)) if size < 50000000 else "Large file"  # Don't count huge files
        print(f"[+] {name}: {os.path.basename(path)} ({size} bytes, {lines} entries)")
      else:
        print(f"[!] Missing: {name} -> {path}")
        
    return True
    
def create_docker_wrappers():
    """Create wrapper scripts for Docker-based tools"""
    wrappers = {
      'enum4linux': '''#!/bin/bash
  docker run --rm -it cddmp/enum4linux-ng "$@"
  ''',
      'crackmapexec-docker': '''#!/bin/bash
  docker run --rm -it byt3bl33d3r/crackmapexec "$@"
  '''
    }
    
    wrapper_dir = os.path.expanduser("~/.local/bin")
    os.makedirs(wrapper_dir, exist_ok=True)
    
    for tool, script in wrappers.items():
      wrapper_path = os.path.join(wrapper_dir, tool)
      with open(wrapper_path, 'w') as f:
        f.write(script)
      os.chmod(wrapper_path, 0o755)
      print(f"[+] Created Docker wrapper: {wrapper_path}")
      
    # Add to PATH if not already there
    shell_rc = os.path.expanduser("~/.zshrc")
    path_export = 'export PATH="$HOME/.local/bin:$PATH"'
    
    try:
      with open(shell_rc, 'r') as f:
        content = f.read()
        
      if path_export not in content:
        with open(shell_rc, 'a') as f:
          f.write(f"\n# Added by chainsaw installer\n{path_export}\n")
        print(f"[+] Added ~/.local/bin to PATH in {shell_rc}")
    except:
      print(f"[!] Manually add to PATH: {path_export}")
      
def check_package_managers():
    """Check and install required package managers"""
    managers = {}
    
    # Check Homebrew
    managers['brew'] = shutil.which('brew') is not None
    
    # Check others
    managers['cargo'] = shutil.which('cargo') is not None
    managers['pipx'] = shutil.which('pipx') is not None
    managers['go'] = shutil.which('go') is not None
    managers['gem'] = shutil.which('gem') is not None
    managers['docker'] = shutil.which('docker') is not None
    
    print(f"[*] Package managers available: {[k for k, v in managers.items() if v]}")
    return managers

class GracefulShutdown:
  def __init__(self):
    self.shutdown = False
    self.cleanup_files = []
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)
    atexit.register(self.cleanup)
    
  def exit_gracefully(self, signum, frame):
    print(f"\n{chr(27)}[0m[!] Shutdown signal received...")
    print("[!] Cleaning up...")
    self.shutdown = True
    self.cleanup()
    sys.exit(0)
    
  def cleanup(self):
    # Reset terminal colors
    print(f"{chr(27)}[0m", end="", flush=True)
    
    # Clean up partial files
    for filepath in self.cleanup_files:
      try:
        if os.path.exists(filepath) and os.path.getsize(filepath) < 1000:  # Partial file
          os.remove(filepath)
          print(f"[+] Cleaned up partial file: {filepath}")
      except:
        pass
        
  def add_cleanup_file(self, filepath):
    self.cleanup_files.append(filepath)

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
        content: "▲▼▲▼ CHAINSAW NETWORK ANALYSIS ▲▼▲▼";
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
      'risk_base': 7.0,
      'enumeration': [
        'nxc ftp {ip} -u "" -p ""',
        'nmap --script ftp-anon,ftp-bounce,ftp-proftpd-backdoor,ftp-vsftpd-backdoor -p 21 {ip}',
        'curl -v ftp://{ip} --max-time 20',
        'lftp -u anonymous, {ip} -e "ls; quit"'
      ],
      'authentication': [
        'nxc ftp {ip} -u {user} -p {pass}',
        'hydra -l {user} -p {pass} ftp://{ip}',
        'lftp -u {user},{pass} {ip} -e "ls; pwd; quit"'
      ],
      'escalation': [
        'nxc ftp {ip} -u {user} -p {pass} --put-file /etc/passwd /tmp/passwd',
        'lftp -u {user},{pass} {ip} -e "put /tmp/test.txt test.txt; ls; quit"',
        'curl -T /tmp/test.txt ftp://{user}:{pass}@{ip}/'
      ],
      'vulnerabilities': [
        'nmap --script ftp-vuln-* -p 21 {ip}',
        'searchsploit --nmap ftp'
      ]
    },

    22: {
      'name': 'SSH',
      'risk_base': 5.0,
      'enumeration': [
        'ssh-keyscan -T 10 {ip}',
        'nmap --script ssh-hostkey,ssh-auth-methods,ssh2-enum-algos -p 22 {ip}',
        'ssh -o BatchMode=yes -o ConnectTimeout=10 {ip} 2>&1',
        'nc -nv {ip} 22'
      ],
      'authentication': [
        'nxc ssh {ip} -u {user} -p {pass}',
        'hydra -l {user} -p {pass} ssh://{ip}',
        'ssh -o PasswordAuthentication=yes -o ConnectTimeout=10 {user}@{ip}'
      ],
      'escalation': [
        'ssh {user}@{ip} "id; uname -a; whoami"',
        'ssh {user}@{ip} "sudo -l"',
        'ssh {user}@{ip} "find / -perm -4000 2>/dev/null"',
        'ssh {user}@{ip} "crontab -l"'
      ],
      'vulnerabilities': [
        'nmap --script ssh-vuln-* -p 22 {ip}',
        'searchsploit openssh'
      ]
    },

    23: {
      'name': 'Telnet',
      'risk_base': 8.0,
      'enumeration': [
        'nmap --script telnet-ntlm-info,telnet-encryption -p 23 {ip}',
        'nc -nv {ip} 23',
        'timeout 10 telnet {ip} 23'
      ],
      'authentication': [
        'hydra -l {user} -p {pass} telnet://{ip}',
        'nxc telnet {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'expect -c "spawn telnet {ip}; expect login:; send {user}\\r; expect Password:; send {pass}\\r; interact"'
      ]
    },

    25: {
      'name': 'SMTP',
      'risk_base': 6.0,
      'enumeration': [
        'nmap --script smtp-commands,smtp-enum-users,smtp-open-relay -p 25 {ip}',
        'nc -nv {ip} 25',
        'timeout 10 telnet {ip} 25'
      ],
      'authentication': [
        'nxc smtp {ip} -u {user} -p {pass}',
        'swaks --to test@{ip} --from test@test.com --server {ip}'
      ],
      'escalation': [
        'smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/top-usernames-shortlist.txt -t {ip}',
        'nmap --script smtp-vuln-* -p 25 {ip}'
      ]
    },

    53: {
      'name': 'DNS',
      'risk_base': 6.0,
      'enumeration': [
        'dig @{ip} version.bind chaos txt',
        'dig @{ip} {domain} axfr',
        'dig @{ip} {domain} any',
        'nmap --script dns-zone-transfer,dns-recursion,dns-cache-snoop -p 53 {ip}',
        'host -t ns {domain} {ip}'
      ],
      'escalation': [
        'dig @{ip} {domain} axfr',
        'fierce -dns {domain} -dnsserver {ip}',
        'dnsenum --dnsserver {ip} {domain}',
        'gobuster dns -d {domain} -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -r {ip}'
      ],
      'vulnerabilities': [
        'nmap --script dns-vuln-* -p 53 {ip}'
      ]
    },

    80: {
      'name': 'HTTP',
      'risk_base': 4.0,
      'enumeration': [
        'feroxbuster -u http://{ip} -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 50 --silent --depth 3 -x php,txt,html,js,json,xml,bak',
        'gobuster dir -u http://{ip} -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 --no-error -x php,txt,html,js',
        'whatweb -a3 http://{ip}',
        'curl -sI http://{ip} --max-time 15',
        'nikto -h http://{ip} -C all -timeout 60'
      ],
      'authentication': [
        'hydra -l {user} -p {pass} http-get://{ip}',
        'wfuzz -c -z list,{user} -z list,{pass} --hc 401,403 http://{ip}/login'
      ],
      'escalation': [
        'nuclei -u http://{ip} -t /root/nuclei-templates/ -c 50',
        'sqlmap -u "http://{ip}/?id=1" --batch --banner',
        'ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u http://{ip}/FUZZ',
        'feroxbuster -u http://{ip}/api -w /usr/share/seclists/Discovery/Web-Content/api/objects.txt -t 30 --silent'
      ],
      'vulnerabilities': [
        'nmap --script http-vuln-* -p 80 {ip}',
        'wapiti -u http://{ip}',
        'skipfish -o /tmp/skipfish_{ip} http://{ip}'
      ]
    },

    135: {
      'name': 'RPC-MSRPC',
      'risk_base': 7.0,
      'enumeration': [
        'nxc smb {ip} -u "" -p ""',
        'rpcclient -U "" -N {ip}',
        'nmap --script msrpc-enum -p 135 {ip}'
      ],
      'authentication': [
        'rpcclient -U {user}%{pass} {ip}',
        'nxc smb {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'rpcclient -U {user}%{pass} {ip} -c "enumdomusers"',
        'rpcclient -U {user}%{pass} {ip} -c "enumdomgroups"',
        'rpcclient -U {user}%{pass} {ip} -c "querydispinfo"'
      ]
    },

    139: {
      'name': 'NetBIOS',
      'risk_base': 7.0,
      'enumeration': [
        'nbtscan {ip}',
        'nmap --script nbstat,smb-os-discovery -p 139 {ip}',
        'smbclient -L //{ip}/ -N',
        'enum4linux -a {ip}'
      ],
      'authentication': [
        'smbclient -L //{ip}/ -U {user}%{pass}',
        'nxc smb {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'smbmap -H {ip} -u {user} -p {pass}',
        'smbclient //{ip}/C$ -U {user}%{pass}',
        'nxc smb {ip} -u {user} -p {pass} --shares'
      ]
    },

    161: {
      'name': 'SNMP',
      'risk_base': 8.0,
      'enumeration': [
        'snmpwalk -v1 -c public {ip}',
        'snmpwalk -v2c -c public {ip}',
        'onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt {ip}',
        'nmap --script snmp-* -p 161 {ip}'
      ],
      'escalation': [
        'snmpwalk -v1 -c public {ip} 1.3.6.1.2.1.25.4.2.1.2',  # Running processes
        'snmpwalk -v1 -c public {ip} 1.3.6.1.2.1.25.6.3.1.2',  # Software installed
        'snmpwalk -v1 -c public {ip} 1.3.6.1.4.1.77.1.2.25',   # Users
        'snmp-check {ip} -c public'
      ],
      'vulnerabilities': [
        'nmap --script snmp-vuln-* -p 161 {ip}'
      ]
    },

    389: {
      'name': 'LDAP',
      'risk_base': 6.5,
      'enumeration': [
        'ldapsearch -x -H ldap://{ip} -s base',
        'nxc ldap {ip} -u "" -p ""',
        'nmap --script ldap-* -p 389 {ip}'
      ],
      'authentication': [
        'ldapsearch -x -H ldap://{ip} -D "{user}" -w {pass}',
        'nxc ldap {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'nxc ldap {ip} -u {user} -p {pass} --users',
        'nxc ldap {ip} -u {user} -p {pass} --groups',
        'nxc ldap {ip} -u {user} -p {pass} --asreproast /tmp/asrep_{ip}.txt',
        'nxc ldap {ip} -u {user} -p {pass} --kerberoasting /tmp/kerb_{ip}.txt'
      ]
    },

    443: {
      'name': 'HTTPS',
      'risk_base': 3.0,
      'enumeration': [
        'testssl.sh --fast --quiet https://{ip}',
        'feroxbuster -u https://{ip} -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -k -t 50 --silent --depth 3 -x php,txt,html,js',
        'sslscan {ip}:443',
        'curl -sIk https://{ip} --max-time 15'
      ],
      'authentication': [
        'hydra -l {user} -p {pass} https-get://{ip}',
        'wfuzz -c -z list,{user} -z list,{pass} --hc 401,403 https://{ip}/login'
      ],
      'escalation': [
        'nuclei -u https://{ip} -t /root/nuclei-templates/ -c 50',
        'sqlmap -u "https://{ip}/?id=1" --batch --banner',
        'feroxbuster -u https://{ip}/api -w /usr/share/seclists/Discovery/Web-Content/api/objects.txt -k -t 30 --silent'
      ],
      'ssl_analysis': [
        'testssl.sh --vulnerable --quiet https://{ip}',
        'nmap --script ssl-enum-ciphers,ssl-cert,ssl-date -p 443 {ip}'
      ]
    },

    445: {
      'name': 'SMB',
      'risk_base': 9.0,
      'enumeration': [
        'nxc smb {ip} -u "" -p "" --shares',
        'smbclient -L //{ip}/ -N',
        'enum4linux -a {ip}',
        'nmap --script smb-os-discovery,smb-security-mode,smb-enum-shares -p 445 {ip}'
      ],
      'authentication': [
        'nxc smb {ip} -u {user} -p {pass}',
        'smbclient -L //{ip}/ -U {user}%{pass}'
      ],
      'escalation': [
        'nxc smb {ip} -u {user} -p {pass} --shares',
        'nxc smb {ip} -u {user} -p {pass} --sam',
        'nxc smb {ip} -u {user} -p {pass} --lsa',
        'nxc smb {ip} -u {user} -p {pass} --ntds',
        'smbmap -H {ip} -u {user} -p {pass} -R',
        'nxc smb {ip} -u {user} -p {pass} -M spider_plus',
        'nxc smb {ip} -u {user} -p {pass} --rid-brute'
      ],
      'vulnerabilities': [
        'nmap --script smb-vuln-* -p 445 {ip}',
        'nxc smb {ip} -u "" -p "" -M zerologon',
        'nxc smb {ip} -u "" -p "" -M petitpotam'
      ]
    },

    1433: {
      'name': 'MSSQL',
      'risk_base': 8.0,
      'enumeration': [
        'nmap --script ms-sql-info,ms-sql-config -p 1433 {ip}',
        'nxc mssql {ip} -u "" -p ""'
      ],
      'authentication': [
        'nxc mssql {ip} -u {user} -p {pass}',
        'sqlcmd -S {ip} -U {user} -P {pass}'
      ],
      'escalation': [
        'nxc mssql {ip} -u {user} -p {pass} --local-auth',
        'nxc mssql {ip} -u {user} -p {pass} -x "whoami"',
        'sqlmap -d "mssql://{user}:{pass}@{ip}:1433/master" --banner'
      ],
      'vulnerabilities': [
        'nmap --script ms-sql-vuln-* -p 1433 {ip}'
      ]
    },

    3306: {
      'name': 'MySQL',
      'risk_base': 7.0,
      'enumeration': [
        'nmap --script mysql-info,mysql-enum -p 3306 {ip}',
        'nxc mysql {ip} -u "" -p ""'
      ],
      'authentication': [
        'mysql -h {ip} -u {user} -p{pass}',
        'nxc mysql {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'mysql -h {ip} -u {user} -p{pass} -e "SELECT version();"',
        'mysql -h {ip} -u {user} -p{pass} -e "SHOW DATABASES;"',
        'mysql -h {ip} -u {user} -p{pass} -e "SELECT user,password FROM mysql.user;"',
        'sqlmap -d "mysql://{user}:{pass}@{ip}:3306/" --banner'
      ],
      'vulnerabilities': [
        'nmap --script mysql-vuln-* -p 3306 {ip}'
      ]
    },

    3389: {
      'name': 'RDP',
      'risk_base': 8.5,
      'enumeration': [
        'nmap --script rdp-enum-encryption,rdp-vuln-ms12-020 -p 3389 {ip}',
        'nxc rdp {ip} -u "" -p ""'
      ],
      'authentication': [
        'nxc rdp {ip} -u {user} -p {pass}',
        'hydra -l {user} -p {pass} rdp://{ip}'
      ],
      'escalation': [
        'rdesktop -u {user} -p {pass} {ip}',
        'xfreerdp /v:{ip} /u:{user} /p:{pass} +clipboard'
      ],
      'vulnerabilities': [
        'nmap --script rdp-vuln-* -p 3389 {ip}'
      ]
    },

    5432: {
      'name': 'PostgreSQL',
      'risk_base': 7.0,
      'enumeration': [
        'nmap --script pgsql-brute -p 5432 {ip}',
        'nxc postgres {ip} -u "" -p ""'
      ],
      'authentication': [
        'psql -h {ip} -U {user} -d postgres',
        'nxc postgres {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'psql -h {ip} -U {user} -d postgres -c "SELECT version();"',
        'psql -h {ip} -U {user} -d postgres -c "\\l"',
        'sqlmap -d "postgresql://{user}:{pass}@{ip}:5432/" --banner'
      ]
    },

    5985: {
      'name': 'WinRM',
      'risk_base': 7.5,
      'enumeration': [
        'nmap --script http-methods,http-headers -p 5985 {ip}',
        'nxc winrm {ip} -u "" -p ""'
      ],
      'authentication': [
        'nxc winrm {ip} -u {user} -p {pass}',
        'evil-winrm -i {ip} -u {user} -p {pass}'
      ],
      'escalation': [
        'evil-winrm -i {ip} -u {user} -p {pass} -e /tmp',
        'nxc winrm {ip} -u {user} -p {pass} -x "whoami"',
        'nxc winrm {ip} -u {user} -p {pass} -x "powershell.exe Get-Process"'
      ]
    },

    6379: {
      'name': 'Redis',
      'risk_base': 9.0,
      'enumeration': [
        'redis-cli -h {ip} -p 6379 info',
        'nmap --script redis-info -p 6379 {ip}',
        'nxc redis {ip}'
      ],
      'escalation': [
        'redis-cli -h {ip} -p 6379 --scan',
        'redis-cli -h {ip} -p 6379 CONFIG GET "*"',
        'redis-cli -h {ip} -p 6379 EVAL "return redis.call(\'CONFIG\',\'GET\',\'*\')" 0',
        'redis-cli -h {ip} -p 6379 FLUSHALL'
      ],
      'vulnerabilities': [
        'nmap --script redis-vuln-* -p 6379 {ip}'
      ]
    },

    8080: {
      'name': 'HTTP-Proxy',
      'risk_base': 6.0,
      'enumeration': [
        'feroxbuster -u http://{ip}:8080 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 50 --silent --depth 3',
        'whatweb -a3 http://{ip}:8080',
        'curl -sI http://{ip}:8080 --max-time 15'
      ],
      'escalation': [
        'nuclei -u http://{ip}:8080 -t /root/nuclei-templates/',
        'feroxbuster -u http://{ip}:8080/api -w /usr/share/seclists/Discovery/Web-Content/api/objects.txt -t 30 --silent'
      ]
    },

    8443: {
      'name': 'HTTPS-Alt',
      'risk_base': 6.0,
      'enumeration': [
        'testssl.sh --fast --quiet https://{ip}:8443',
        'feroxbuster -u https://{ip}:8443 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -k -t 50 --silent',
        'curl -sIk https://{ip}:8443 --max-time 15'
      ]
    },

    9200: {
      'name': 'Elasticsearch',
      'risk_base': 8.5,
      'enumeration': [
        'curl -s http://{ip}:9200/_cluster/health',
        'curl -s http://{ip}:9200/_cat/indices',
        'nmap --script elasticsearch-info -p 9200 {ip}'
      ],
      'escalation': [
        'curl -s http://{ip}:9200/_search?pretty',
        'curl -s http://{ip}:9200/_cluster/settings?pretty',
        'elasticdump --input=http://{ip}:9200 --output=/tmp/elastic_{ip}.json'
      ]
    },

    27017: {
      'name': 'MongoDB',
      'risk_base': 8.0,
      'enumeration': [
        'nmap --script mongodb-info -p 27017 {ip}',
        'mongo {ip}:27017 --eval "db.stats()" --quiet'
      ],
      'escalation': [
        'mongo {ip}:27017 --eval "db.adminCommand(\'listCollections\')"',
        'mongo {ip}:27017 --eval "show dbs"',
        'mongo {ip}:27017 --eval "db.runCommand({{connectionStatus : 1}})"'
      ]
    },

    2375: {
      'name': 'Docker-API',
      'risk_base': 9.5,
      'enumeration': [
        'curl -s http://{ip}:2375/version',
        'docker -H tcp://{ip}:2375 info'
      ],
      'escalation': [
        'docker -H tcp://{ip}:2375 ps -a',
        'docker -H tcp://{ip}:2375 images',
        'docker -H tcp://{ip}:2375 run -it --rm -v /:/host alpine chroot /host sh'
      ]
    },

    2376: {
      'name': 'Docker-TLS',
      'risk_base': 7.0,
      'enumeration': [
        'openssl s_client -connect {ip}:2376',
        'docker --tlsverify -H tcp://{ip}:2376 info'
      ]
    },

    # Additional services from the original that were missing
    88: {
      'name': 'Kerberos',
      'risk_base': 7.0,
      'enumeration': [
        'nmap --script krb5-enum-users -p 88 {ip}',
        'nxc ldap {ip} -u "" -p ""',
      ],
      'authentication': [
        'nxc ldap {ip} -u {user} -p {pass} --asreproast /tmp/asrep_{ip}.txt',
        'nxc ldap {ip} -u {user} -p {pass} --kerberoasting /tmp/kerb_{ip}.txt'
      ],
      'fallback': ['nc -v {ip} 88']
    },

    464: {
      'name': 'Kerberos-PW',
      'risk_base': 6.0,
      'enumeration': ['nmap --script krb5-* -p 464 {ip}'],
      'fallback': ['nc -v {ip} 464']
    },

    593: {
      'name': 'RPC-HTTP',
      'risk_base': 7.0,
      'enumeration': [
        'nmap --script rpc-* -p 593 {ip}',
        'rpcclient -U "" -N {ip}'
      ],
      'fallback': ['nc -v {ip} 593']
    },

    636: {
      'name': 'LDAPS',
      'risk_base': 6.5,
      'enumeration': [
        'ldapsearch -x -H ldaps://{ip} -s base -o ldif-wrap=no -o tls_reqcert=never',
        'nmap --script ssl-cert -p 636 {ip}',
        'nxc ldap {ip} -u "" -p ""'
      ],
      'fallback': ['openssl s_client -connect {ip}:636 -verify_return_error']
    },

    3268: {
      'name': 'Global-Catalog',
      'risk_base': 6.0,
      'enumeration': [
        'ldapsearch -x -H ldap://{ip}:3268 -s base',
        'nmap --script ldap-* -p 3268 {ip}'
      ],
      'fallback': ['nc -v {ip} 3268']
    },

    3269: {
      'name': 'Global-Catalog-SSL',
      'risk_base': 6.0,
      'enumeration': [
        'ldapsearch -x -H ldaps://{ip}:3269 -s base -o tls_reqcert=never',
        'nmap --script ldap-* -p 3269 {ip}'
      ],
      'fallback': ['openssl s_client -connect {ip}:3269']
    }
  }

GENERIC_CHECKS = {
    'name': 'Generic',
    'risk_base': 5.0,
    'enum': [
        'nc -v -n -w 5 {ip} {port}',
        'curl -I http://{ip}:{port} --max-time 15',
        'nmap -sV -p {port} --script="banner,(safe or default) and not broadcast" {ip}'
    ],
    'fallback': [
        'telnet {ip} {port}',
        'socat - TCP:{ip}:{port},connect-timeout=15'
    ]
}

# Integration configurations
INTEGRATION_COMMANDS = {
    'slack_notify': 'curl -X POST -H "Content-type: application/json" --data \'{"text":"🔥 Scan complete for {ip} - {critical_count} critical findings"}\' {slack_webhook}',
    'jira_ticket': 'curl -X POST -u {jira_user}:{jira_token} -H "Content-Type: application/json" --data \'{"fields": {"project": {"key": "SEC"}, "summary": "Security vulnerabilities found on {ip}", "description": "Automated scan found {total_issues} issues"}}\' {jira_url}/rest/api/2/issue/',
    'teams_notify': 'curl -X POST -H "Content-Type: application/json" --data \'{"text": "Chainsaw Alert: {critical_count} critical vulnerabilities found on {ip}"}\' {teams_webhook}',
    'discord_notify': 'curl -X POST -H "Content-Type: application/json" --data \'{"embeds": [{"title": "🔥 Chainsaw Alert", "description": "Target: {ip}\\nCritical Issues: {critical_count}\\nTotal Issues: {total_issues}", "color": 15548997, "footer": {"text": "Chainsaw Network Analysis"}}]}\' {discord_webhook}',
    'ifttt_trigger': 'curl -X POST -H "Content-Type: application/json" --data \'{"value1": "{ip}", "value2": "{critical_count}", "value3": "{total_issues}"}\' https://maker.ifttt.com/trigger/{ifttt_event}/with/key/{ifttt_key}'
}

class CyberScanner:
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.attack_paths = []
        self.risk_scores = {}
        self.start_time = datetime.now()
        self.shutdown_handler = GracefulShutdown() 
        
    def banner(self):
        """Display enhanced cyberpunk banner with error handling"""
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
      
        try:
            import sys
            print(banner_text)
            sys.stdout.flush()
        except (BlockingIOError, BrokenPipeError, OSError):
            # Fallback to simple banner
            try:
                print("CHAINSAW - Network Security Scanner v2.0")
                print("[!] Target Acquired - Initiating Scan")
                sys.stdout.flush()
            except:
                pass  # Silent fallback
        
    def run_cmd_enhanced(self, cmd, timeout=30):
        """Enhanced command execution with better error handling"""
        try:
          # Check if shutdown requested
          if self.shutdown_handler.shutdown:
            return {'command': cmd, 'output': 'Interrupted', 'success': False}
          
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
        except KeyboardInterrupt:
          print(f"{chr(27)}[0m\n[!] Command interrupted: {cmd}")
          raise
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
            cmd = f"curl -k -s -I {protocol}://{ip}:{port}{endpoint} --max-time 15"
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
        
#       print(f"[*] Testing port {port} ({config.get('name', 'Unknown')})...")
        
        # Run standard checks with validation
        for check_type in ['anon', 'auth', 'enum']:
          if check_type in config:
            print(f"[*] Running {check_type} checks on port {port}...")
            checks = config[check_type] if isinstance(config[check_type], list) else [config[check_type]]
            
            # VALIDATE COMMANDS BEFORE EXECUTION
            validated_checks = self.validate_and_fallback_commands(checks, replacements)
            
            if not validated_checks:
              print(f"[!] No valid tools for {check_type} checks on port {port}")
              continue
            
            with ThreadPoolExecutor(max_workers=3) as executor:
              futures = []
              for check in validated_checks:
                if check_type == 'auth' and (not user or not password):
                  print(f"[!] Skipping auth check (no credentials): {check}")
                  continue
                processed_cmd = check.format(**replacements)
#               print(f"[*] Executing: {processed_cmd}")
                future = executor.submit(self.run_cmd_enhanced, processed_cmd, timeout=45)
                futures.append(future)
                
#             for future in as_completed(futures, timeout=60):
#               try:
#                 result = future.result(timeout=5)
#                 if result['success']:
#                   print(f"[+] Command succeeded: {result['command'][:50]}...")
#                 else:
#                   print(f"[!] Command failed: {result['command'][:50]}...")
#                 results.append(result)
#               except Exception as e:
#                 print(f"[!] Tool execution error: {str(e)}")
                  
                  
        # Only run fallbacks if NO successes (not just enum failures)
        if 'fallback' in config and not any(res.get('success', False) for res in results):
          print(f"[*] Running fallback tools for port {port}...")
          fallbacks = config['fallback'] if isinstance(config['fallback'], list) else [config['fallback']]
          for fallback in fallbacks[:2]:  # Limit fallbacks
            processed_cmd = fallback.format(**replacements)
#           print(f"[*] Fallback: {processed_cmd}")
            result = self.run_cmd_enhanced(processed_cmd, timeout=15)  # Shorter timeout for fallbacks
            results.append(result)
          
        print(f"[+] Completed {len(results)} tests on port {port}")
        return results        
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
        threat_level, status = self.get_overall_threat_level()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>CHAINSAW ANALYSIS :: {ip}</title>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          {TERMINAL_CSS}
        </head>
        <body>
          <div class="scan-line"></div>
          <div class="terminal-header">
            <h1 class="glitch">// CHAINSAW NETWORK ANALYSIS</h1>
            <h2>TARGET ACQUIRED: {ip}</h2>
            <h3>{datetime.now().strftime('[%Y-%m-%d %H:%M:%S UTC]')}</h3>
            <div style="margin-top: 1rem;">
              <span class="success">SCAN STATUS: COMPLETE</span> | 
              <span class="warning">DURATION: {datetime.now() - self.start_time}</span> | 
              <span class="{'fail' if threat_level in ['CRITICAL', 'HIGH'] else 'warning' if threat_level == 'ELEVATED' else 'success'}">THREAT LEVEL: {threat_level}</span>
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
          
          json_filename = f"chainsaw_{ip}_{datetime.now().strftime('%Y%m%d%H%M')}.json"
          with open(json_filename, 'w') as f:
            self.shutdown_handler.add_cleanup_file(json_filename)
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
              <pre class="{'success' if status == 'ACCEPTABLE' else 'warning' if status == 'CONCERNING' else 'fail'}">
      [!] SYSTEM SECURITY STATUS: {status}
      [!] CHAINSAW ANALYSIS COMPLETE  
      [!] STAY VIGILANT IN THE DIGITAL SHADOWS
              </pre>
            </div>
          </body>
          </html>
          """
        return html
    
    def get_overall_threat_level(self):
      """Calculate overall threat level based on risk scores"""
      if not self.risk_scores:
        return 'LOW', 'ACCEPTABLE'
      
      max_score = max(self.risk_scores.values())
      avg_score = sum(self.risk_scores.values()) / len(self.risk_scores.values())
      critical_count = sum(1 for score in self.risk_scores.values() if score >= 9.0)
      high_count = sum(1 for score in self.risk_scores.values() if score >= 7.0)
      
      # Determine threat level
      if critical_count > 0 or max_score >= 9.0:
        return 'CRITICAL', 'COMPROMISED'
      elif high_count > 1 or max_score >= 8.0 or avg_score >= 7.0:
        return 'HIGH', 'ELEVATED'
      elif high_count > 0 or max_score >= 7.0 or avg_score >= 5.5:
        return 'ELEVATED', 'CONCERNING'
      else:
        return 'LOW', 'ACCEPTABLE'

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
      
        # Enhanced nmap scanning
        nmap_opts = "-T4 --top-ports 1000"
        if self.args.evasion:
            nmap_opts = "-Pn -T1 --top-ports 1000"
        
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
          try:
            futures = {}
            for port, service in open_ports:
              if self.shutdown_handler.shutdown:
                break
            for port, service in open_ports:
              # Add port to replacements for each service
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
#               print(f"[+] Completed scan for port {port} (Risk: {self.risk_scores[port]:.1f})")
              except Exception as e:
                print(f"[!] Error scanning port {port}: {str(e)}")
                self.results[port] = []
                self.risk_scores[port] = 0.0
          except KeyboardInterrupt:
            print(f"{chr(27)}[0m[!] Shutting down gracefully...")
            executor.shutdown(wait=False)
            raise
        
        # Analyze attack paths
        self.attack_paths = self.analyze_attack_paths(self.results)
        print(f"[+] Identified {len(self.attack_paths)} potential attack paths")
        
        # Generate report
        report = self.generate_enhanced_report(self.results, self.args.ip)
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        filename = f"chainsaw_{self.args.ip}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
          self.shutdown_handler.add_cleanup_file(filename)
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
# Chainsaw Continuous Monitor for {self.args.ip}
while true; do
    echo "[$(date)] Running continuous scan..."
    python3 {os.path.abspath(__file__)} {self.args.ip} --no-browser
    sleep 3600  # Run every hour
done
"""
        monitor_filename = f"chainsaw_monitor_{self.args.ip}.sh"
        with open(monitor_filename, 'w') as f:
            f.write(monitor_script)
        os.chmod(monitor_filename, 0o755)
        print(f"[+] Continuous monitoring script created: {monitor_filename}")
        
    def validate_and_fallback_commands(self, commands, replacements):
      """Validate tools exist and provide fallbacks"""
      validated_commands = []
      
      # Tools that commonly fail and their fallbacks
      tool_fallbacks = {
        'kerbrute': f'nmap --script=krb5-enum-users -p 88 {replacements["ip"]}',
        'dnsrecon': f'nmap --script=dns-* -p 53 {replacements["ip"]}',
        'crackmapexec': f'nxc',  # crackmapexec is now nxc
      }
      
      for cmd in commands:
        tool = cmd.split()[0]
        
        # Handle tool aliases
        if tool == 'crackmapexec':
          cmd = cmd.replace('crackmapexec', 'nxc', 1)
          tool = 'nxc'
          
        # Check if tool exists
        if shutil.which(tool):
          validated_commands.append(cmd)
        elif tool in tool_fallbacks:
          print(f"[!] {tool} not found, using fallback")
          validated_commands.append(tool_fallbacks[tool])
        else:
          print(f"[!] Skipping missing tool: {tool}")
          
      return validated_commands

def main():
    # Check and install tools first
    check_and_install_tools()
    
    # Setup wordlists for macOS
    if platform.system().lower() == 'darwin':
      setup_macos_wordlists()
      check_wordlists()

    parser = argparse.ArgumentParser(
        description='Chainsaw Network Penetration Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  Examples: 
    python3 chainsaw.py 192.168.1.1
    python3 chainsaw.py target.com --evasion --api-test
    python3 chainsaw.py server.com -u admin -p pass --continuous --export-json
    python3 chainsaw.py site.com --integrations discord_notify --discord-webhook "URL"
    python3 chainsaw.py 10.0.0.1 --integrations slack_notify ifttt_trigger --slack-webhook "URL" --ifttt-key "KEY" --ifttt-event "alert"
    python3 chainsaw.py target.com --evasion --api-test --risk-score --export-json --no-browser
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
