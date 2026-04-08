import os
from platformdirs import user_music_dir
from pathlib import Path
import psutil
import pygame
import sys
import subprocess
import shutil

def is_ffmpeg_installed():
    """
    Checks if FFmpeg is installed and accessible in the system PATH.
    Returns:
        bool: True if installed, False otherwise.
    """
    if shutil.which("ffmpeg") is None:
        return False

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        return False
    
supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg']

if is_ffmpeg_installed():
    supported_formats.append("m4a")


oper = ""
# Get other drives
if sys.platform.startswith('win'):
    oper = "windows"
elif sys.platform.startswith('linux'):
    oper = "linux"
elif sys.platform == 'darwin':
    oper = "mac"
else:
    oper = "default"

def get_music_files_and_directories(folder_path, SCREEN_HEIGHT, og_folder, dir_scroll=0, file_scroll=0):
    try:
        DIRECTORY_ONLY = [
            entry for entry in os.listdir(folder_path) 
            if os.path.isdir(os.path.join(folder_path, entry)) and not entry.startswith('.')
        ]

        directory_buttons = []

        for directory in DIRECTORY_ONLY:
            y_pos = (DIRECTORY_ONLY.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])
                
        FILES_ONLY = [
            entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]

        FILES_ONLY.sort(key=lambda entry: os.path.getctime(os.path.join(folder_path, entry)))

        file_buttons = []

        for file in FILES_ONLY:
            y_pos = SCREEN_HEIGHT/2+(FILES_ONLY.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2 - 30 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

        return DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, folder_path
    except Exception as e:
        print("access denied:", e)
        print("reopening music")
        print("og:", og_folder)

        DIRECTORY_ONLY = [
            entry for entry in os.listdir(og_folder) 
            if os.path.isdir(os.path.join(og_folder, entry)) and not entry.startswith('.')
        ]

        directory_buttons = []

        for directory in DIRECTORY_ONLY:
            y_pos = (DIRECTORY_ONLY.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])

        FILES_ONLY = [
            entry for entry in os.listdir(og_folder) if os.path.isfile(os.path.join(og_folder, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]

        FILES_ONLY.sort(key=lambda entry: os.path.getctime(os.path.join(og_folder, entry)))

        file_buttons = []

        for file in FILES_ONLY:
            y_pos = SCREEN_HEIGHT/2+(FILES_ONLY.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2 - 30 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

        return DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder
    
def get_drives():
    if oper == "windows" or oper == "linux":
        partitions = psutil.disk_partitions(all=True)
        drives = []
        for p in partitions:
            drives.append(p.mountpoint)
        return drives
    else:
        drives = []
        volumes = Path('/Volumes/')
        for drive in volumes.iterdir():
            drives.append(drive)
        
        return drives
    
def get_files(path, folder_type=False):
    folder_path = ""
    if folder_type:
        folder_type = path
    else:
        folder_path = Path(path).parent

    

    files = [
        entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
    ]

    files.sort(key=lambda entry: os.path.getctime(os.path.join(folder_path, entry)))

    if not(folder_type):
        index = 0
        if oper == "windows":
            index = files.index(str(path).split("\\")[-1])
        else:
            index = files.index(str(path).split("/")[-1])
        return files, index, str(folder_path)
    else:
        return files