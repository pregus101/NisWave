import os
from pathlib import Path
import psutil
import sys
import subprocess
import shutil

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

def get_music_files_and_directories(folder_path: str, SCREEN_HEIGHT: int, og_folder: str, dir_scroll: int = 0, file_scroll: int = 0) -> list[list[str], list[str], list[int, str], list[int, str], str]:
    try:
        DIRECTORY_ONLY: list[str] = [
            entry for entry in os.listdir(folder_path) 
            if os.path.isdir(os.path.join(folder_path, entry)) and not entry.startswith('.')
        ]

        directory_buttons: list[int, str] = []

        for directory in DIRECTORY_ONLY:
            y_pos: int = (DIRECTORY_ONLY.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])
                
        FILES_ONLY: list[str] = [
            entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]


        FILES_ONLY.sort(key=lambda entry: os.path.getctime(os.path.join(folder_path, entry)))

        file_buttons: list[int, str] = []

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

        directory_buttons: list = []

        for directory in DIRECTORY_ONLY:
            y_pos = (DIRECTORY_ONLY.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])

        FILES_ONLY: list[str] = [
            entry for entry in os.listdir(og_folder) if os.path.isfile(os.path.join(og_folder, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]

        FILES_ONLY.sort(key=lambda entry: os.path.getctime(os.path.join(og_folder, entry)))

        file_buttons: list[str] = []

        for file in FILES_ONLY:
            y_pos = SCREEN_HEIGHT/2+(FILES_ONLY.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

        return DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder
    
def scroll_files_and_directories(dir_scroll: int, file_scroll: int, directory_buttons: list, file_buttons: list, SCREEN_HEIGHT: int, directories_only: list, files_only: list) -> tuple[list, list]:
    directory_buttons = []
    for directory in directories_only:
            y_pos = (directories_only.index(directory)+1)*40 + 10 - dir_scroll
            if -30 < y_pos < SCREEN_HEIGHT/2:  # Only include visible items
                directory_buttons.append([y_pos, directory])

    file_buttons = []
    for file in files_only:
            y_pos = SCREEN_HEIGHT/2+(files_only.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2+20 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

    return directory_buttons, file_buttons
    
def get_drives() -> list:
    if oper == "windows" or oper == "linux":
        partitions: list[str] = psutil.disk_partitions(all=True)
        drives: list[str] = []
        for p in partitions:
            drives.append(p.mountpoint)
        return drives
    
    drives: list[str] = []
    volumes: path = Path('/Volumes/')
    for drive in volumes.iterdir():
        drives.append(drive)
    
    return drives
    
def get_files(path: str, folder_type: bool = False) -> list:
    folder_path: str = ""
    if folder_type:
        folder_type = path
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
    
def search(files: list[str], query: str) -> list:
    return [file for file in files if query.lower() in file.lower()]

def find_offset_to_file(selected_file, screen, FILES_ONLY)  -> int:
    try:
        selected_file: str = search(FILES_ONLY, selected_file)[0]
        song_index: int = FILES_ONLY.index(selected_file)
        target_y: int = song_index * 40
        list_view_height: int = (screen.get_height() / 2) - 60

        file_scroll_target: str = target_y

        max_scroll: int = max(0, len(FILES_ONLY) * 40 - list_view_height)
        return max(0, min(file_scroll_target, max_scroll))
    except:
        return 0