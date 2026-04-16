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

`uv` automatically manages Python versions and dependencies, keeping your system clean.

1. Add user to dialout group
    ```
    sudo usermod -aF dialout igel
    ```

2. Install dependencies
    ```
    sudo apt install \
    python3-pyqt6 \
    python3-pyqt6.qtwebengine \
    libqt6webenginecore6-bin
    python3-tk \
    scrot \
    python3-venv \
    python3-pip
    ```

3.  Clone the project from Github
    ```
    https://github.com/Oberfeldwedler/km3003.git
    ```

4. Prepare venv

```
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install nicegui[native] pyautogui cryptography pymysql pyserial qtpy PyQt6-WebEngine
```

4. Calibrate for touchscreen manually or execute `calibrate_touchscreen.sh`

    ```
    xinput set-prop "eGalax Inc. USB TouchController" "libinput Calibration Matrix" 1.1707, 0.0, -0.0888, 0.0, 1.1141, -0.0636, 0.0, 0.0, 1.0
    xinput_calibrator -v
    xinput set-prop "eGalax Inc. USB TouchController" "libinput Calibration Matrix" 0.9829, 0.0, 0.006, 0.0, -1.0119, 1.0005, 0.0, 0.0, 1.0
    ```

5.  Configure `calibrate_touchscreen.sh` to run on Login and setup screen timeout
    Don't forget to make the script executable with `chmod +x calibrate_touchscreen.sh`


6.  **Run the App** and add to autostart
    ```bash
    python3 main.py
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

## Use python webserver to copy paste stuff from AI

Execute this in this dir and create an index.html
```
sudo python -m http.server 80
```

## Install vnc

´´´
sudo apt install krfb
´´´