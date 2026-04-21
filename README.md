# AegisVLESS

```text
                                                                            
▄████▄ ▄▄▄▄▄  ▄▄▄▄ ▄▄  ▄▄▄▄   ██  ██ ██     ██████ ▄█████ ▄█████   
██▄▄██ ██▄▄  ██ ▄▄ ██ ███▄▄   ██▄▄██ ██     ██▄▄   ▀▀▀▄▄▄ ▀▀▀▄▄▄   
██  ██ ██▄▄▄ ▀███▀ ██ ▄▄██▀    ▀██▀  ██████ ██▄▄▄▄ █████▀ █████▀                                                      
                                           
```

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/OS-Linux-orange?style=for-the-badge&logo=linux" alt="OS">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen?style=for-the-badge" alt="Status">
</p>

> <b>Was this tool helpful? Give it a ⭐ as a "thank you"!</b>
> <b>Инструмент был полезен? Поставь ⭐ в качестве «спасибо»!</b>
[English](#english) | [Русский](#русский)

---

<a name="english"></a>
## English

A standalone Python daemon and CLI tool designed for automated management and dynamic rotation of **VLESS Reality** configurations within X-UI panels. Aegis eliminates manual intervention by interacting directly with the SQLite database to ensure high availability and censorship resistance.

### 🛠 Architecture Flow
```mermaid
graph TD
    A[AegisVLESS Daemon] -->|Direct SQL Mutation| B[(X-UI SQLite DB)]
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
- **Subscription Server:** Built-in server for delivering links via secure, customizable paths.

### 📂 Project Structure
```text
.
├── aegis.py            # Main logic and CLI menu
├── README.md           # Project documentation
└── .gitignore          # Git exclusions
```

### 🛠 System Requirements
- **OS:** Linux distributions with `systemd` (Ubuntu 20.04+, Debian 11+).
- **Dependencies:** Python 3.8+, `sqlite3`, `ufw`, `curl`, `git`.
- **Permissions:** Must be run as `root`.

### 📦 Installation & Usage
1. **Clone & Prepare:**
   ```bash
   git clone https://github.com/neeitr0n/AegisVLESS.git
   cd AegisVLESS
   chmod +x aegis.py
   ```
2. **Initial Setup:**
   ```bash
   sudo python3 aegis.py
   ```
3. **Daemon Control:**
   ```bash
   sudo systemctl status aegis
   sudo journalctl -u aegis -f
   ```

---

<a name="русский"></a>
## Русский

Автономный Python-демон и CLI-утилита для автоматизированного управления и динамической ротации конфигураций **VLESS Reality** в панелях X-UI. Aegis исключает необходимость ручной настройки, взаимодействуя напрямую с базой данных SQLite для обеспечения максимальной скрытности и обхода блокировок.

### 🛠 Схема работы
```mermaid
graph TD
    A[AegisVLESS Daemon] -->|Прямая правка SQL| B[(X-UI SQLite DB)]
    A -->|Сохранение состояния| A
    A -->|Управление портами| C[UFW Firewall]
    A -->|Автоматизация| D[Служба systemd]
    A -->|Доставка API| E[Защищенный сервер подписок]
    B -->|Обновление| F[VLESS Reality Inbound]
```

### 🌟 Основные возможности
- **Прямая модификация БД:** Работа с `/etc/x-ui/x-ui.db` для мгновенного обновления настроек без перезапуска всей панели.
- **Умная ротация SNI:**
  - `best_ping`: Автоматический выбор домена с минимальной задержкой.
  - `random_sni`: Случайный выбор из пула проверенных доменов.
- **Гибкие порты:** Поддержка стандартных веб-портов (80, 443 и др.) или динамического диапазона (42000-65000).
- **Автоматизация UFW:** Синхронное открытие новых и закрытие старых портов в фаерволе.
- **Автономность:** Никаких внешних `.json` конфигов; все состояние хранится внутри логики скрипта.
- **Сервер подписок:** Встроенный сервер для раздачи актуальных ссылок по защищенному пути.

### 📂 Структура проекта
```text
.
├── aegis.py            # Основная логика и CLI меню
├── README.md           # Документация проекта
└── .gitignore          # Исключения Git
```

### 🛠 Системные требования
- **ОС:** Linux дистрибутивы с поддержкой `systemd` (Ubuntu 20.04+, Debian 11+).
- **Зависимости:** Python 3.8+, `sqlite3`, `ufw`, `curl`, `git`.
- **Права:** Требуется запуск от имени `root`.

### 📦 Установка и использование
1. **Клонирование:**
   ```bash
   git clone https://github.com/neeitr0n/AegisVLESS.git
   cd AegisVLESS
   chmod +x aegis.py
   ```
2. **Первоначальная настройка:**
   ```bash
   sudo python3 aegis.py
   ```
3. **Управление службой:**
   ```bash
   sudo systemctl status aegis
   sudo journalctl -u aegis -f
   ```

---

### 🔗 SNI Pool / Пул доменов
<details>
<summary>View configured domains / Посмотреть список доменов</summary>

- rutube.ru
- yandex.ru
- vk.com
- ozon.ru
- ya.ru
- wildberries.ru
- python.org
- microsoft.com
- apple.com
- samsung.com
- oracle.com
- pinterest.com
- kernel.org
- cisco.org
- nvidia.com
- amd.com
</details>

---

### ⚠️ Disclaimer
This tool is for educational purposes only. The author is not responsible for any misuse or damages caused by this software.
