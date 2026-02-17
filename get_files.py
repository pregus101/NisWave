import os

def get_music_files_and_directories(folder_path, SCREEN_HEIGHT):
    DIRECTORY_ONLY = [
        entry for entry in os.listdir(folder_path) 
        if os.path.isdir(os.path.join(folder_path, entry)) and not entry.startswith('.')
    ]

    directory_buttons = []

    for directory in DIRECTORY_ONLY:
        directory_buttons.append([(DIRECTORY_ONLY.index(directory)+1)*40 + 10, directory])

    supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
    FILES_ONLY = [
        entry for entry in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats
    ]

    file_buttons = []

    for file in FILES_ONLY:
        file_buttons.append([SCREEN_HEIGHT/2+(FILES_ONLY.index(file)+1)*40 + 10, file])

    return DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons
