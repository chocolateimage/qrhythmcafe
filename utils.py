from pathlib import Path
try:
    from gi.repository import GLib
    hasgi = True
except Exception:
    hasgi = False
import urllib.request
import zipfile
import os
import shutil
from PyQt5.QtCore import QObject, QThread, QMutex, pyqtSignal

VERSION_NUMBER = "0.0.2"


class MultiThreadedDownload(QObject):
    queueupdated = pyqtSignal()
    class DownloadThread(QThread):
        def run(self):
            while True:
                print("locking (3)")
                _mtd.lock.lock()
                if len(_mtd.downloadqueue) == 0:
                    print("unlocking (3.1)")
                    _mtd.lock.unlock()
                    break
                downloadprocess: DownloadProcess = _mtd.downloadqueue.pop(0)
                _mtd.isdownloading.append(downloadprocess)
                downloadprocess.is_started = True
                print("unlocking (3.2)")
                _mtd.lock.unlock()
                _mtd.queueupdated.emit()
                print("doing bg download")
                downloadprocess._bgdownload()
                downloadprocess.is_finished = True
                print("emitting finished")
                downloadprocess.finished.emit()
                print("locking (4)")
                _mtd.lock.lock()
                _mtd.isdownloading.remove(downloadprocess)
                _mtd.downloadfinished.append(downloadprocess)
                print("unlocking (4)")
                _mtd.lock.unlock()
                _mtd.queueupdated.emit()
            print("trying to finish this thread (locking 5)")
            _mtd.lock.lock()
            _mtd.threads.remove(self)
            _mtd.finishedthreads.append(self)
            print("unlocking (5)")
            _mtd.lock.unlock()
            print("finished with this thread!")
    
    def __init__(self):
        super().__init__()
        self.downloadqueue = []
        self.isdownloading = []
        self.downloadfinished = []
        self.lock = QMutex()
        self.threads = []
        self.finishedthreads = [] # needs weirdly else it crashes

    def add_to_queue(self,downloadprocess):
        newthread = None
        print("threads",len(self.threads))
        if len(self.threads) < 7:
            print("under 7 threads, creating new")
            self.lock.lock()
            print("created...")
            newthread = MultiThreadedDownload.DownloadThread()
            self.threads.append(newthread)
            print("unlocking... (1)")
            self.lock.unlock()
        print("locking (2)")
        self.lock.lock()
        self.downloadqueue.append(downloadprocess)
        print("unlocking (2)")
        self.lock.unlock()
        if newthread != None:
            print("starting new thread... " + str(len(self.threads)) + " threads now")
            newthread.start(QThread.Priority.LowPriority)
        self.queueupdated.emit()

class DownloadProcess(QObject):
    finished = pyqtSignal()
    def __init__(self,data):
        super().__init__()
        self.data = data
        self.is_started = False
        self.is_finished = False
    def _bgdownload(self):
        data = self.data
        rdzippath = get_temp_folder() + "/" + data["id"] + ".rdzip"
        levelpath = get_rd_level_folder(data["id"])
        urllib.request.urlretrieve(data["url2"],rdzippath)
        with zipfile.ZipFile(rdzippath,"r") as z:
            z.extractall(levelpath)
        os.remove(rdzippath)

_mtd = MultiThreadedDownload()

def get_temp_folder():
    if hasgi:
        path = GLib.get_user_cache_dir() + "/qrhythmcafe_temp"
    else:
        path = str(Path.home()) + "/AppData/Local/Temp/qrhythmcafe_temp"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_rd_levels_folder():
    if hasgi:
        return GLib.get_user_special_dir(GLib.USER_DIRECTORY_DOCUMENTS) + "/Rhythm Doctor/Levels"
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
        data.get("rdlevel_sha1",None),
        data.get("sha1",None),
    ]
    for i in names:
        if i == None:
            continue
        if os.path.isdir(get_rd_level_folder(i)):
            return i
    return None

def download_rd_level(data,onfinish):
    downloadprocess = DownloadProcess(data)
    downloadprocess.finished.connect(onfinish)
    _mtd.add_to_queue(downloadprocess)
    return downloadprocess

def remove_rd_level(data):
    foldername = get_available_rd_level_name(data)
    if foldername == None:
        return
    path = get_rd_level_folder(foldername)
    shutil.rmtree(path)