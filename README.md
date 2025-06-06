# 🚀 Xtream UI for Ubuntu 24

[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-orange.svg)](https://releases.ubuntu.com/24.04/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.5%2B-blue.svg)](https://mariadb.org/)
[![License](https://img.shields.io/badge/License-Open%20Source-green.svg)](LICENSE)

## 📋 Descriere

Acest repository conține toate componentele necesare pentru instalarea **Xtream Codes IPTV panel** pe **Ubuntu 24.04** cu compatibilitate completă Ubuntu 18.

### ✅ **Caracteristici Principale**

- 🔧 **Instalare automată** cu un singur script
- 🗄️ **MariaDB 10.5+** din repository oficial
- 📚 **Librarii Ubuntu 18** pentru compatibilitate completă
- 🔗 **Symlink-uri automate** pentru librariile critice
- 🛡️ **Fixuri SSL/CURL/PNG** integrate
- ⚡ **LD_LIBRARY_PATH** configurat automat
- 👤 **Admin user** creat automat

## 📂 Structura Repository

```
├── libs/                    # Librarii Ubuntu 18 (.deb packages)
│   ├── libssl1.0.0_*.deb   # OpenSSL 1.0.x pentru OPENSSL_1.0.1
│   ├── libcurl3_*.deb      # CURL pentru CURL_OPENSSL_3
│   ├── libpng12-0_*.deb    # PNG12 pentru PNG12_0
│   └── ...                 # Alte librarii critice
├── mariadb/                # MariaDB setup tools
│   └── mariadb_repo_setup  # Script oficial MariaDB
├── scripts/                # Scripts de instalare
│   └── install_ubuntu24_fixed.py
└── README.md
```

## 🚀 Instalare Rapidă

```bash
# Download și rulare directă
wget -O install.py https://raw.githubusercontent.com/mirelsen/xtreanui-for-Ubuntu24/main/scripts/install_ubuntu24_fixed.py
python3 install.py
```

## 🔧 Instalare Manuală

```bash
# 1. Clone repository
git clone https://github.com/mirelsen/xtreanui-for-Ubuntu24.git
cd xtreanui-for-Ubuntu24

# 2. Rulează scriptul
python3 scripts/install_ubuntu24_fixed.py
```

## 📋 Cerințe Sistem

- **Ubuntu Server 24.04 LTS**
- **Minimum 2GB RAM** (recomandat 4GB+)
- **20GB spațiu disc liber**
- **Conexiune internet activă**

## 🛠️ Funcționalități

### ✅ **Compatibilitate Automată**
- Instalare automată librarii Ubuntu 18
- Creare symlink-uri pentru:
  - `libssl.so.1.0.0` → `libssl.so.1.0`
  - `libcrypto.so.1.0.0` → `libcrypto.so.1.0`
  - `libpng12.so.0` → `libpng16.so.16`
  - `libcurl.so.4` compatibility

### 🗄️ **MariaDB Robust**
- Curățare completă a MySQL/MariaDB existent
- Instalare MariaDB 10.5+ din repository oficial
- Configurare optimizată pentru Xtream Codes
- Port 7999 (standard Xtream)

### 📊 **După Instalare**
- **Admin Panel**: `http://YOUR_IP:8080/ACCESS_CODE`
- **Login**: `admin/admin`
- **Database**: MariaDB pe port 7999
- **Services**: Toate pornite automat

## 🔍 Rezolvare Probleme

### Probleme Comune și Soluții

**1. Eroare: `CURL_OPENSSL_3 not found`**
```bash
# Scriptul repară automat - rulează din nou
python3 scripts/install_ubuntu24_fixed.py
```

**2. Eroare: `PNG12_0 not found`**
```bash
# Verifică dacă libpng12 este instalat
dpkg -l | grep libpng12
```

**3. MariaDB nu pornește**
```bash
# Scriptul face curățare completă și reinstalare
systemctl status mariadb
```

## 📝 Credite

- Repository menținut de [@mirelsen](https://github.com/mirelsen)
- Bazat pe Xtream Codes IPTV panel
- Adaptat pentru Ubuntu 24.04 LTS

## 📄 Licență

Acest proiect este open source și disponibil sub licența standard.

---

### 🆘 Support

Pentru probleme sau întrebări, creează un [Issue](https://github.com/mirelsen/xtreanui-for-Ubuntu24/issues) în acest repository. 