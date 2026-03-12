import os
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from PIL import Image
import pygame
import shutil
from mutagen import File as MutagenFile

def reSize(path, size):
    img = Image.open(path)

    width, height = img.size

    img = img.resize((int(width*(size/height)), size), Image.Resampling.LANCZOS)

    img.save(path)

    return [int(width*(size/height)), size]

class image_get:
    def __init__(self, screen, size, output_dir=os.path.join(os.path.dirname(__file__), "main_cover_art/"), typeOf="cover"):
        self.screen = screen
        self.size = size
        self.output_dir = output_dir
        self.typeOf = typeOf
        self.screen_width, self.screen_height = self.screen.get_size()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        shutil.copy(os.path.join(os.path.dirname(__file__), "assets/default_cover.jpg"), os.path.join(os.path.dirname(__file__), "main_cover_art/"))
        self.old_image = os.path.join(os.path.dirname(__file__), "main_cover_art/default_cover.jpg")
        self.file_path = os.path.join(os.path.dirname(__file__), "main_cover_art/default_cover.jpg")

    def update_image(self, file_path):
        if Path(file_path).is_file():
            if Path(self.old_image).is_file():
                os.remove(self.old_image)

            skip = False
            
            if Path(file_path).is_file():
                file = MutagenFile(file_path)
            else:
                skip = True
                file = None

            if file and file.tags and not skip:
                for tag in file.tags.getall('APIC'):
                    print("debug3")
                    if isinstance(tag, APIC):
                        if not os.path.exists(self.output_dir):
                            os.makedirs(self.output_dir)
                        if tag.mime == 'image/jpeg':
                            ext = 'jpg'
                        elif tag.mime == 'image/png':
                            ext = 'png'
                        else:
                            print(f"Unsupported image mime type: {tag.mime}")
                            continue
                        
                        track_title = os.path.basename(file_path)[:-4]
                        return_path = os.path.join(os.path.dirname(__file__), f"main_cover_art/{track_title.replace('/', '_')}_{self.typeOf}.{ext}")

                        with open(return_path, 'wb') as img_file:
                            img_file.write(tag.data)
                        
                        print(f"Successfully extracted cover art to: {return_path}")

                        renSize = reSize(return_path, self.size)

                        self.old_image = return_path

                        self.file_path = file_path

                        return renSize, return_path
                    
            else:
                if Path(self.old_image).is_file():
                    os.remove(self.old_image)

                if not os.path.exists(self.output_dir):
                    os.makedirs(self.output_dir)

                shutil.copy(os.path.join(os.path.dirname(__file__), "assets/default_cover.jpg"), os.path.join(os.path.dirname(__file__), "main_cover_art/"))

                return_path = os.path.join(os.path.dirname(__file__), "main_cover_art/default_cover.jpg")

                renSize = reSize(return_path, self.size)

                self.old_image = return_path

                print(return_path)

                self.file_path = file_path

                print("returning")

                return [self.size, self.size], return_path
            
        return [self.size, self.size], self.old_image



    def update_size(self, is_custom_size=False, custom_size = 640):
        if is_custom_size:
            self.size = custom_size
        
        self.screen_width, self.screen_height = self.screen.get_size()
        self.size = int(640 * ((self.screen_width/1920 + self.screen_height/1147) / 2))
        
        render_size, cover_art_path =  self.update_image(self.file_path)

        return render_size, cover_art_path
    
def get_artist(mp3_file_path):
    # Load the MP3 file with mutagen
    try:
        audio = EasyID3(mp3_file_path)
        return audio.get('artist', ['Unknown Artist'])[0]
    except:
        return 'Unknown Artist'
