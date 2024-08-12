# km3003

## Setup

### Windows

1. install python
    - do *NOT* install als admin
    - set the checkbox to add to `PATH`

2. install python libraries
    ```
    python -m pip install pysimplegui pyserial pymysql cryptography
    ```

3. setup km3003.conf
    - make a copy of `km3003_sample.conf` and name it `km3003.conf` 
    - customize database info
    - customize COM port

4. TODO: get hobby pysimplegui license key from pysimplegui.com 
 
4. TODO: configure scheduled reboot and updates

# Raspbian standalone

    Notes: For mysql in a docker container, you will need 64bit Raspberry Pi OS

1. Setup database with docker

mysql docker-compose.yml
```yaml
version: '3'

    services:
    db:
        image: mysql:8.0
        command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
        restart: unless-stopped
        ports:
        - 3306:3306
        volumes:
        - ./mysql:/var/lib/mysql
        env_file:
        - .env
```
### .env
```ini
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
```

Copy create statements of real km3003 db and eexcute via mysql workbench for all four databases
Copy users and product rows via mysql workbench

2. install python modules

```
 pip3 install pyserial --break-system-packages pymysql --break-system-packages pysimplegui
```

3. clone km3003 repo

4. `cp km3003_sample.conf km3003.conf`

5. setup resolution to `800x480` and configure rest of config file

    scanner is probably `/dev/ttyACM0`

6. first start of program... use geanny. Because lazy
7. left button in pysimplegui activation to enter license key
8. start again

## How to create .exe

```
python -m pip install pyinstaller
python -m PyInstaller km3003.py --onefile --noconsole

PyInstaller km3003.py --onefile --noconsole --paths=c:\users\igel\appdata\roaming\python\python312\site-packages 
```


## How to install OpenSSH Server in Windows 11

Settings >> System >> Optional Features

Add Feature >> Search for SSH >> OpenSSH Server

`WIN + R` >> `services.msc` >> 