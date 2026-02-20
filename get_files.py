import os
from platformdirs import user_music_dir
from pathlib import Path

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

        supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg'] #, '.m4a']
        FILES_ONLY = [
            entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]

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

        supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg'] #, '.m4a']
        FILES_ONLY = [
            entry for entry in os.listdir(og_folder) if os.path.isfile(os.path.join(og_folder, entry)) and os.path.splitext(entry)[1].lower() in supported_formats and not(entry[0] == ".")
        ]

        file_buttons = []

        for file in FILES_ONLY:
            y_pos = SCREEN_HEIGHT/2+(FILES_ONLY.index(file)+1)*40 + 10 - file_scroll
            if SCREEN_HEIGHT/2 - 30 < y_pos < SCREEN_HEIGHT:  # Only include visible items
                file_buttons.append([y_pos, file])

        return DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder
        
