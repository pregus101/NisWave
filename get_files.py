import os
from pathlib import Path
import psutil
import sys
import subprocess
import shutil
from typing import Any

from pygame import Surface

def is_ffmpeg_installed() -> bool:
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
    
supported_formats: list[str] = ['.mp3', '.wav', '.flac', '.aac', '.ogg']

if is_ffmpeg_installed():
    supported_formats.append(".m4a")

print(supported_formats)

oper: str = ""
# Get other drives
if sys.platform.startswith('win'):
    oper = "windows"
elif sys.platform.startswith('linux'):
    oper = "linux"
elif sys.platform == 'darwin':
    oper = "mac"
else:
    oper = "default"

def get_music_files_and_directories(folder_path: str, SCREEN_HEIGHT: int, og_folder: str, dir_scroll: int = 0, file_scroll: int = 0) -> tuple[list[str], list[str], list[Any], list[Any], str]:
    try:
        directory_only: list[str] = [
            entry for entry in os.listdir(folder_path) 
            if os.path.isdir(os.path.join(folder_path, entry)) and not entry.startswith('.')
        ]

        directory_buttons: list[Any] = []

        for directory in directory_only:
            y_pos: float = (directory_only.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])
                
        files_only: list[str] = [
            entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]


        files_only.sort(key=lambda entry: os.path.getctime(os.path.join(folder_path, entry)))

        file_buttons: list[Any] = []

        for file in files_only:
            y_pos = SCREEN_HEIGHT/2+(files_only.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2 - 30 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

        return directory_only, files_only, directory_buttons, file_buttons, folder_path
    except Exception as e:
        print("access denied:", e)
        print("reopening music")
        print("og:", og_folder)

        directory_only = [
            entry for entry in os.listdir(og_folder) 
            if os.path.isdir(os.path.join(og_folder, entry)) and not entry.startswith('.')
        ]

        directory_buttons = []

        for directory in directory_only:
            y_pos = (directory_only.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])

        files_only = [
            entry for entry in os.listdir(og_folder) if os.path.isfile(os.path.join(og_folder, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]

        files_only.sort(key=lambda entry: os.path.getctime(os.path.join(og_folder, entry)))

        file_buttons = []

        for file in files_only:
            y_pos = SCREEN_HEIGHT/2+(files_only.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

        return directory_only, files_only, directory_buttons, file_buttons, og_folder
    
def scroll_files_and_directories(dir_scroll: int, file_scroll: int, directory_buttons: list[Any], file_buttons: list[Any], SCREEN_HEIGHT: int, directories_only: list[str], files_only: list[str]) -> tuple[list[Any], list[Any]]:
    directory_buttons = []
    for directory in directories_only:
            y_pos: float = (directories_only.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])

    file_buttons = []
    for file in files_only:
            y_pos = SCREEN_HEIGHT/2+(files_only.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2+20 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

    return directory_buttons, file_buttons
    
def get_drives() -> list[Path]:
    if oper == "windows" or oper == "linux":
        partitions: list[Any] = psutil.disk_partitions(all=True)
        drives: list[Path] = []
        for p in partitions:
            drives.append(p.mountpoint)
        return drives
    
    drives = []
    volumes: Path = Path('/Volumes/')
    for drive in volumes.iterdir():
        drives.append(drive)
    
    return drives
    
def get_files(path: str, folder_type: bool = False) -> tuple[list[str], int, str] | list[str]:
    folder_path: str = ""
    if folder_type:
        folder_path = path
    else:
        folder_path: str = str(Path(path).parent)

    

    files: list[str] = [
        entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
    ]

    files.sort(key=lambda entry: os.path.getctime(os.path.join(folder_path, entry)))

    if not(folder_type):
        index: int = 0
        if oper == "windows":
            index: int = files.index(str(path).split("\\")[-1])
        else:
            index: int = files.index(str(path).split("/")[-1])
        return files, index, str(folder_path)
    else:
        return files
    
def search(files: list[str], query: str) -> list[str]:
    return [file for file in files if query.lower() in file.lower()]

def find_offset_to_file(selected_file: str, screen: Surface, files_only: list[str])  -> float:
    try:
        selected_file = search(files_only, selected_file)[0]
        song_index: int = files_only.index(selected_file)
        target_y: int = song_index * 40
        list_view_height: float = (screen.get_height() / 2) - 60

        file_scroll_target: float = target_y

        max_scroll: float = max(0, len(files_only) * 40 - list_view_height)
        return max(0, min(file_scroll_target, max_scroll))
    except:
        return 0