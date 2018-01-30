# AutoCRT
Quickly build SecureCRT SSH sessions


--------------------------------------
####   HOW TO USE   ####
AutoCRT will work on Windows or MacOS. Binary files for each are provided in the bin directory

Running with the `-h` switch will provide you with some help
```
C:\Users\User> AutoCRT.exe -h
Usage: AutoCRT [options]

Options:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template=TEMPLATE
                        .INI file to use for template
  -l USER, --user=USER  SSH login name to use
  -w PASSWORD, --password=PASSWORD
                        SSH password to use
  -o OUTPUT_FOLDER, --output_folder=OUTPUT_FOLDER
                        Folder where .INI file is created
  -i HOSTNAME, --hostname=HOSTNAME
                        IP address or hostname of remote device
  -r RANGE, --range=RANGE
                        IP address range of hosts to find
  -d DEVICE_TYPE, --device_type=DEVICE_TYPE
                        Device Type
```

Windows Example (Single IP)
`AutoCRT.exe -t "C:\SecureCRT\Sessions\MyCustomerSession.ini" -i 192.168.1.1 -l admin -w password123`

Windows Example (IP Range)
`AutoCRT.exe -t "C:\SecureCRT\Sessions\MyCustomerSession.ini" -r 192.168.1.1-192.168.1.20 -l admin -w password123`

MacOS Example (Single IP) 
`./AutoCRT -t "/Users/MyUser/SecureCRT/Sessions/MyCustomerSession.ini" -i 192.168.1.1 -l admin -w password123`

MacOS Example (IP Range) 
`./AutoCRT -t "/Users/MyUser/SecureCRT/Sessions/MyCustomerSession.ini" -r 192.168.1.1-192.168.1.20 -l admin -w password123`


--------------------------------------
####   COMPILE   ####
AutoCRT requires the use of Python 2.7.X

##### Windows
  1. Install Python 2.7.X interpreter from the [Python Website][python_website]
  2. Download "pip-Win" from its [download site][pip_win]
  3. Open pip-Win and run with command `venv -c -i  pyi-env-name`
  4. Install PyInstaller with command `pip install PyInstaller`
    - You will also need to `pip install netmiko` and `pip install netaddr`
  5. Navigate a folder with AutoCRT.py
  6. Run command to compile: `pyinstaller --onefile AutoCRT.py`

##### MacOS/Linux
  1. Install Python 2.7.X and set as default interpreter
	  - Install [Homebrew][homebrew]
	  - Open Terminal and use Homebrew to install updated Python: `brew install python`
	  - Open the bash_profile in VI and add the new Python path: `more .bash_profile`
	    - Insert the line at the bottom: `export PATH="/usr/local/Cellar/python/2.7.13/bin:${PATH}"`
	  - Close Terminal and reopen it, type `python --version` and make sure it shows version 2.7.13 or greater
  2. Install Pip with command `sudo easy_install pip`
  3. Use Pip to install PyInstaller `pip install pyinstaller`
    - You will also need to `pip install netmiko` and `pip install netaddr`
  4. Run command to compile: `pyinstaller --onefile --windowed --icon=acid.ico --clean Acid.py`


[python_website]: https://www.python.org/
[pip_win]: https://sites.google.com/site/pydatalog/python/pip-for-windows
[homebrew]: https://brew.sh/