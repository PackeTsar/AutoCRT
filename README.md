# AutoCRT
Quickly build SecureCRT SSH sessions


-----------------------------------------
####   TABLE OF CONTENTS   ####

1. [How to Use](#how-to-use)
2. [Requirements](#requirements)
4. [Compile](#compile)
5. [Contributing](#contributing)


--------------------------------------
####   HOW TO USE   ####
AutoCRT will work on Windows or MacOS. Binary files for each are provided in the bin directory






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