# Aegis Surgeon

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/OS-Linux-orange?style=for-the-badge&logo=linux" alt="OS">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen?style=for-the-badge" alt="Status">
</p>

```text
                                                                                                                                                                                                               
                                                                                                                                                                                                               
               AAA                                                      iiii               VVVVVVVV           VVVVVVVVLLLLLLLLLLL             EEEEEEEEEEEEEEEEEEEEEE   SSSSSSSSSSSSSSS    SSSSSSSSSSSSSSS      
              A:::A                                                    i::::i              V::::::V           V::::::VL:::::::::L             E::::::::::::::::::::E SS:::::::::::::::S SS:::::::::::::::S     
             A:::::A                                                    iiii               V::::::V           V::::::VL:::::::::L             E::::::::::::::::::::ES:::::SSSSSS::::::SS:::::SSSSSS::::::S     
            A:::::::A                                                                      V::::::V           V::::::VLL:::::::LL             EE::::::EEEEEEEEE::::ES:::::S     SSSSSSSS:::::S     SSSSSSS     
           A:::::::::A            eeeeeeeeeeee       ggggggggg   gggggiiiiiii     ssssssssssV:::::V           V:::::V   L:::::L                 E:::::E       EEEEEES:::::S            S:::::S                 
          A:::::A:::::A         ee::::::::::::ee    g:::::::::ggg::::gi:::::i   ss::::::::::sV:::::V         V:::::V    L:::::L                 E:::::E             S:::::S            S:::::S                 
         A:::::A A:::::A       e::::::eeeee:::::ee g:::::::::::::::::g i::::i ss:::::::::::::sV:::::V       V:::::V     L:::::L                 E::::::EEEEEEEEEE    S::::SSSS          S::::SSSS              
        A:::::A   A:::::A     e::::::e     e:::::eg::::::ggggg::::::gg i::::i s::::::ssss:::::sV:::::V     V:::::V      L:::::L                 E:::::::::::::::E     SS::::::SSSSS      SS::::::SSSSS         
       A:::::A     A:::::A    e:::::::eeeee::::::eg:::::g     g:::::g  i::::i  s:::::s  ssssss  V:::::V   V:::::V       L:::::L                 E:::::::::::::::E       SSS::::::::SS      SSS::::::::SS       
      A:::::AAAAAAAAA:::::A   e:::::::::::::::::e g:::::g     g:::::g  i::::i    s::::::s        V:::::V V:::::V        L:::::L                 E::::::EEEEEEEEEE          SSSSSS::::S        SSSSSS::::S      
     A:::::::::::::::::::::A  e::::::eeeeeeeeeee  g:::::g     g:::::g  i::::i       s::::::s      V:::::V:::::V         L:::::L                 E:::::E                         S:::::S            S:::::S     
    A:::::AAAAAAAAAAAAA:::::A e:::::::e           g::::::g    g:::::g  i::::i ssssss   s:::::s     V:::::::::V          L:::::L         LLLLLL  E:::::E       EEEEEE            S:::::S            S:::::S     
   A:::::A             A:::::Ae::::::::e          g:::::::ggggg:::::g i::::::is:::::ssss::::::s     V:::::::V         LL:::::::LLLLLLLLL:::::LEE::::::EEEEEEEE:::::ESSSSSSS     S:::::SSSSSSSS     S:::::S     
  A:::::A               A:::::Ae::::::::eeeeeeee   g::::::::::::::::g i::::::is::::::::::::::s       V:::::V          L::::::::::::::::::::::LE::::::::::::::::::::ES::::::SSSSSS:::::SS::::::SSSSSS:::::S     
 A:::::A                 A:::::Aee:::::::::::::e    gg::::::::::::::g i::::::i s:::::::::::ss         V:::V           L::::::::::::::::::::::LE::::::::::::::::::::ES:::::::::::::::SS S:::::::::::::::SS      
AAAAAAA                   AAAAAAA eeeeeeeeeeeeee      gggggggg::::::g iiiiiiii  sssssssssss            VVV            LLLLLLLLLLLLLLLLLLLLLLLLEEEEEEEEEEEEEEEEEEEEEE SSSSSSSSSSSSSSS    SSSSSSSSSSSSSSS        
                                                              g:::::g                                                                                                                                          
                                                  gggggg      g:::::g                                                                                                                                          
                                                  g:::::gg   gg:::::g                                                                                                                                          
                                                   g::::::ggg:::::::g                                                                                                                                          
                                                    gg:::::::::::::g                                                                                                                                           
                                                      ggg::::::ggg                                                                                                                                             
                                                         gggggg                                                                                                                                                
   
                                           
```

[English](#english) | [Русский](#русский)

---

<a name="english"></a>
## English

A standalone Python daemon and CLI tool designed for automated management and dynamic rotation of **VLESS Reality** configurations within X-UI panels. Aegis eliminates manual intervention by interacting directly with the SQLite database to ensure high availability and censorship resistance.

### 🛠 Architecture Flow

```mermaid
graph TD
    A[Aegis Daemon] -->|Direct SQL Mutation| B[(X-UI SQLite DB)]
    A -->|State Persistence| A
    A -->|Port Management| C[UFW Firewall]
    A -->|Automation| D[systemd Service]
    A -->|API Delivery| E[Secure Subscription Server]
    B -->|Update| F[VLESS Reality Inbound]
```

### 🚀 Key Features

- **Database-Level Integration:** Modifies `/etc/x-ui/x-ui.db` directly for zero-latency updates.
- **Intelligent SNI Rotation:** - `best_ping`: Automatic selection based on lowest latency.
  - `random_sni`: Randomized selection from a vetted pool.
- **Port Shifting:** Toggle between standard web ports (80, 443) and dynamic ephemeral ranges (42k-65k).
- **Self-Healing Firewall:** Automatic `ufw` rule updates synchronized with port rotation.
- **Stateless Configuration:** Zero external `.json` dependencies; state is maintained within the binary logic.

### 📦 Installation

```bash
git clone https://github.com/neeitr0n/AegisVLESS.git
cd AegisVLESS
chmod +x aegis_surgeon.py
```

### ⚙️ Usage

1. **Initial Setup:**
   ```bash
   sudo python3 aegis_surgeon.py
   ```
2. **Daemon Control:**
   ```bash
   sudo systemctl status aegis
   sudo journalctl -u aegis -f -n 50
   ```

---

<a name="русский"></a>
## Русский

Автономный Python-демон и CLI-утилита для автоматизированного управления и динамической ротации конфигураций **VLESS Reality** в панелях X-UI. Aegis исключает необходимость ручной настройки, взаимодействуя напрямую с базой данных SQLite для обеспечения максимальной скрытности и обхода блокировок.

### 🌟 Основные возможности

- **Прямая модификация БД:** Работа с `/etc/x-ui/x-ui.db` для мгновенного обновления настроек без перезапуска всей панели.
- **Умная ротация SNI:**
  - `best_ping`: Автоматический выбор домена с минимальной задержкой.
  - `random_sni`: Случайный выбор из пула проверенных доменов.
- **Гибкие порты:** Поддержка стандартных веб-портов (80, 443 и др.) или динамического диапазона (42000-65000).
- **Автоматизация UFW:** Синхронное открытие новых и закрытие старых портов в фаерволе.
- **Subscription Server:** Встроенный сервер для раздачи актуальных ссылок по защищенному пути.

### 📂 Структура проекта

```text
.
├── aegis_surgeon.py    # Основная логика и CLI меню
├── README.md           # Документация проекта
└── .gitignore          # Исключения Git
```

### 🛠 Системные требования

- **ОС:** Linux дистрибутивы с поддержкой `systemd` (Ubuntu 20.04+, Debian 11+).
- **Зависимости:** Python 3.8+, `sqlite3`, `ufw`, `curl`, `git`.
- **Права:** Требуется запуск от имени `root`.

### 🔗 Проверенный пул SNI

<details>
<summary>Нажмите, чтобы развернуть список доменов</summary>

- debian.org
- kernel.org
- python.org
- cloudflare.com
- microsoft.com
- wikipedia.org
- *и еще 55+ проверенных доменов с поддержкой TLS 1.3 и H2*
</details>

---

### ⚠️ Disclaimer
This tool is for educational purposes only. The author is not responsible for any misuse or damages caused by this software.
