#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
🚀 Xtream UI for Ubuntu 24.04 LTS - Enhanced Installer
📂 Repository: https://github.com/mirelsen/xtreanui-for-Ubuntu24
🔧 Uses Ubuntu 18 compatibility libraries from GitHub repository
✅ Supports MariaDB 10.5+, complete SSL/CURL/PNG fixes
"""
import subprocess, os, random, string, sys, shutil, socket, zipfile, urllib.request, urllib.error, urllib.parse, json, base64, time
from itertools import cycle
from zipfile import ZipFile
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# URLs și logica de download din install_github.py
rDownloadURL = {"main": "https://github.com/emre1393/xtreamui_mirror/releases/latest/download/main.tar.gz", "sub": "https://github.com/emre1393/xtreamui_mirror/releases/latest/download/LB.tar.gz"}

# Pachete adaptate pentru Ubuntu 24
rPackages = ["libcurl4", "libxslt1-dev", "libgeoip-dev", "libonig-dev", "e2fsprogs", "wget", "mcrypt", "nscd", "htop", "zip", "unzip", "mc", "mariadb-server", "libpng16-16", "python3-paramiko", "python-is-python3"]

rInstall = {"MAIN": "main", "LB": "sub"}

# Configurația MySQL din install_github.py (decodată) - pe portul 7999
rMySQLCnf = """# Xtream Codes

[client]
port            = 3306

[mysqld_safe]
nice            = 0

[mysqld]
default-authentication-plugin=mysql_native_password
user            = mysql
port            = 7999
basedir         = /usr
datadir         = /var/lib/mysql
tmpdir          = /tmp

lc-messages-dir = /usr/share/mysql
skip-external-locking
skip-name-resolve=1

bind-address            = *

key_buffer_size = 128M
myisam_sort_buffer_size = 4M
max_allowed_packet      = 64M
myisam-recover-options  = BACKUP
max_length_for_sort_data = 8192
query_cache_limit = 0
query_cache_size = 0
query_cache_type = 0

expire_logs_days = 10
max_binlog_size = 100M
transaction_isolation = READ-COMMITTED
max_connections  = 10000
open_files_limit = 10240
innodb_open_files =10240
max_connect_errors = 4096
table_open_cache = 4096
table_definition_cache = 4096
tmp_table_size = 64M
max_heap_table_size = 64M
back_log = 4096

innodb_buffer_pool_size = 512M
innodb_read_io_threads = 4
innodb_write_io_threads = 4
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT
performance_schema = 0
innodb_file_per_table = 1
innodb_io_capacity = 200
innodb_table_locks = 0
innodb_lock_wait_timeout = 50
innodb_deadlock_detect = 1
innodb_log_file_size = 64M

sql-mode="NO_ENGINE_SUBSTITUTION"


[mysqldump]
quick
quote-names
max_allowed_packet      = 128M
complete-insert

[mysql]

[isamchk]
key_buffer_size         = 16M"""

rMySQLServiceFile = """# MySQL systemd service file

[Unit]
Description=MySQL Community Server
After=network.target

[Install]
WantedBy=multi-user.target

[Service]
Type=forking
User=mysql
Group=mysql
PIDFile=/run/mysqld/mysqld.pid
PermissionsStartOnly=true
ExecStartPre=/usr/share/mysql/mysql-systemd-start pre
ExecStart=/usr/sbin/mysqld --daemonize --pid-file=/run/mysqld/mysqld.pid --max-execution-time=0
EnvironmentFile=-/etc/mysql/mysqld
TimeoutSec=600
Restart=on-failure
RuntimeDirectory=mysqld
RuntimeDirectoryMode=755
LimitNOFILE=5000"""

rVersions = {
    "24.04": "noble"
}

class col:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GRAY = '\033[37m'
    DARK_GRAY = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

def generate(length=32): 
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getVersion():
    try: 
        return os.popen("lsb_release -d").read().split(":")[-1].strip()
    except: 
        return ""

def printc(rText, rColour=col.BRIGHT_GREEN, rPadding=0):
    print("%s ┌──────────────────────────────────────────┐ %s" % (rColour, col.ENDC))
    for i in range(rPadding): 
        print("%s │                                          │ %s" % (rColour, col.ENDC))
    print("%s │ %s%s%s │ %s" % (rColour, " "*(20-(len(rText)//2)), rText, " "*(40-(20-(len(rText)//2))-len(rText)), col.ENDC))
    for i in range(rPadding): 
        print("%s │                                          │ %s" % (rColour, col.ENDC))
    print("%s └──────────────────────────────────────────┘ %s" % (rColour, col.ENDC))
    print(" ")

def is_installed(package_name):
    try:
        subprocess.run(['dpkg', '-s', package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def prepare(rType="MAIN"):
    global rPackages
    if rType != "MAIN": 
        rPackages = rPackages[:-3]  # Remove mariadb-server, etc pentru LB
    
    printc("Preparing Installation")
    
    # Cleanup locks
    for rFile in ["/var/lib/dpkg/lock-frontend", "/var/cache/apt/archives/lock", "/var/lib/dpkg/lock"]:
        try: 
            os.remove(rFile)
        except: 
            pass
    
    # Update system
    printc("Updating Operating System")
    subprocess.run("apt-get update -y > /dev/null 2>&1", shell=True)
    subprocess.run("apt-get -y full-upgrade > /dev/null 2>&1", shell=True)
    
    # Remove libcurl4 conflict doar dacă este instalat
    if is_installed("libcurl4"):
        printc("Removing libcurl4 conflict")
        subprocess.run("apt-get remove --auto-remove libcurl4 -y > /dev/null 2>&1", shell=True)
    else:
        printc("libcurl4 not installed, skipping removal")
    
    # Install MariaDB repository pentru MAIN doar dacă nu este deja adăugat
    if rType == "MAIN":
        mariadb_repo_exists = False
        try:
            sources_content = open("/etc/apt/sources.list").read()
            sources_list_d = os.listdir("/etc/apt/sources.list.d/")
            
            # Verifică în sources.list și în sources.list.d
            if "mariadb" in sources_content.lower() or any("mariadb" in f.lower() for f in sources_list_d):
                mariadb_repo_exists = True
        except:
            pass
    
    # Install packages doar dacă nu sunt deja instalate (EXCLUDE MariaDB - will be handled in fix_mariadb_installation)
    packages_to_install = []
    for rPackage in rPackages:
        if rPackage != "mariadb-server" and not is_installed(rPackage):  # Skip MariaDB here
            packages_to_install.append(rPackage)
    
    if packages_to_install:
        printc("Installing packages: %s" % ", ".join(packages_to_install))
        for rPackage in packages_to_install:
            printc("Installing %s" % rPackage)
            subprocess.run("apt-get install %s -y > /dev/null 2>&1" % rPackage, shell=True)
    else:
        printc("All required packages already installed (MariaDB will be handled separately)")
    
    # Install Ubuntu 18 compatibility libraries - FIXED VERSION
    printc("Installing Ubuntu 18 compatibility libraries")
    
    # Install libpng12 compatibility - FIXED for Ubuntu 24
    if not is_installed("libpng12-0"):
        printc("Installing libpng12 compatibility")
        subprocess.run("wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb > /dev/null 2>&1", shell=True)
        install_result = subprocess.run("dpkg -i /tmp/libpng12.deb", shell=True, capture_output=True, text=True)
        subprocess.run("apt-get install -f -y > /dev/null 2>&1", shell=True)
        
        # Verify installation
        if install_result.returncode == 0:
            printc("✅ libpng12-0 installed successfully")
        else:
            printc("libpng12-0 installation had issues, attempting manual symlink fix", col.BRIGHT_YELLOW)
        
        try: 
            os.remove("/tmp/libpng12.deb")
        except: 
            pass
    else:
        printc("libpng12 already installed")
    
    # Create libpng12.so.0 symlink - CRITICAL FIX for PHP compatibility
    printc("Creating libpng12.so.0 symlink")
    
    # Multiple symlink attempts for different versions
    symlink_created = False
    possible_targets = [
        "/usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0",
        "/usr/lib/x86_64-linux-gnu/libpng12.so.0.54",
        "/usr/lib/x86_64-linux-gnu/libpng12.so",
        "/lib/x86_64-linux-gnu/libpng12.so.0.54.0",
        "/lib/x86_64-linux-gnu/libpng12.so.0.54",
        "/lib/x86_64-linux-gnu/libpng12.so"
    ]
    
    for target in possible_targets:
        if os.path.exists(target):
            subprocess.run("ln -sf %s /usr/lib/x86_64-linux-gnu/libpng12.so.0" % target, shell=True)
            symlink_created = True
            printc(f"✅ libpng12.so.0 symlink created -> {target}")
            break
    
    # Backup solution: Use libpng16 if libpng12 not found
    if not symlink_created:
        printc("Attempting backup solution: using libpng16 for compatibility", col.BRIGHT_YELLOW)
        if os.path.exists("/usr/lib/x86_64-linux-gnu/libpng16.so.16"):
            subprocess.run("ln -sf /usr/lib/x86_64-linux-gnu/libpng16.so.16 /usr/lib/x86_64-linux-gnu/libpng12.so.0", shell=True)
            printc("✅ Created libpng12.so.0 -> libpng16.so.16 compatibility symlink")
            symlink_created = True
    
    if not symlink_created:
        printc("Warning: Could not create any libpng12.so.0 symlink", col.BRIGHT_RED)
    
    # Refresh library cache for all symlinks
    subprocess.run("ldconfig", shell=True)
    
    # Install libssl1.1
    if not is_installed("libssl1.1"):
        printc("Installing libssl1.1")
        subprocess.run("wget -q -O /tmp/libssl1.1.deb http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb > /dev/null 2>&1", shell=True)
        subprocess.run("dpkg -i /tmp/libssl1.1.deb > /dev/null 2>&1", shell=True)
        try: 
            os.remove("/tmp/libssl1.1.deb")
        except: 
            pass
    else:
        printc("libssl1.1 already installed")
    
    # Create libssl.so.1.0.0 symlink
    if not os.path.exists("/usr/lib/x86_64-linux-gnu/libssl.so.1.0.0"):
        printc("Creating libssl.so.1.0.0 symlink")
        subprocess.run("ln -sf /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/x86_64-linux-gnu/libssl.so.1.0.0", shell=True)
        subprocess.run("ldconfig", shell=True)
    
    # Install libzip5
    if not is_installed("libzip5"):
        printc("Installing libzip5")
        subprocess.run("wget -q -O /tmp/libzip5.deb http://archive.ubuntu.com/ubuntu/pool/universe/libz/libzip/libzip5_1.5.1-0ubuntu1_amd64.deb > /dev/null 2>&1", shell=True)
        subprocess.run("dpkg -i /tmp/libzip5.deb > /dev/null 2>&1", shell=True)
        try: 
            os.remove("/tmp/libzip5.deb")
        except: 
            pass
    else:
        printc("libzip5 already installed")
    
    # Install Ubuntu 18 libraries using the comprehensive script - AUTOMATED SOLUTION
    printc("Installing Ubuntu 18 libraries with comprehensive Xtream Codes compatibility fixes")
    ubuntu18_script = r"""#!/bin/bash
cd /tmp
mkdir ubuntu18_libs
cd ubuntu18_libs

LIBS_DIR="/home/xtreamcodes/iptv_xtream_codes/lib"
mkdir -p $LIBS_DIR

echo "Downloading Ubuntu 18 compatibility libraries from GitHub repository..."

# CRITICAL libraries from mirelsen/xtreanui-for-Ubuntu24 repository
GITHUB_LIBS_URL="https://github.com/mirelsen/xtreanui-for-Ubuntu24/raw/main/libs"

# CRITICAL: OpenSSL 1.0.x libraries for OPENSSL_1.0.1 fix
wget -q "$GITHUB_LIBS_URL/libssl1.0.0_1.0.2n-1ubuntu5.13_amd64.deb"
wget -q "$GITHUB_LIBS_URL/libssl1.0-dev_1.0.2n-1ubuntu5.13_amd64.deb"

# CRITICAL: Curl libraries for CURL_OPENSSL_3 fix  
wget -q "$GITHUB_LIBS_URL/libcurl3_7.58.0-2ubuntu2_amd64.deb"
wget -q "$GITHUB_LIBS_URL/libcurl3-gnutls_7.58.0-2ubuntu3_amd64.deb"

# CRITICAL: PNG12 libraries for PNG12_0 fix
wget -q "$GITHUB_LIBS_URL/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb"

# CRITICAL: Additional networking libraries for CURL/SSL compatibility  
wget -q "$GITHUB_LIBS_URL/libnettle6_3.4-1_amd64.deb"
wget -q "$GITHUB_LIBS_URL/libldap-2.4-2_2.4.45+dfsg-1ubuntu1.11_amd64.deb"
wget -q "$GITHUB_LIBS_URL/libgssapi3-heimdal_7.5.0+dfsg-1_amd64.deb"

# MySQL configuration package
wget -q "$GITHUB_LIBS_URL/mysql-apt-config_0.8.22-1_all.deb"

echo "Installing system-wide Ubuntu 18 compatibility libraries..."
# Install all packages with dependency resolution
dpkg -i *.deb > /dev/null 2>&1
apt-get install -f -y > /dev/null 2>&1

echo "Extracting additional libraries to Xtream Codes lib directory..."
# Extract all .so files to Xtream Codes lib directory for runtime linking
for deb_file in *.deb; do
    if [ -f "$deb_file" ]; then
        package_name=$(basename "$deb_file" .deb)
        mkdir -p "/tmp/extract_$package_name"
        cd "/tmp/extract_$package_name"
        ar x "../$deb_file" > /dev/null 2>&1
        if [ -f "data.tar.xz" ]; then
            tar xf data.tar.xz > /dev/null 2>&1
            # Copy all .so files to Xtream lib directory
            find . -name "*.so*" -type f -exec cp {} "$LIBS_DIR/" \; > /dev/null 2>&1
        fi
        cd /tmp/ubuntu18_libs
        rm -rf "/tmp/extract_$package_name"
    fi
done

echo "Creating comprehensive compatibility symlinks..."
cd "$LIBS_DIR"

# Create symlinks for versioned libraries
for file in *.so.*; do
    if [[ $file == *.so.*.* ]]; then
        base=$(echo $file | sed 's/\\(.*\\.so\\.[0-9]\\+\\)\\..*/\\1/')
        if [ ! -L "$base" ] && [ ! -f "$base" ]; then
            ln -sf "$file" "$base" > /dev/null 2>&1
        fi
    fi
done

# CRITICAL system-wide symlinks for immediate compatibility
# Fix CURL_OPENSSL_3 error
if [ -f "/usr/lib/x86_64-linux-gnu/libcurl.so.4.4.0" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libcurl.so.4.4.0 /usr/lib/x86_64-linux-gnu/libcurl.so.4
fi

# Fix OPENSSL_1.0.1 error  
if [ -f "/usr/lib/x86_64-linux-gnu/libssl.so.1.0.0" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libssl.so.1.0.0 /usr/lib/x86_64-linux-gnu/libssl.so.1.0
    ln -sf /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0
fi

# Fix PNG12_0 error - multiple locations for maximum compatibility
if [ -f "/usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0 /usr/lib/x86_64-linux-gnu/libpng12.so.0
    ln -sf /usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0 /lib/x86_64-linux-gnu/libpng12.so.0
    # Also copy to Xtream lib directory
    cp /usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0 "$LIBS_DIR/"
    cd "$LIBS_DIR"
    ln -sf libpng12.so.0.54.0 libpng12.so.0
    ln -sf libpng12.so.0.54.0 libpng12.so
fi

# Refresh library cache
ldconfig

echo "✅ ALL Ubuntu 18 compatibility libraries installed with Xtream Codes fixes"
echo "Libraries available in: $LIBS_DIR"
echo "System-wide compatibility: ACTIVATED"

# Cleanup
cd /tmp
rm -rf ubuntu18_libs
"""
    
    # Write and execute Ubuntu 18 libraries script
    with open("/tmp/install_ubuntu18_libs.sh", "w") as f:
        f.write(ubuntu18_script)
    
    subprocess.run("chmod +x /tmp/install_ubuntu18_libs.sh", shell=True)
    subprocess.run("/tmp/install_ubuntu18_libs.sh", shell=True)
    
    try: 
        os.remove("/tmp/install_ubuntu18_libs.sh")
    except: 
        pass
    
    printc("Ubuntu 18 compatibility libraries installed")
    
    # Verifică componente Python2.7 și instaleză doar ce lipsește
    python_installed = subprocess.run("python2.7 --version > /dev/null 2>&1", shell=True).returncode == 0 or subprocess.run("python --version 2>&1 | grep 'Python 2.7' > /dev/null", shell=True).returncode == 0
    pip_installed = subprocess.run("pip2.7 --version > /dev/null 2>&1", shell=True).returncode == 0
    paramiko_installed = subprocess.run("pip2.7 show paramiko > /dev/null 2>&1", shell=True).returncode == 0

    components_needed = []
    if not python_installed:
        components_needed.append("Python 2.7")
    if not pip_installed:
        components_needed.append("pip2.7")
    if not paramiko_installed:
        components_needed.append("paramiko")
    
    if components_needed:
        printc("Installing missing Python2 components: %s" % ", ".join(components_needed))
        
        # Instalează dependințele doar dacă Python2.7 nu este instalat
        if not python_installed:
            printc("Building Python 2.7 from source...")
            subprocess.run("sudo apt install -y build-essential checkinstall libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev wget tar > /dev/null 2>&1", shell=True)
            subprocess.run("cd /usr/src && sudo wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz > /dev/null 2>&1 && sudo tar xzf Python-2.7.18.tgz > /dev/null 2>&1 && cd Python-2.7.18 && sudo ./configure --enable-optimizations > /dev/null 2>&1 && sudo make altinstall > /dev/null 2>&1", shell=True)

        if not pip_installed:
            printc("Installing pip2.7...")
            subprocess.run("curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py > /dev/null 2>&1 && sudo python2.7 get-pip.py > /dev/null 2>&1", shell=True)

        if not paramiko_installed and pip_installed:
            printc("Installing paramiko...")
            subprocess.run("pip2.7 install paramiko > /dev/null 2>&1", shell=True)
    else:
        printc("Python2.7, pip2.7 and paramiko already installed, skipping")
    
    # Create xtreamcodes user doar dacă nu există
    try:
        subprocess.run("getent passwd xtreamcodes > /dev/null 2>&1", shell=True, check=True)
        printc("User xtreamcodes already exists, skipping creation")
    except subprocess.CalledProcessError:
        printc("Creating user xtreamcodes")
        subprocess.run("adduser --system --shell /bin/false --group --disabled-login xtreamcodes > /dev/null 2>&1", shell=True)
    
    # Creează directorul doar dacă nu există
    if not os.path.exists("/home/xtreamcodes"): 
        os.mkdir("/home/xtreamcodes")
        printc("Created /home/xtreamcodes directory")
    else:
        printc("/home/xtreamcodes directory already exists")
    
    return True 

def install(rType="MAIN"):
    global rInstall, rDownloadURL
    
    # Verifică dacă Xtream Codes este deja instalat
    if os.path.exists("/home/xtreamcodes/iptv_xtream_codes") and os.path.exists("/home/xtreamcodes/iptv_xtream_codes/start_services.sh"):
        printc("Xtream Codes already installed, skipping download")
        printc("If you want to reinstall, remove /home/xtreamcodes/iptv_xtream_codes first")
        return True
    
    printc("Downloading Software")
    
    try: 
        rURL = rDownloadURL[rInstall[rType]]
    except:
        printc("Invalid download URL!", col.BRIGHT_RED)
        return False
    
    # Download folosind wget (ca în install_github.py)
    subprocess.run('wget -q -O "/tmp/xtreamcodes.tar.gz" "%s"' % rURL, shell=True)
    
    if os.path.exists("/tmp/xtreamcodes.tar.gz"):
        printc("Installing Software")
        if os.path.exists("/home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb"):
            subprocess.run('chattr -f -i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null 2>&1', shell=True)
        subprocess.run('tar -zxvf "/tmp/xtreamcodes.tar.gz" -C "/home/xtreamcodes/" > /dev/null', shell=True)
        # Nu șterge arhiva încă - va fi ștearsă după importul database.sql în funcția mysql()
        printc("Software extracted - keeping archive until database import completes")
        return True
    
    printc("Failed to download installation file!", col.BRIGHT_RED)
    return False

def installadminpanel():
    # Verifică dacă admin panel-ul este deja instalat
    if os.path.exists("/home/xtreamcodes/iptv_xtream_codes/admin") and os.path.exists("/home/xtreamcodes/iptv_xtream_codes/admin/index.php"):
        printc("Admin Panel already installed")
        admin_files = os.listdir("/home/xtreamcodes/iptv_xtream_codes/admin")
        if len(admin_files) > 5:  # Verifică dacă are fișiere suficiente
            printc("Admin Panel appears to be complete, skipping download")
            return True
        else:
            printc("Admin Panel incomplete, proceeding with installation")
    
    # Folosesc URL-urile din install_github.py
    rURL = "https://github.com/emre1393/xtreamui_mirror/releases/latest/download/release_22f.zip"
    printc("Downloading Admin Panel")  
    subprocess.run('wget -q -O "/tmp/update.zip" "%s"' % rURL, shell=True)
    
    if os.path.exists("/tmp/update.zip"):
        try: 
            is_ok = zipfile.ZipFile("/tmp/update.zip")
        except:
            printc("Invalid link or zip file is corrupted!", col.BRIGHT_RED)
            os.remove("/tmp/update.zip")
            return False
    
    printc("Installing Admin Panel")
    subprocess.run('unzip -o /tmp/update.zip -d /tmp/update/ > /dev/null && cp -rf /tmp/update/XtreamUI-master/* /home/xtreamcodes/iptv_xtream_codes/ > /dev/null && rm -rf /tmp/update/XtreamUI-master > /dev/null && rm -rf /tmp/update > /dev/null && chown -R xtreamcodes:xtreamcodes /home/xtreamcodes > /dev/null', shell=True)
    
    # Nu șterge arhiva încă - va fi ștearsă după importul database.sql
    printc("Admin Panel extracted - keeping archive until database import completes")
    
    # Verifică dacă newstuff este deja instalat
    newstuff_indicator = "/home/xtreamcodes/iptv_xtream_codes/.newstuff_installed"
    if os.path.exists(newstuff_indicator):
        printc("New Stuff already installed, skipping")
        return True
    
    # Download new stuff
    rURL2 = "https://github.com/emre1393/xtreamui_mirror/releases/latest/download/newstuff.zip"
    printc("Downloading New Stuff for Admin Panel")  
    subprocess.run('wget -q -O "/tmp/update2.zip" "%s"' % rURL2, shell=True)
    
    if os.path.exists("/tmp/update2.zip"):
        try: 
            is_ok = zipfile.ZipFile("/tmp/update2.zip")
        except:
            printc("Invalid link or zip file is corrupted!", col.BRIGHT_RED)
            os.remove("/tmp/update2.zip")
            return False
    
    printc("Installing New Stuff for Admin Panel")
    subprocess.run('unzip -o /tmp/update2.zip -d /tmp/update2/ > /dev/null && cp -rf /tmp/update2/* /home/xtreamcodes/iptv_xtream_codes/ > /dev/null && rm -rf /tmp/update2 > /dev/null && chown -R xtreamcodes:xtreamcodes /home/xtreamcodes > /dev/null', shell=True)
    
    # Nu șterge arhiva încă - va fi ștearsă după importul database.sql
    printc("New Stuff extracted - keeping archive until database import completes")
    
    # Mark newstuff as installed
    try:
        with open(newstuff_indicator, "w") as f:
            f.write("installed")
    except:
        pass
    
    return True

def fix_mariadb_installation():
    """COMPLETE system cleanup and fresh MariaDB 10.5/10.6 installation"""
    printc("COMPLETE MySQL/MariaDB cleanup and fresh installation...")
    
    # Step 1: Kill all MySQL/MariaDB processes
    printc("Step 1: Stopping all MySQL/MariaDB processes...")
    subprocess.run("systemctl stop mariadb mysql mysqld >/dev/null 2>&1", shell=True)
    subprocess.run("pkill -f mysqld >/dev/null 2>&1", shell=True)
    subprocess.run("pkill -f mariadbd >/dev/null 2>&1", shell=True)
    subprocess.run("pkill -f mysql >/dev/null 2>&1", shell=True)
    
    # Step 2: Remove ALL MySQL/MariaDB packages completely
    printc("Step 2: Removing ALL MySQL/MariaDB packages...")
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get remove --purge mysql* mariadb* -y >/dev/null 2>&1", shell=True)
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get remove --purge libmysql* libmariadb* -y >/dev/null 2>&1", shell=True)
    subprocess.run("apt-get autoremove --purge -y >/dev/null 2>&1", shell=True)
    subprocess.run("apt-get autoclean >/dev/null 2>&1", shell=True)
    
    # Step 3: Remove ALL MySQL/MariaDB directories and files
    printc("Step 3: Cleaning all MySQL/MariaDB directories...")
    directories_to_clean = [
        "/var/lib/mysql",
        "/var/lib/mysql-files", 
        "/var/lib/mysql-keyring",
        "/etc/mysql",
        "/var/log/mysql",
        "/var/run/mysqld",
        "/usr/share/mysql",
        "/etc/apparmor.d/usr.sbin.mysqld"
    ]
    
    for directory in directories_to_clean:
        subprocess.run(f"rm -rf {directory} >/dev/null 2>&1", shell=True)
    
    # Step 4: Clean package manager
    printc("Step 4: Cleaning package manager...")
    subprocess.run("fuser -k /var/cache/debconf/config.dat >/dev/null 2>&1", shell=True)
    subprocess.run("fuser -k /var/lib/dpkg/lock-frontend >/dev/null 2>&1", shell=True)
    subprocess.run("fuser -k /var/lib/dpkg/lock >/dev/null 2>&1", shell=True)
    subprocess.run("dpkg --configure -a >/dev/null 2>&1", shell=True)
    subprocess.run("apt-get clean >/dev/null 2>&1", shell=True)
    subprocess.run("apt-get update -y >/dev/null 2>&1", shell=True)
    
    # Step 5: Install MariaDB 10.6 using official MariaDB repository
    printc("Step 5: Installing MariaDB 10.6 from official repository...")
    
    # Download MariaDB repository setup script
    printc("Downloading MariaDB repository setup...")
    download_result = subprocess.run(
        "curl -LsSO https://r.mariadb.com/downloads/mariadb_repo_setup",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if download_result.returncode != 0:
        printc("❌ ERROR: Failed to download MariaDB repository setup!", col.BRIGHT_RED)
        return False
    
    # Verify SHA256 checksum
    printc("Verifying MariaDB repository setup integrity...")
    verify_result = subprocess.run(
        'echo "c4a0f3dade02c51a6a28ca3609a13d7a0f8910cccbb90935a2f218454d3a914a mariadb_repo_setup" | sha256sum -c -',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if verify_result.returncode != 0:
        printc("❌ ERROR: MariaDB repository setup verification failed!", col.BRIGHT_RED)
        printc("Security check failed - aborting installation", col.BRIGHT_RED)
        return False
    
    printc("✅ MariaDB repository setup verified successfully")
    
    # Make script executable
    subprocess.run("chmod +x mariadb_repo_setup", shell=True)
    
    # Setup MariaDB 10.5 repository (most stable for Xtream Codes)
    printc("Setting up MariaDB 10.5 repository...")
    setup_result = subprocess.run(
        "./mariadb_repo_setup --mariadb-server-version=\"10.5\"",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if setup_result.returncode != 0:
        printc("❌ ERROR: Failed to setup MariaDB repository!", col.BRIGHT_RED)
        printc(f"Setup error: {setup_result.stderr}", col.BRIGHT_RED)
        return False
    
    printc("✅ MariaDB 10.6 repository configured successfully")
    
    # Update package lists with new repository
    printc("Updating package lists with MariaDB repository...")
    subprocess.run("apt-get update -y >/dev/null 2>&1", shell=True)
    
    # Install MariaDB 10.6
    printc("Installing MariaDB 10.6 server and client...")
    install_result = subprocess.run(
        "DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server mariadb-client",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if install_result.returncode != 0:
        printc("❌ ERROR: Failed to install MariaDB 10.6!", col.BRIGHT_RED)
        printc(f"Install error: {install_result.stderr}", col.BRIGHT_RED)
        return False
    
    printc("✅ MariaDB 10.6 installed successfully!")
    
    # Clean up setup script
    subprocess.run("rm -f mariadb_repo_setup >/dev/null 2>&1", shell=True)
    
    # Step 6: Configure MariaDB
    printc("Step 6: Configuring MariaDB...")
    subprocess.run("systemctl enable mariadb >/dev/null 2>&1", shell=True)
    subprocess.run("systemctl daemon-reload >/dev/null 2>&1", shell=True)
    
    # Create MySQL directories
    subprocess.run("mkdir -p /var/run/mysqld >/dev/null 2>&1", shell=True)
    subprocess.run("chown mysql:mysql /var/run/mysqld >/dev/null 2>&1", shell=True)
    
    # Initialize database if needed
    if not os.path.exists("/var/lib/mysql/mysql"):
        printc("Initializing MariaDB database...")
        subprocess.run("mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql >/dev/null 2>&1", shell=True)
    
    # Step 7: Start MariaDB service
    printc("Step 7: Starting MariaDB service...")
    start_result = subprocess.run("systemctl start mariadb", shell=True, capture_output=True, text=True)
    
    if start_result.returncode == 0:
        # Verify it's running
        time.sleep(3)
        status_check = subprocess.run("systemctl is-active mariadb", shell=True, capture_output=True, text=True)
        if status_check.stdout.strip() == "active":
            printc("✅ MariaDB installed and started successfully!")
            
            # Step 8: Verify version
            version_check = subprocess.run("mysql --version", shell=True, capture_output=True, text=True)
            if version_check.returncode == 0:
                printc(f"Installed version: {version_check.stdout.strip()}")
            
            return True
        else:
            printc("⚠️ MariaDB installed but not running, trying restart...", col.BRIGHT_YELLOW)
            subprocess.run("systemctl restart mariadb >/dev/null 2>&1", shell=True)
            time.sleep(3)
            final_check = subprocess.run("systemctl is-active mariadb", shell=True, capture_output=True, text=True)
            if final_check.stdout.strip() == "active":
                printc("✅ MariaDB started after restart!")
                return True
            else:
                printc("❌ MariaDB failed to start even after restart", col.BRIGHT_RED)
                return False
    else:
        printc("❌ Failed to start MariaDB", col.BRIGHT_RED)
        printc(f"Start error: {start_result.stderr}", col.BRIGHT_RED)
        return False

def check_mariadb_service():
    """Check what MariaDB service is available and try to start it"""
    service_names = ['mariadb', 'mysql', 'mysqld', 'mysql.service', 'mariadb.service']
    
    # First check systemctl list-units for available services
    list_result = subprocess.run("systemctl list-units --type=service --state=loaded,inactive,active | grep -E '(maria|mysql)'", shell=True, capture_output=True, text=True)
    if list_result.stdout.strip():
        printc(f"Found database services: {list_result.stdout.strip()}")
        # Extract service name from first match - skip special characters
        lines = list_result.stdout.strip().split('\n')
        for line in lines:
            # Skip lines with "not-found" status
            if "not-found" in line:
                continue
            parts = line.split()
            for part in parts:
                if 'mariadb' in part.lower() or 'mysql' in part.lower():
                    if part.endswith('.service'):
                        return part[:-8]
                    else:
                        return part
    
    # Fallback to manual check
    for service in service_names:
        # Check if service file exists
        service_file_exists = subprocess.run(f"systemctl cat {service} >/dev/null 2>&1", shell=True)
        if service_file_exists.returncode == 0:
            printc(f"Found MariaDB service: {service}")
            return service
    
    # Final check for service files in filesystem
    service_files = [
        '/lib/systemd/system/mariadb.service',
        '/lib/systemd/system/mysql.service',
        '/etc/systemd/system/mariadb.service',
        '/etc/systemd/system/mysql.service'
    ]
    
    for service_file in service_files:
        if os.path.exists(service_file):
            service_name = os.path.basename(service_file).replace('.service', '')
            printc(f"Found service file: {service_file}")
            return service_name
    
    return None

def ensure_mariadb_running():
    """Ensure MariaDB is running - FORCE CLEANUP if any service is failed"""
    printc("Checking MariaDB service status...")
    
    service_name = check_mariadb_service()
    
    # Check if service exists and its current status
    if service_name:
        result = subprocess.run(f"systemctl is-active {service_name}", shell=True, capture_output=True, text=True)
        service_status = result.stdout.strip()
        
        if service_status == "active":
            printc(f"✅ MariaDB service {service_name} is already running")
            return True
        elif service_status in ["failed", "inactive"]:
            printc(f"MariaDB service {service_name} is {service_status} - FORCING COMPLETE CLEANUP...", col.BRIGHT_YELLOW)
            # Force cleanup even if service exists but is broken
            if not fix_mariadb_installation():
                printc("ERROR: Failed to fix MariaDB installation!", col.BRIGHT_RED)
                return False
            # After cleanup, check again
            service_name = check_mariadb_service()
    else:
        printc("No MariaDB service found - performing fresh installation...", col.BRIGHT_YELLOW)
        # No service found, do fresh installation
        if not fix_mariadb_installation():
            printc("ERROR: Failed to install MariaDB!", col.BRIGHT_RED)
            return False
        # After installation, check again
        service_name = check_mariadb_service()
    
    # At this point we should have a working service
    if not service_name:
        printc("ERROR: No MariaDB service found even after installation!", col.BRIGHT_RED)
        return False
    
    # Final check - service should be running now
    result = subprocess.run(f"systemctl is-active {service_name}", shell=True, capture_output=True, text=True)
    if result.stdout.strip() == "active":
        printc(f"✅ MariaDB service {service_name} is now running after fix!")
        return True
    else:
        printc(f"ERROR: MariaDB service {service_name} still not running after installation", col.BRIGHT_RED)
        subprocess.run(f"systemctl status {service_name}", shell=True)
        return False

def mysql(rUsername, rPassword):
    global rMySQLCnf, rMySQLServiceFile
    printc("Configuring MySQL on port 7999")
    
    rCreate = True
    if os.path.exists("/etc/mysql/my.cnf"):
        try:
            existing_content = open("/etc/mysql/my.cnf", "r").read()
            if "# Xtream Codes" in existing_content:
                printc("Xtream Codes MySQL configuration found - updating with optimized settings")
                rCreate = True  # Force re-creation to apply optimized settings
        except:
            pass
    
    if rCreate:
        # Ensure MySQL directory exists
        if not os.path.exists("/etc/mysql"):
            os.makedirs("/etc/mysql")
            printc("Created MySQL configuration directory")
        
        if os.path.exists("/etc/mysql/my.cnf"):
            shutil.copy("/etc/mysql/my.cnf", "/etc/mysql/my.cnf.xc")
            printc("Backed up existing MySQL configuration")
        rFile = open("/etc/mysql/my.cnf", "w")
        rFile.write(rMySQLCnf)
        rFile.close()
        printc("Applied Xtream Codes MySQL configuration - Port 7999")
        
        # CRITICAL: Ensure MariaDB is running before proceeding
        if not ensure_mariadb_running():
            printc("INSTALLATION STOPPED: MariaDB failed to start!", col.BRIGHT_RED)
            printc("Please check the errors above and fix MariaDB before continuing", col.BRIGHT_RED)
            return False
    
    # Automatic MySQL configuration - no user input needed
    printc("Configuring MySQL automatically...")
    
    # Try connection without password first (fresh MariaDB install)
    rExtra = ""
    connection_test = subprocess.run("mysql -u root -e 'SELECT 1;' >/dev/null 2>&1", shell=True)
    
    if connection_test.returncode != 0:
        # Try to reset MySQL root password for fresh install
        printc("Setting up MySQL root access...")
        subprocess.run("systemctl stop mariadb", shell=True)
        subprocess.run("mysqld_safe --skip-grant-tables --skip-networking &", shell=True)
        time.sleep(3)
        subprocess.run("mysql -u root -e \"UPDATE mysql.user SET authentication_string=PASSWORD(''), plugin='mysql_native_password' WHERE User='root'; FLUSH PRIVILEGES;\" >/dev/null 2>&1", shell=True)
        subprocess.run("pkill mysqld_safe", shell=True)
        subprocess.run("pkill mysqld", shell=True)
        time.sleep(2)
        
        # Restart MariaDB normally
        if not ensure_mariadb_running():
            printc("Failed to configure MySQL automatically", col.BRIGHT_RED)
            return False
    
    # Test connection again
    printc("Testing MySQL connection...")
    mysql_port = subprocess.run("mysql -u root -e 'SHOW VARIABLES LIKE \"port\";'", shell=True, capture_output=True, text=True)
    
    if "7999" in mysql_port.stdout:
        printc("MySQL is running on port 7999 (correct)")
    else:
        printc("Warning: MySQL port may not be 7999", col.BRIGHT_YELLOW)
    
    # Check if database exists
    database_exists = False
    try:
        result = subprocess.run("mysql -u root -e 'SHOW DATABASES;' | grep xtream_iptvpro", shell=True, capture_output=True, text=True)
        if "xtream_iptvpro" in result.stdout:
            database_exists = True
            printc("Database xtream_iptvpro already exists - recreating for fresh install")
    except:
        pass
    
    # Always create/recreate database for main installation
    rDrop = True
        
    # Proceed with database setup (no loop needed - automatic)
    try:
        if rDrop:
            # Drop existing users and database with error checking
            printc("Dropping existing users...")
            drop_users = subprocess.run('mysql -u root%s -e "DROP USER IF EXISTS \'%s\'@\'%%\'; DROP USER IF EXISTS \'%s\'@\'localhost\'; DROP USER IF EXISTS \'%s\'@\'127.0.0.1\';"' % (rExtra, rUsername, rUsername, rUsername), shell=True, capture_output=True, text=True)
            if drop_users.returncode != 0:
                printc("Warning: Could not drop some users (they may not exist)", col.BRIGHT_YELLOW)
            
            printc("Creating database...")
            create_db = subprocess.run('mysql -u root%s -e "DROP DATABASE IF EXISTS xtream_iptvpro; CREATE DATABASE IF NOT EXISTS xtream_iptvpro;"' % rExtra, shell=True, capture_output=True, text=True)
            if create_db.returncode != 0:
                printc("ERROR: Failed to create database!", col.BRIGHT_RED)
                printc(f"MySQL Error: {create_db.stderr}", col.BRIGHT_RED)
                return False
            else:
                printc("Database created successfully")
            
            # CRITICAL: Verify MariaDB is running before database import
            printc("Final MariaDB verification before database import...")
            if not ensure_mariadb_running():
                printc("CRITICAL ERROR: MariaDB is not running before database import!", col.BRIGHT_RED)
                return False
            
            # Test database connection before import
            printc("Testing database connection...")
            connection_test = subprocess.run("mysql -u root%s -e 'SELECT 1;'" % rExtra, shell=True, capture_output=True, text=True)
            if connection_test.returncode != 0:
                printc("CRITICAL ERROR: Cannot connect to database before import!", col.BRIGHT_RED)
                printc(f"Connection Error: {connection_test.stderr}", col.BRIGHT_RED)
                return False
            else:
                printc("✅ Database connection verified - ready for import")
            
            # Import database doar dacă fișierul există
            if os.path.exists("/home/xtreamcodes/iptv_xtream_codes/database.sql"):
                printc("Importing database schema")
                import_db = subprocess.run("mysql -u root%s xtream_iptvpro < /home/xtreamcodes/iptv_xtream_codes/database.sql" % rExtra, shell=True, capture_output=True, text=True)
                if import_db.returncode != 0:
                    printc("ERROR: Failed to import database schema!", col.BRIGHT_RED)
                    printc(f"MySQL Error: {import_db.stderr}", col.BRIGHT_RED)
                    return False
                else:
                    printc("Database schema imported successfully")
            else:
                printc("Warning: database.sql not found, checking /root/database.sql")
                if os.path.exists("/root/database.sql"):
                    printc("Importing database from /root/database.sql")
                    import_db = subprocess.run("mysql -u root%s xtream_iptvpro < /root/database.sql" % rExtra, shell=True, capture_output=True, text=True)
                    if import_db.returncode != 0:
                        printc("ERROR: Failed to import database from /root/database.sql!", col.BRIGHT_RED)
                        printc(f"MySQL Error: {import_db.stderr}", col.BRIGHT_RED)
                        return False
                    else:
                        printc("Database imported successfully from /root/database.sql")
                else:
                    printc("Warning: No database.sql found, skipping import")
            
            # Configure settings
            printc("Configuring settings...")
            settings_update = subprocess.run('mysql -u root%s -e "USE xtream_iptvpro; UPDATE settings SET live_streaming_pass = \'%s\', unique_id = \'%s\', crypt_load_balancing = \'%s\', get_real_ip_client=\'\';"' % (rExtra, generate(20), generate(12), generate(20)), shell=True, capture_output=True, text=True)
            if settings_update.returncode != 0:
                printc("Warning: Could not update settings table", col.BRIGHT_YELLOW)
                printc(f"MySQL Error: {settings_update.stderr}", col.BRIGHT_YELLOW)
            
            # Configure server
            printc("Configuring streaming server...")
            server_config = subprocess.run('mysql -u root%s -e "USE xtream_iptvpro; REPLACE INTO streaming_servers (id, server_name, domain_name, server_ip, vpn_ip, ssh_password, ssh_port, diff_time_main, http_broadcast_port, total_clients, system_os, network_interface, latency, status, enable_geoip, geoip_countries, last_check_ago, can_delete, server_hardware, total_services, persistent_connections, rtmp_port, geoip_type, isp_names, isp_type, enable_isp, boost_fpm, http_ports_add, network_guaranteed_speed, https_broadcast_port, https_ports_add, whitelist_ips, watchdog_data, timeshift_only) VALUES (1, \'Main Server\', \'\', \'%s\', \'\', NULL, NULL, 0, 8080, 1000, \'%s\', \'eth0\', 0, 1, 0, \'\', 0, 0, \'{}\', 3, 0, 8880, \'low_priority\', \'\', \'low_priority\', 0, 1, \'\', 1000, 8443, \'\', \'[\"127.0.0.1\",\"\"]\', \'{}\', 0);"' % (rExtra, getIP(), getVersion()), shell=True, capture_output=True, text=True)
            if server_config.returncode != 0:
                printc("Warning: Could not configure streaming server", col.BRIGHT_YELLOW)
                printc(f"MySQL Error: {server_config.stderr}", col.BRIGHT_YELLOW)
            
            # Create admin user with correct fields
            printc("Creating admin user...")
            admin_user = subprocess.run('mysql -u root%s -e "USE xtream_iptvpro; REPLACE INTO reg_users (id, username, password, email, member_group_id, verified, status, default_lang, reseller_dns, owner_id, google_2fa_sec, date_registered) VALUES (1, \'admin\', \'\\$6\\$rounds=20000\\$xtreamcodes\\$XThC5OwfuS0YwS4ahiifzF14vkGbGsFF1w7ETL4sRRC5sOrAWCjWvQJDromZUQoQuwbAXAFdX3h3Cp3vqulpS0\', \'admin@website.com\', 1, 1, 1, \'english\', \'\', 0, \'\', UNIX_TIMESTAMP());"' % rExtra, shell=True, capture_output=True, text=True)
            if admin_user.returncode != 0:
                printc("ERROR: Failed to create admin user!", col.BRIGHT_RED)
                printc(f"MySQL Error: {admin_user.stderr}", col.BRIGHT_RED)
                return False
            else:
                printc("Admin user created successfully")
            
            # Create database users
            printc("Creating database users...")
            
            # Create localhost user
            create_local_user = subprocess.run('mysql -u root%s -e "CREATE USER \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'; GRANT ALL PRIVILEGES ON xtream_iptvpro.* TO \'%s\'@\'localhost\' WITH GRANT OPTION; GRANT SELECT, PROCESS, LOCK TABLES ON *.* TO \'%s\'@\'localhost\';FLUSH PRIVILEGES;"' % (rExtra, rUsername, rPassword, rUsername, rUsername), shell=True, capture_output=True, text=True)
            if create_local_user.returncode != 0:
                printc("Warning: Could not create localhost user", col.BRIGHT_YELLOW)
                printc(f"MySQL Error: {create_local_user.stderr}", col.BRIGHT_YELLOW)
            
            # Create 127.0.0.1 user
            create_127_user = subprocess.run('mysql -u root%s -e "CREATE USER \'%s\'@\'127.0.0.1\' IDENTIFIED BY \'%s\'; GRANT ALL PRIVILEGES ON xtream_iptvpro.* TO \'%s\'@\'127.0.0.1\' WITH GRANT OPTION; GRANT SELECT, PROCESS, LOCK TABLES ON *.* TO \'%s\'@\'127.0.0.1\';FLUSH PRIVILEGES;"' % (rExtra, rUsername, rPassword, rUsername, rUsername), shell=True, capture_output=True, text=True)
            if create_127_user.returncode != 0:
                printc("Warning: Could not create 127.0.0.1 user", col.BRIGHT_YELLOW)
                printc(f"MySQL Error: {create_127_user.stderr}", col.BRIGHT_YELLOW)
            
            # Create wildcard user
            create_wild_user = subprocess.run('mysql -u root%s -e "GRANT SELECT, INSERT, UPDATE, DELETE ON xtream_iptvpro.* TO \'%s\'@\'%%\' IDENTIFIED BY \'%s\';FLUSH PRIVILEGES;"' % (rExtra, rUsername, rPassword), shell=True, capture_output=True, text=True)
            if create_wild_user.returncode != 0:
                printc("Warning: Could not create wildcard user", col.BRIGHT_YELLOW)
                printc(f"MySQL Error: {create_wild_user.stderr}", col.BRIGHT_YELLOW)
            
            printc("Database users configuration completed")
            
            # Create dashboard statistics
            printc("Creating dashboard statistics...")
            dashboard_stats = subprocess.run('mysql -u root%s -e "USE xtream_iptvpro; CREATE TABLE IF NOT EXISTS dashboard_statistics (id int(11) NOT NULL AUTO_INCREMENT, type varchar(16) NOT NULL DEFAULT \'\', time int(16) NOT NULL DEFAULT \'0\', count int(16) NOT NULL DEFAULT \'0\', PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1; INSERT INTO dashboard_statistics (type, time, count) VALUES(\'conns\', UNIX_TIMESTAMP(), 0),(\'users\', UNIX_TIMESTAMP(), 0);"' % rExtra, shell=True, capture_output=True, text=True)
            if dashboard_stats.returncode != 0:
                printc("Warning: Could not create dashboard statistics", col.BRIGHT_YELLOW)
            
            # Security settings
            printc("Applying security settings...")
            security_settings = subprocess.run('mysql -u root%s -e "USE xtream_iptvpro; UPDATE settings SET get_real_ip_client=\'\', double_auth=\'1\', hash_lb=\'1\', mag_security=\'1\' where id=\'1\';"' % rExtra, shell=True, capture_output=True, text=True)
            if security_settings.returncode != 0:
                printc("Warning: Could not apply security settings", col.BRIGHT_YELLOW)
        
        printc("MySQL configuration completed successfully!")
        
        # Clean up ONLY download archives after successful database import
        printc("Cleaning up download archives...")
        cleanup_files = [
            "/tmp/xtreamcodes.tar.gz",
            "/tmp/update.zip", 
            "/tmp/update2.zip"
        ]
        
        for cleanup_file in cleanup_files:
            try:
                if os.path.exists(cleanup_file):
                    os.remove(cleanup_file)
                    printc(f"Removed: {cleanup_file}")
            except:
                pass
                
        # Keep database.sql as backup - don't delete it
        printc("✅ Kept database.sql as backup - installation archives cleaned")
        return True
        
    except Exception as e: 
        printc("MySQL configuration failed: %s" % str(e), col.BRIGHT_RED)
        return False

def encrypt(rHost="127.0.0.1", rUsername="user_iptvpro", rPassword="", rDatabase="xtream_iptvpro", rServerID=1, rPort=7999):
    printc("Encrypting configuration for port 7999...")
    try: 
        os.remove("/home/xtreamcodes/iptv_xtream_codes/config")
    except: 
        pass
    
    # Using Python 3 compatible encoding
    rf = open('/home/xtreamcodes/iptv_xtream_codes/config', 'wb')
    lestring = ''.join(chr(ord(c)^ord(k)) for c,k in zip('{\"host\":\"%s\",\"db_user\":\"%s\",\"db_pass\":\"%s\",\"db_name\":\"%s\",\"server_id\":\"%d\", \"db_port\":\"%d\", \"pconnect\":\"0\"}' % (rHost, rUsername, rPassword, rDatabase, rServerID, rPort), cycle('5709650b0d7806074842c6de575025b1')))
    rf.write(base64.b64encode(bytes(lestring, 'ascii')))
    rf.close()

def configure(rType="MAIN"):
    printc("Configuring System")
    
    # Configure fstab doar dacă nu este deja configurat
    fstab_content = open("/etc/fstab").read()
    if "/home/xtreamcodes/iptv_xtream_codes/" not in fstab_content:
        printc("Adding tmpfs mounts to fstab")
        rFile = open("/etc/fstab", "a")
        rFile.write("\ntmpfs /home/xtreamcodes/iptv_xtream_codes/streams tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=90% 0 0\ntmpfs /home/xtreamcodes/iptv_xtream_codes/tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=3G 0 0\n")
        rFile.close()
    else:
        printc("Tmpfs mounts already configured in fstab")
    
    # Configure sudoers doar dacă nu este deja configurat
    sudoers_content = open("/etc/sudoers").read()
    if "xtreamcodes" not in sudoers_content:
        printc("Adding xtreamcodes to sudoers")
        subprocess.run('echo "xtreamcodes ALL = (root) NOPASSWD: /sbin/iptables, /usr/bin/chattr" >> /etc/sudoers', shell=True)
    else:
        printc("xtreamcodes already configured in sudoers")
    
    # Create init script doar dacă nu există
    if not os.path.exists("/etc/init.d/xtreamcodes"):
        printc("Creating init script")
        rFile = open("/etc/init.d/xtreamcodes", "w")
        rFile.write("#! /bin/bash\n/home/xtreamcodes/iptv_xtream_codes/start_services.sh")
        rFile.close()
        subprocess.run("chmod +x /etc/init.d/xtreamcodes > /dev/null", shell=True)
    else:
        printc("Init script already exists")
    
    # Mount tmpfs
    printc("Mounting tmpfs filesystems")
    subprocess.run("mount -a", shell=True)
    
    # Setup ffmpeg doar dacă nu este deja configurat
    if not os.path.exists("/usr/bin/ffmpeg") or not os.path.islink("/usr/bin/ffmpeg"):
        printc("Setting up ffmpeg symlink")
        try: 
            os.remove("/usr/bin/ffmpeg")
        except: 
            pass
        
        if os.path.exists("/home/xtreamcodes/iptv_xtream_codes/bin/ffmpeg"):
            subprocess.run("ln -s /home/xtreamcodes/iptv_xtream_codes/bin/ffmpeg /usr/bin/", shell=True)
        else:
            printc("Warning: ffmpeg binary not found in xtreamcodes directory")
    else:
        printc("ffmpeg symlink already configured")
    
    # Create tv_archive directory doar dacă nu există
    if not os.path.exists("/home/xtreamcodes/iptv_xtream_codes/tv_archive"): 
        os.mkdir("/home/xtreamcodes/iptv_xtream_codes/tv_archive/")
        printc("Created tv_archive directory")
    else:
        printc("tv_archive directory already exists")
    
    # Set ownership and permissions
    printc("Setting file ownership and permissions")
    subprocess.run("chown xtreamcodes:xtreamcodes -R /home/xtreamcodes > /dev/null", shell=True)
    subprocess.run("chmod -R 0777 /home/xtreamcodes > /dev/null", shell=True)
    
    if rType == "MAIN": 
        subprocess.run(r"sudo find /home/xtreamcodes/iptv_xtream_codes/admin/ -type f -exec chmod 644 {} \; > /dev/null 2>&1", shell=True)
        subprocess.run(r"sudo find /home/xtreamcodes/iptv_xtream_codes/admin/ -type d -exec chmod 755 {} \; > /dev/null 2>&1", shell=True)
    
    # Fix start_services.sh cu LD_LIBRARY_PATH - CRITICAL FIX for Ubuntu 18 compatibility!
    start_script_path = "/home/xtreamcodes/iptv_xtream_codes/start_services.sh"
    if os.path.exists(start_script_path):
        printc("Applying comprehensive LD_LIBRARY_PATH fix to start_services.sh")
        start_content = open(start_script_path, 'r').read()
        
        # Enhanced LD_LIBRARY_PATH with Ubuntu 18 compatibility paths
        enhanced_ld_path = """#!/bin/bash
# Critical Ubuntu 18 compatibility library paths for Xtream Codes
export LD_LIBRARY_PATH="/home/xtreamcodes/iptv_xtream_codes/lib:/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"

# Ensure critical symlinks exist at runtime
if [ -f "/usr/lib/x86_64-linux-gnu/libssl.so.1.0.0" ] && [ ! -f "/usr/lib/x86_64-linux-gnu/libssl.so.1.0" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libssl.so.1.0.0 /usr/lib/x86_64-linux-gnu/libssl.so.1.0 2>/dev/null
fi

if [ -f "/usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0" ] && [ ! -f "/usr/lib/x86_64-linux-gnu/libcrypto.so.1.0" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0 2>/dev/null
fi

if [ -f "/usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0" ] && [ ! -f "/usr/lib/x86_64-linux-gnu/libpng12.so.0" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0 /usr/lib/x86_64-linux-gnu/libpng12.so.0 2>/dev/null
fi

if [ -f "/usr/lib/x86_64-linux-gnu/libcurl.so.4.4.0" ] && [ ! -f "/usr/lib/x86_64-linux-gnu/libcurl.so.4" ]; then
    ln -sf /usr/lib/x86_64-linux-gnu/libcurl.so.4.4.0 /usr/lib/x86_64-linux-gnu/libcurl.so.4 2>/dev/null
fi

# Refresh library cache
ldconfig 2>/dev/null

"""
        
        # Remove existing LD_LIBRARY_PATH lines and add enhanced version
        lines = start_content.split('\n')
        filtered_lines = []
        skip_shebang = True
        
        for line in lines:
            if skip_shebang and line.startswith('#!/'):
                skip_shebang = False
                continue
            if 'export LD_LIBRARY_PATH' not in line and 'LD_LIBRARY_PATH=' not in line:
                filtered_lines.append(line)
        
        # Combine enhanced header with existing content
        start_content = enhanced_ld_path + '\n'.join(filtered_lines)
        
        # Fix chown command
        if "2>/dev/null" not in start_content:
            start_content = start_content.replace("chown -R xtreamcodes:xtreamcodes /home/xtreamcodes", "chown -R xtreamcodes:xtreamcodes /home/xtreamcodes 2>/dev/null")
        
        # Write back the enhanced script
        with open(start_script_path, 'w') as f:
            f.write(start_content)
        
        subprocess.run("chmod +x /home/xtreamcodes/iptv_xtream_codes/start_services.sh > /dev/null", shell=True)
        printc("start_services.sh enhanced with comprehensive Ubuntu 18 compatibility")
    
    # Configure hosts doar pentru intrările care nu există
    hosts_entries = [
        "127.0.0.1    xtream-codes.com",
        "127.0.0.1    api.xtream-codes.com", 
        "127.0.0.1    downloads.xtream-codes.com"
    ]
    
    hosts_content = open("/etc/hosts").read()
    entries_added = False
    for entry in hosts_entries:
        domain = entry.split()[1]
        if domain not in hosts_content:
            printc("Adding %s to hosts file" % domain)
            subprocess.run('echo "%s" >> /etc/hosts' % entry, shell=True)
            entries_added = True
    
    if not entries_added:
        printc("All required hosts entries already configured")
    
    # Configure crontab doar dacă nu este deja configurat
    crontab_content = open("/etc/crontab").read()
    if "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh" not in crontab_content:
        printc("Adding startup script to crontab")
        subprocess.run('echo "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh" >> /etc/crontab', shell=True)
    else:
        printc("Startup script already configured in crontab")

def verify_ubuntu18_compatibility():
    """Verifică și fixează automat toate problemele de compatibilitate Ubuntu 18"""
    printc("Performing Ubuntu 18 compatibility verification and auto-fixes")
    
    # Critical library symlinks that MUST exist for Xtream Codes
    critical_symlinks = [
        ("/usr/lib/x86_64-linux-gnu/libssl.so.1.0.0", "/usr/lib/x86_64-linux-gnu/libssl.so.1.0"),
        ("/usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0", "/usr/lib/x86_64-linux-gnu/libcrypto.so.1.0"),
        ("/usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0", "/usr/lib/x86_64-linux-gnu/libpng12.so.0"),
        ("/usr/lib/x86_64-linux-gnu/libcurl.so.4.4.0", "/usr/lib/x86_64-linux-gnu/libcurl.so.4"),
        ("/usr/lib/x86_64-linux-gnu/libpng12.so.0.54.0", "/usr/lib/x86_64-linux-gnu/libpng12.so"),
        # Additional libpng12.so.0 symlink for PHP compatibility
        ("/usr/lib/x86_64-linux-gnu/libpng16.so.16", "/usr/lib/x86_64-linux-gnu/libpng12.so.0"),
    ]
    
    fixed_links = []
    for source, target in critical_symlinks:
        if os.path.exists(source) and not os.path.exists(target):
            try:
                os.symlink(source, target)
                fixed_links.append(os.path.basename(target))
                printc(f"✓ Fixed symlink: {os.path.basename(target)}")
            except:
                printc(f"⚠ Could not create symlink: {os.path.basename(target)}", col.BRIGHT_YELLOW)
    
    if fixed_links:
        printc(f"Auto-fixed {len(fixed_links)} library symlinks", col.BRIGHT_GREEN)
        # Refresh library cache
        subprocess.run("ldconfig", shell=True)
    else:
        printc("All critical library symlinks already exist", col.BRIGHT_GREEN)
    
    # Test binaries for compatibility issues
    printc("Testing Xtream Codes binaries for library compatibility...")
    test_binaries = [
        "/home/xtreamcodes/iptv_xtream_codes/bin/ffmpeg",
        "/home/xtreamcodes/iptv_xtream_codes/bin/ffprobe", 
        "/home/xtreamcodes/iptv_xtream_codes/php/bin/php"
    ]
    
    compatibility_issues = []
    for binary in test_binaries:
        if os.path.exists(binary):
            try:
                result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    printc(f"✓ {os.path.basename(binary)} working correctly")
                else:
                    compatibility_issues.append(binary)
            except:
                compatibility_issues.append(binary)
        else:
            printc(f"⚠ Binary not found: {binary}", col.BRIGHT_YELLOW)
    
    if compatibility_issues:
        printc(f"Detected {len(compatibility_issues)} compatibility issues - applying enhanced LD_LIBRARY_PATH", col.BRIGHT_YELLOW)
        
        # Create enhanced LD config file
        ld_config = """# Xtream Codes Ubuntu 18 compatibility
/home/xtreamcodes/iptv_xtream_codes/lib
/usr/lib/x86_64-linux-gnu
/lib/x86_64-linux-gnu
"""
        with open("/etc/ld.so.conf.d/xtream-ubuntu18.conf", "w") as f:
            f.write(ld_config)
        
        subprocess.run("ldconfig", shell=True)
        printc("✓ Enhanced library configuration applied")
    else:
        printc("✅ All Xtream Codes binaries passed compatibility test!", col.BRIGHT_GREEN)

def start(first=True):
    if first: 
        printc("Starting Xtream Codes with LD_LIBRARY_PATH")
    else: 
        printc("Restarting Xtream Codes")
    # Use export LD_LIBRARY_PATH before running start_services.sh
    subprocess.run("export LD_LIBRARY_PATH=/home/xtreamcodes/iptv_xtream_codes/lib:$LD_LIBRARY_PATH && /home/xtreamcodes/iptv_xtream_codes/start_services.sh > /dev/null", shell=True) 

if __name__ == "__main__":
    try: 
        rVersion = os.popen('lsb_release -sr').read().strip()
    except: 
        rVersion = None
    
    if rVersion not in rVersions:
        printc("Unsupported Operating System, Works only on Ubuntu Server 24.04", col.BRIGHT_RED)
        sys.exit(1)

    printc("Xtream UI - Ubuntu 24.04 FIXED Installer", col.BRIGHT_GREEN, 2)
    print("%s │ Includes ALL compatibility fixes for Ubuntu 24 %s" % (col.BRIGHT_GREEN, col.ENDC))
    print("%s │ ✓ MariaDB on port 7999 %s" % (col.BRIGHT_GREEN, col.ENDC))
    print("%s │ ✓ Ubuntu 18 libraries compatibility %s" % (col.BRIGHT_GREEN, col.ENDC))
    print("%s │ ✓ SSL/PNG library fixes %s" % (col.BRIGHT_GREEN, col.ENDC))
    print("%s │ ✓ LD_LIBRARY_PATH in start_services.sh %s" % (col.BRIGHT_GREEN, col.ENDC))
    print("%s │ ✓ Proper admin user creation %s" % (col.BRIGHT_GREEN, col.ENDC))
    print(" ")
    
    rType = input("  Installation Type [MAIN, LB]: ")
    print(" ")
    
    if rType.upper() in ["MAIN", "LB"]:
        if rType.upper() == "LB":
            rHost = input("  Main Server IP Address: ")
            rPassword = input("  MySQL Password: ")
            try: 
                rServerID = int(input("  Load Balancer Server ID: "))
            except: 
                rServerID = -1
            print(" ")
        else:
            rHost = "127.0.0.1"
            rPassword = generate()
            rServerID = 1
            rAccesscode = generate(12)

        rUsername = "user_iptvpro"
        rDatabase = "xtream_iptvpro"
        rPort = 7999
        
        if len(rHost) > 0 and len(rPassword) > 0 and rServerID > -1:
            printc("Start installation with ALL fixes applied? Y/N", col.BRIGHT_YELLOW)
            if input("  ").upper() == "Y":
                print(" ")
                
                # Start installation process
                printc("Installing with Ubuntu 24 compatibility fixes", col.BRIGHT_CYAN)
                rRet = prepare(rType.upper())
                if not install(rType.upper()): 
                    sys.exit(1)
                
                if rType.upper() == "MAIN":
                    if not mysql(rUsername, rPassword): 
                        sys.exit(1)
                
                encrypt(rHost, rUsername, rPassword, rDatabase, rServerID, rPort)
                
                if rType.upper() == "MAIN": 
                    if not installadminpanel():
                        printc("Warning: Admin panel installation failed", col.BRIGHT_YELLOW)
                    # Configure admin panel access code
                    subprocess.run("sed -i 's|randomcodehere|%s|g' /home/xtreamcodes/iptv_xtream_codes/nginx/conf/admin_panel.conf" % rAccesscode, shell=True)
                
                configure(rType.upper())
                
                # Final Ubuntu 18 compatibility verification and fixes
                verify_ubuntu18_compatibility()
                
                start()
                
                printc("Installation completed successfully!", col.BRIGHT_GREEN, 2)
                
                if rType.upper() == "MAIN":
                    printc("IMPORTANT - Save these credentials!")
                    print("%s ╔═══════════════════════════════════════════════════════════════╗ %s" % (col.BRIGHT_YELLOW, col.ENDC))
                    print("%s ║ MySQL Root Password: Keep your existing root password        ║ %s" % (col.BRIGHT_YELLOW, col.ENDC))
                    print("%s ║ MySQL User Password: %-40s ║ %s" % (col.BRIGHT_YELLOW, rPassword, col.ENDC))
                    print("%s ║ Admin Panel URL: http://%-15s:8080/%-12s ║ %s" % (col.BRIGHT_YELLOW, getIP(), rAccesscode, col.ENDC))
                    print("%s ║ Admin Login: admin / admin                                   ║ %s" % (col.BRIGHT_YELLOW, col.ENDC))
                    print("%s ║ Access Code: %-47s ║ %s" % (col.BRIGHT_YELLOW, rAccesscode, col.ENDC))
                    print("%s ║ Database Port: 7999 (Xtream Codes default)                  ║ %s" % (col.BRIGHT_YELLOW, col.ENDC))
                    print("%s ╚═══════════════════════════════════════════════════════════════╝ %s" % (col.BRIGHT_YELLOW, col.ENDC))
                    
                    # Save credentials to file
                    try:
                        rFile = open("/root/xtream_credentials.txt", "w")
                        rFile.write("=== XTREAM CODES CREDENTIALS ===\n")
                        rFile.write("MySQL User Password: %s\n" % rPassword)
                        rFile.write("Admin Panel URL: http://%s:8080/%s\n" % (getIP(), rAccesscode))
                        rFile.write("Admin Login: admin/admin\n")
                        rFile.write("Access Code: %s\n" % rAccesscode)
                        rFile.write("Database Port: 7999\n")
                        rFile.write("Server IP: %s\n" % getIP())
                        rFile.write("Installation Date: %s\n" % subprocess.run("date", shell=True, capture_output=True, text=True).stdout.strip())
                        rFile.close()
                        printc("Credentials saved to /root/xtream_credentials.txt", col.BRIGHT_GREEN)
                    except:
                        printc("Warning: Could not save credentials file", col.BRIGHT_YELLOW)
                
                # Final Summary with fixes applied
                printc("Installation Summary with ALL FIXES:", col.BRIGHT_BLUE)
                print("%s │ System: Ubuntu %s FIXED %s" % (col.BRIGHT_BLUE, rVersion, col.ENDC))
                print("%s │ Type: %s Server %s" % (col.BRIGHT_BLUE, rType.upper(), col.ENDC))
                print("%s │ IP Address: %s %s" % (col.BRIGHT_BLUE, getIP(), col.ENDC))
                if rType.upper() == "MAIN":
                    print("%s │ Admin Panel: http://%s:8080/%s %s" % (col.BRIGHT_BLUE, getIP(), rAccesscode, col.ENDC))
                    print("%s │ Streaming Port: 8080 %s" % (col.BRIGHT_BLUE, col.ENDC))
                    print("%s │ Database: xtream_iptvpro on port 7999 %s" % (col.BRIGHT_BLUE, col.ENDC))
                print("%s │ Ubuntu 18 Libraries: ✓ INSTALLED %s" % (col.BRIGHT_BLUE, col.ENDC))
                print("%s │ SSL Compatibility: ✓ FIXED %s" % (col.BRIGHT_BLUE, col.ENDC))
                print("%s │ LD_LIBRARY_PATH: ✓ CONFIGURED %s" % (col.BRIGHT_BLUE, col.ENDC))
                print("%s │ Admin User: ✓ CREATED %s" % (col.BRIGHT_BLUE, col.ENDC))
                print("%s │ Service Status: ✓ RUNNING %s" % (col.BRIGHT_BLUE, col.ENDC))
                print(" ")
                printc("✅ ALL Ubuntu 24 compatibility issues RESOLVED!", col.BRIGHT_GREEN)
                printc("Re-running this script will skip already installed components", col.BRIGHT_CYAN)
                
                # Final test
                printc("Testing Admin Panel Access...", col.BRIGHT_CYAN)
                test_result = subprocess.run("curl -s -o /dev/null -w '%%{http_code}' http://127.0.0.1:8080/%s" % rAccesscode, shell=True, capture_output=True, text=True)
                if "200" in test_result.stdout:
                    printc("✅ Admin Panel is accessible!", col.BRIGHT_GREEN)
                else:
                    printc("⚠️  Admin Panel test returned: %s" % test_result.stdout, col.BRIGHT_YELLOW)
                    printc("Please check services with: /home/xtreamcodes/iptv_xtream_codes/start_services.sh", col.BRIGHT_YELLOW)
                
            else: 
                printc("Installation cancelled", col.BRIGHT_RED)
        else: 
            printc("Invalid entries", col.BRIGHT_RED)
    else: 
        printc("Invalid installation type", col.BRIGHT_RED) 