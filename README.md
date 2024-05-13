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