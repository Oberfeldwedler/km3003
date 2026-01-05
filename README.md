# KM3003

Die gesamte Dokumentation, inklusive der Abschlusspräsentation und Datenbank Creation-Statements, wurde in das Submodul `km3003_docs` ausgelagert.

## Description
Der Kühlschrankmanager im Vertretungszimmer der Fachschaft ersetzt die Strichliste, welche früher am Kühlschrank hing und die Getränkekäufe der Vereinsmitglieder erfasste.

Der KM3003 ist die Weiterentwicklung der bisherigen Kühlschrankmanager. Während Vorgängerversionen auf proprietären oder älteren Frameworks basierten, setzt der KM3003 auf moderne Web-Technologien (**NiceGUI**) für eine flüssige Touch-Bedienung und einfache Wartung.

**Features:**
* **Self-Checkout POS:** Touchscreen-Interface für Getränkekäufe.
* **Barcode-Scan:** Identifikation von Mitgliedern (Studentenausweis) und Produkten (EAN-Codes).
* **Guthaben-System:** Unterstützt positive Guthaben und Schulden.
* **Modern UI:** Web-basiertes Frontend (lokal laufend via NiceGUI).

## EI Wiki Eintrag

https://ei-wiki.oth-regensburg.de/wiki/K%C3%BChlschrankbuchungssystem_KM3003

## Prerequisites

* **MySQL Database:** Requires a running MySQL server (see Docker instructions below).
* **Hardware:** Barcode Scanner (Serial/USB) & Touchscreen.

## Installation via `uv`

`uv` automatically manages Python versions and dependencies, keeping your system clean.

1.  **Install uv** (if not already installed):

    https://docs.astral.sh/uv/getting-started/installation/

2. Clone the project from Github
    ```
    https://github.com/Oberfeldwedler/km3003.git
    ```

3.  **Sync Dependencies**:
    Navigate to the project folder and run:
    ```bash
    uv sync
    ```
    *This will install the correct Python version (>=3.12) and all libraries defined in `pyproject.toml`.*

4.  **Run the App**:
    ```bash
    uv run main.py
    ```

## Configuration

1.  **Create Config File**:
    Copy the sample configuration file:
    * `cp km3003_sample.conf km3003.conf` (Linux)
    * Or manually copy and rename `km3003_sample.conf` to `km3003.conf`.

2.  **Edit `km3003.conf`**:
    Open the file and adjust the settings:
    * **[mysql]**: Enter host, port, user, password, and database name.
    * **[serial]**: Set the correct COM port (Windows, e.g., `COM3`) or path (Linux, e.g., `/dev/ttyACM0`).
    * **[general]**: Adjust timeouts or primary colors if desired.

    *Tip: To test without a physical scanner, set `console_input = True` in the config and type barcodes into the terminal.*


2.  **Import Schema**:
    * Connect to the database (e.g., via MySQL Workbench).
    * Execute the creation statements found in `km3003_docs` or the resource folder.
    * Import initial users and products.
