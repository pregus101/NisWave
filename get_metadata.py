import os
from pathlib import Path
from PIL.ImageFile import ImageFile
from mutagen.mp4 import MP4
from mutagen.id3 import APIC # type: ignore
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from PIL import Image
import shutil
from mutagen import File as MutagenFile # type: ignore
from typing import Any
from numpy import cov # type: ignore
from pygame import Surface

def reSize(path: Path, size: int) -> list[int]:
    img: ImageFile = Image.open(path)

    width: int
    height: int
    width, height = img.size

    img.resize((int(width*(size/height)), size), Image.Resampling.LANCZOS).save(path)

    return (int(width*(size/height)), size)

class image_get:
    def __init__(self, screen: Surface, size: int, output_dir: Path = Path(os.path.join(os.path.dirname(__file__), "main_cover_art/")), typeOf: str = "cover") -> None:
        self.screen: Surface = screen
        self.size: int = size
        self.output_dir: Path = output_dir
        self.typeOf: str = typeOf
        self.screen_width: int
        self.screen_height: int
        self.screen_width, self.screen_height = self.screen.get_size()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        shutil.copy(os.path.join(os.path.dirname(__file__), "assets/default_cover.jpg"), os.path.join(os.path.dirname(__file__), "main_cover_art/"))
        self.old_image: Path = Path(os.path.join(os.path.dirname(__file__), "main_cover_art/default_cover.jpg"))
        self.file_path: Path = Path(os.path.join(os.path.dirname(__file__), "main_cover_art/default_cover.jpg"))

    def default_cover(self, file_path: Path) -> tuple[tuple[int, int], Path]:
        if Path(self.old_image).is_file():
            os.remove(self.old_image)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        shutil.copy(os.path.join(os.path.dirname(__file__), "assets/default_cover.jpg"), os.path.join(os.path.dirname(__file__), "main_cover_art/"))

        return_path: Path = Path(os.path.join(os.path.dirname(__file__), "main_cover_art/default_cover.jpg"))

        renSize: list[int] = reSize(return_path, self.size)

        self.old_image = return_path

        print(return_path)

        self.file_path = file_path

        return [renSize[0], renSize[1]], return_path

    def update_image(self, file_path: Path = Path("")) -> tuple[list[int], Path]:
        if Path(file_path).is_file():
            if Path(self.old_image).is_file():
                os.remove(self.old_image)

            skip = False
            
            if Path(file_path).is_file():
                if str(file_path).lower().endswith('.m4a'):
                    file: Any | None = MP4(file_path)
                
                elif str(file_path).lower().endswith('.mp3'):
                    try:
                        file: Any | None = MutagenFile(file_path) # type: ignore
                    except:
                        skip = True
                        file: Any | None = None
                elif str(file_path).lower().endswith('.flac'):
                    file: Any | None = FLAC(file_path)
                else:
                    skip = True
                    file: Any | None = None
            else:
                skip = True
                file: Any | None = None


            if not skip and file and file.tags: # type: ignore
                if str(file_path).lower().endswith('.m4a'):
                    if 'covr' in file.tags: # type: ignore
                        image_data: bytes = file.tags["covr"][0] # type: ignore
                        
                        track_title = os.path.basename(file_path)[:-4]
                        return_path = Path(os.path.join(os.path.dirname(__file__), f"main_cover_art/{track_title.replace('/', '_')}_{self.typeOf}.png"))

                        with open(return_path, "wb") as f:
                            f.write(image_data) # type: ignore
                        print("Image extracted successfully.")

                        renSize: list[int] = reSize(return_path, self.size)

                        self.old_image = return_path

                        self.file_path = file_path

                        return renSize, return_path
                elif str(file_path).lower().endswith('.flac'):

                    track_title = os.path.basename(file_path)[:-4]
                    return_path = Path(os.path.join(os.path.dirname(__file__), f"main_cover_art/{track_title.replace('/', '_')}_{self.typeOf}.png"))
                    
                    for picture in file.pictures: # type: ignore
                        with open(return_path, 'wb') as f:
                            f.write(picture.data) # type: ignore
                        print(f"Thumbnail saved: {picture.mime}") # type: ignore

                    renSize: list[int] = reSize(return_path, self.size)

                    self.old_image = return_path

                    self.file_path = file_path

                    return renSize, return_path

                try:
                    for tag in file.tags.getall('APIC'): # type: ignore
                        print("debug3")
                        if isinstance(tag, APIC):
                            if not os.path.exists(self.output_dir):
                                os.makedirs(self.output_dir)
                            if tag.mime == 'image/jpeg': # type: ignore
                                ext = 'jpg'
                            elif tag.mime == 'image/png': # type: ignore
                                ext = 'png'
                            else:
                                print(f"Unsupported image mime type: {tag.mime}") # type: ignore
                                continue
                            
                            track_title: str = os.path.basename(file_path)[:-4]
                            return_path: Path = Path(os.path.join(os.path.dirname(__file__), f"main_cover_art/{track_title.replace('/', '_')}_{self.typeOf}.{ext}"))

                            with open(return_path, 'wb') as img_file:
                                img_file.write(tag.data) # type: ignore
                            
                            print(f"Successfully extracted cover art to: {return_path}")

                            renSize: list[int] = reSize(return_path, self.size)

                            self.old_image = return_path

                            self.file_path = file_path

                            return renSize, return_path
                except:
                    return self.default_cover(file_path)
                    
            else:
                return self.default_cover(file_path)
                
        return self.default_cover(file_path)

    def update_size(self, is_custom_size: bool=False, custom_size: int = 640) -> tuple[list[int], Path]:
        if is_custom_size:
            self.size = custom_size
        
        self.screen_width, self.screen_height = self.screen.get_size()
        self.size = int(640 * ((self.screen_width/1920 + self.screen_height/1147) / 2))
        
        render_size: list[int]
        cover_art_path: Path
        
        render_size, cover_art_path =  self.update_image(self.file_path)

        return render_size, cover_art_path

def get_artist(file_path: str) -> str:
    try:
        if file_path.lower().endswith('.m4a'):
            audio: Any = MP4(file_path)
            return str(audio.tags.get('\xa9ART', ['Unknown Artist'])[0])
        elif file_path.lower().endswith('.mp3'):
            audio = EasyID3(file_path)
            return str(audio.get('artist', ['Unknown Artist'])[0])
        elif file_path.lower().endswith('.flac'):
            print(file_path)
            audio = FLAC(file_path)
            return str(audio.get('artist', ['Unknown Artist'])[0])
        elif file_path.lower().endswith('.wav'):
            audio = WAVE(file_path)
            artist: str = audio.get('artist', ['Unknown Artist'])[0]
            return str(artist)
        else:
            return "Unknown Artist"
    except:
        return "Unknown Artist"
