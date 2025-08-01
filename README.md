# QRhythmCafe

![image](https://github.com/chocolateimage/qrhythmcafe/assets/45315451/3e0d0f64-20e0-49e4-ba22-6a74c44fc02d)

## How can I run this?

**WINDOWS:** Download the .exe: https://github.com/chocolateimage/qrhythmcafe/releases

**DEBIAN / UBUNTU / MINT:** Use the repository at https://packages.playlook.de/deb/ for automatic updates. Follow the repository commands then run `sudo apt install qrhythmcafe`

**ARCH:** Use the [AUR package](https://aur.archlinux.org/packages/qrhythmcafe): `yay -S qrhythmcafe`

## Developing
You will need Python for this during development.

#### Linux

You need to install these Python packages, preferrably with your package manager to get native themes:

```bash
# apt (Debian, Ubuntu, Mint, etc.)
sudo apt install python3-pyqt6 python3-requests pyqt6-dev-tools python3-yaml

# Pacman (Arch)
sudo pacman -S --needed python python-pyqt6 python-requests python-yaml
```

#### Windows

On windows you need to install PyQt6 and requests with pip:

`pip install PyQt6 requests PyYAML`

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

# Reporting Issues

If you have any issues or feature requests, report them in the [issue tracker](https://github.com/chocolateimage/qrhythmcafe/issues) on GitHub.
