# Aegis Surgeon

[Русская версия ниже](#русская-версия)

A standalone Python daemon and CLI tool for managing, automating, and dynamically rotating VLESS Reality configurations within X-UI panels. Aegis operates by directly interacting with the X-UI SQLite database, providing automated evasion techniques via SNI and port rotation without requiring manual panel intervention.

## Core Features

* **Direct Database Mutation:** Modifies inbound proxies and network settings directly via `/etc/x-ui/x-ui.db`.
* **Dynamic Rotation Engine:**
    * **SNI Rotation:** Supports selection from a predefined pool via random assignment or lowest latency (ping) analysis.
    * **Port Rotation:** Supports shifting between standard web ports (80, 443, etc.) or dynamic ephemeral ports (42000-65000).
* **Systemd Integration:** Automatically deploys and manages itself as a background daemon (`aegis.service`).
* **Firewall Automation:** Dynamically manages `ufw` rules to open new ports and close old ones during rotation cycles.
* **Subscription Provisioning:** Automatically generates and serves VLESS links via a secure, randomized subscription path utilizing a built-in HTTP server.
* **Self-Modifying Configuration:** Persists CLI menu state by rewriting its own variable definitions, eliminating the need for external `.json` dependencies.

## System Requirements

* **OS:** Any modern Linux distribution with systemd (Ubuntu, Debian, etc.)  
* **Dependencies:** Python 3.x, `sqlite3`, `ufw`, `curl`
* **Privileges:** `root` execution is strictly required (for `systemctl`, `ufw`, and database write access).
* **Environment:** An existing and active X-UI panel (or fork like 3x-ui). 
    * *Note:* The script expects the database to be located at `/etc/x-ui/x-ui.db` and uses the `x-ui restart` command.

## Installation & Usage

1. **Download the script:**
   Ensure the script is placed in a directory where it has read/write permissions, as it updates its own configuration variables.
   ```bash
   wget -O aegis.py <raw_github_url>
   chmod +x aegis.py
   ```

2. **Initial Setup & CLI Menu:**
   Run the script with root privileges to access the configuration menu.
   ```bash
   sudo python3 aegis.py
   ```

3. **Service Management:**
   Once configured, use the CLI menu to install and start the background service. You can monitor the daemon via standard systemd commands:
   ```bash
   sudo systemctl status aegis
   sudo journalctl -u aegis -f
   ```

---

<a name="русская-версия"></a>
# AegisVLESS (Русский)

Автономный Python-daemon и CLI-утилита для управления, автоматизации и динамической ротации конфигураций VLESS Reality в панелях X-UI. Aegis работает напрямую с SQLite-базой данных X-UI, обеспечивая автоматизированный обход блокировок с помощью ротации SNI и портов без необходимости ручного вмешательства через веб-интерфейс.

## Основные возможности

* **Прямое взаимодействие с БД:** Модификация входящих прокси и сетевых настроек напрямую через `/etc/x-ui/x-ui.db`.
* **Движок динамической ротации:**
    * **Ротация SNI:** Поддержка выбора из заданного пула случайным образом или на основе анализа минимальной задержки (ping).
    * **Ротация портов:** Переключение между стандартными веб-портами (80, 443 и т.д.) или динамическими портами (42000-65000).
* **Интеграция с systemd:** Автоматическое развертывание и управление в виде фонового процесса (`aegis.service`).
* **Управление фаерволом:** Динамическое управление правилами `ufw` для открытия новых портов и закрытия старых в процессе ротации.
* **Генерация подписок:** Встроенный HTTP-сервер для раздачи актуальных VLESS-ссылок по защищенному рандомизированному пути.
* **Самомодифицируемая конфигурация:** Сохранение состояния CLI-меню путем перезаписи собственных переменных в коде, что исключает зависимость от внешних файлов `.json`.

## Системные требования

* **ОС:** Любой современный дистрибутив Linux с поддержкой systemd (Ubuntu, Debian и др.)
* **Зависимости:** Python 3.x, `sqlite3`, `ufw`, `curl`
* **Права:** Строго требуется запуск от имени `root` (для `systemctl`, `ufw` и записи в БД).
* **Окружение:** Установленная и работающая панель X-UI (или форк, например 3x-ui). 
    * *Примечание:* Скрипт ожидает, что база данных находится по пути `/etc/x-ui/x-ui.db`, и использует системную команду `x-ui restart`.

## Установка и использование

1. **Загрузка скрипта:**
   Убедитесь, что скрипт находится в директории с правами на чтение и запись, так как он обновляет собственные конфигурационные переменные.
   ```bash
   wget -O aegis.py <raw_github_url>
   chmod +x aegis.py
   ```

2. **Первичная настройка и CLI меню:**
   Запустите скрипт с правами root для доступа к конфигурационному меню.
   ```bash
   sudo python3 aegis.py
   ```

3. **Управление службой:**
   После конфигурации используйте меню CLI для установки и запуска фоновой службы. Мониторинг демона осуществляется стандартными командами systemd:
   ```bash
   sudo systemctl status aegis
   sudo journalctl -u aegis -f
   ```
