import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

def get_cover_art(mp3_file_path, size=640, output_dir=os.path.join(os.path.dirname(__file__), "temp_cover_art")):
    """
    Extracts the cover art from an MP3 file using the mutagen library.
    """

    print(mp3_file_path, output_dir)

    try:
        # Load the MP3 file with mutagen
        audio = MP3(mp3_file_path)
        
        # Check if there are any ID3 tags
        if not audio.tags:
            print(f"No ID3 tags found in {mp3_file_path}")
            return

        # Iterate over the tags to find the album art (APIC tag)
        for tag in audio.tags.getall('APIC'):
            if isinstance(tag, APIC):
                # Ensure the output directory exists
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Determine file extension based on image mime type
                if tag.mime == 'image/jpeg':
                    ext = 'jpg'
                elif tag.mime == 'image/png':
                    ext = 'png'
                else:
                    print(f"Unsupported image mime type: {tag.mime}")
                    continue
                
                # Create the output filename
                track_title = audio.get('TIT2', ['temp'])[0]
                output_filename = f"{track_title.replace('/', '_')}_cover.{ext}"
                output_path = os.path.join(output_dir, output_filename)

                # Write the image data to a file
                with open(output_path, 'wb') as img_file:
                    img_file.write(tag.data)
                
                print(f"Successfully extracted cover art to: {output_path}")

                img = Image.open(output_path)

                width, height = img.size

                img = img.resize((int(width*(size/height)), size), Image.Resampling.LANCZOS)

                img.save(output_path)

                return int(width*(size/height)), size # Stop after the first image is found
        
        print(f"No cover art (APIC tag) found in {mp3_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

        return 640, 640