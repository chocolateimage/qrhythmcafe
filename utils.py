from pathlib import Path

try:
    from gi.repository import GLib

    has_glib = True
except Exception:
    has_glib = False
import urllib.request
import zipfile
import os
import shutil
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette

VERSION_NUMBER = "0.2.0"


def get_temp_folder():
    if has_glib:
        path = GLib.get_user_cache_dir() + "/qrhythmcafe_temp"
    elif os.name == "win32":
        path = str(Path.home()) + "/AppData/Local/Temp/qrhythmcafe_temp"
    else:
        path = str(Path.home()) + "/.cache/qrhythmcafe_temp"

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def get_rd_levels_folder():
    if has_glib:
        return (
            GLib.get_user_special_dir(GLib.USER_DIRECTORY_DOCUMENTS)
            + "/Rhythm Doctor/Levels"
        )
    else:
        return str(Path.home()) + "/Documents/Rhythm Doctor/Levels"


def get_rd_level_folder(foldername):
    return get_rd_levels_folder() + "/" + foldername


# returns None if level not installed and returns the folder name if it's installed
def get_available_rd_level_name(data):
    names = [
        data["id"],
        data["id"] + ".rdzip",
        data["id"] + ".rdzip_FILES",
        data["id"] + "_FILES",
        data.get("rdlevel_sha1", None),
        data.get("sha1", None),
    ]
    for i in names:
        if i is None:
            continue
        if os.path.isdir(get_rd_level_folder(i)):
            return i
    return None


def download_rd_level(data):
    rdzippath = get_temp_folder() + "/" + data["id"] + ".rdzip"
    levelpath = get_rd_level_folder(data["id"])
    urllib.request.urlretrieve(data["url2"], rdzippath)
    with zipfile.ZipFile(rdzippath, "r") as z:
        z.extractall(levelpath)
    os.remove(rdzippath)


def remove_rd_level(data):
    foldername = get_available_rd_level_name(data)
    if foldername is None:
        return
    path = get_rd_level_folder(foldername)
    shutil.rmtree(path)


def is_dark_mode():
    app = QApplication.instance()
    palette = app.palette()
    background_color = palette.color(QPalette.ColorRole.Window)
    brightness = (
        background_color.red() + background_color.green() + background_color.blue()
    ) / 3
    return brightness < 128


def get_icon_path(icon_name):
    if is_dark_mode():
        return "ui/" + icon_name + "-darkmode.svg"
    else:
        return "ui/" + icon_name + "-lightmode.svg"
