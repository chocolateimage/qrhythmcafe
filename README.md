# Developing
You will need Python for this during development.

#### Linux
You need to install PyQT5 and requests with apt:

`sudo apt install python3-pyqt5 python3-requests`
#### Windows
On windows you need to install PyQT5 and requests with pip:

`pip install PyQT5 requests`

## Building

#### Linux

Go to the "deb" directory

`cd deb`

Run "packagedeb.sh". This file will copy all required files into the correct "usr" folders for building into a `qrhythmcafe.deb` file

Command: `./packagedeb.sh`

---

If you have any issues, report them in the [issue tracker](https://github.com/chocolateimage/qrhythmcafe/issues) on GitHub