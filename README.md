# km3003

## Setup IDE

### Windows


```
python -m pip install pysimplegui
python -m pip install pyserial
python -m pip install mysql-connector-python
```



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