<img width="2557" height="1078" alt="2026-05-10_21-47" src="https://github.com/user-attachments/assets/be0a40c5-cb8a-4536-ba9c-504bd2f1e975" /><br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/OS-Linux-orange?style=for-the-badge&logo=linux" alt="OS">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen?style=for-the-badge"
 alt="Status">
</p>

> **Automated VLESS Reality management daemon with dynamic SNI/port rotation for X-UI panels.**

---

### 📖 Documentation

[English](readme-en.md) | [Русский](readme-ru.md) | [简体中文](readme-zh.md) | [فارسى](readme-fa.md)

---

### 🚀 Features

| Feature | Description |
|---------|-------------|
| **SNI Rotation** | `best_ping` (lowest latency) or `random_sni` (pool of 14+ domains) |
| **Port Modes** | `dynamic` (49152-65535) or `standard` (80, 443, 2053, etc.) |
| **Migration** | Seamless config swap with 40-min client migration window |
| **Firewall** | Auto-updating `ufw` rules synchronized with port rotation |
| **WebUI** | Multi-language dashboard (EN/RU/ZH/FA) with light/dark themes |
| **Subscription** | Built-in secure subscription server with customizable paths |

---

### 🛠 Quick Install

```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
git clone https://github.com/neeitr0n/AegisVLESS.git
cd AegisVLESS
chmod +x aegis.py
sudo python3 aegis.py
```

---

### 📂 Project Structure

```
.
├── aegis.py                    # Core logic & CLI
├── gui/                        # Web interface
│   ├── index_template.html     # Panel template
│   ├── index_data.html        # Generated panel
│   └── login.html             # Auth page
├── readmeEN.md                 # English docs
├── readmeRU.md                 # Russian docs
├── readmeZH.md                 # Chinese docs
├── readmeFA.md                 # Persian docs
└── .gitignore
```

---

### 📋 Requirements

- **OS:** Linux (Ubuntu 20.04+, Debian 11+) with `systemd`
- **Dependencies:** Python 3.8+, `sqlite3`, `ufw`, `curl`, `git`
- **Permissions:** Root required

---

### 🔗 SNI Pool
<details>
<summary>View configured domains</summary>

- rutube.ru
- yandex.ru
- ya.ru
- www.python.org
- www.microsoft.com
- www.apple.com
- www.samsung.com
- www.oracle.com
- www.pinterest.com
- www.kernel.org
- www.cisco.org
- www.nvidia.com
- www.amd.com
</details>

---

### ⚠️ Disclaimer

This tool is for educational purposes only. The author is not responsible for any misuse or damages caused by this software.

---

### ⭐ Support

Was this tool helpful? Give it a ⭐ as a "thank you"!
