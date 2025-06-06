# QRhythmCafe

![image](https://github.com/chocolateimage/qrhythmcafe/assets/45315451/3e0d0f64-20e0-49e4-ba22-6a74c44fc02d)

## How can I run this?

Download the .exe (or .deb if you're on Linux) from the releases section: https://github.com/chocolateimage/qrhythmcafe/releases

## Developing
You will need Python for this during development.

#### Linux
You need to install PyQt6 and requests with apt:

`sudo apt install python3-pyqt6 python3-requests pyqt6-dev-tools`

#### Windows
On windows you need to install PyQt6 and requests with pip:

`pip install PyQt6 requests`

## Building

#### Windows

1. Install "pyinstaller": `pip install pyinstaller`
2. Run "buildwindows.bat"
3. In the dist folder there should be a file with the name of "qrhythmcafe.exe"

#### Linux

Go to the "deb" directory

`cd deb`

Run "packagedeb.sh". This file will copy all required files into the correct "usr" folders for building into a `qrhythmcafe.deb` file

Command: `./packagedeb.sh`

---

If you have any issues, report them in the [issue tracker](https://github.com/chocolateimage/qrhythmcafe/issues) on GitHub
