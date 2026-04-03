import re
import sys

def extract_pixel_filenames():
    # Regex pattern for PXL_YYYYMMDD_HHMMSSmmm.ext
    # Handles .jpg and .mp4 specifically
    pixel_regex = re.compile(r'PXL_\d{8}_\d{9}\.(?:jpg|mp4)', re.IGNORECASE)

    # Read from standard input
    for line in sys.stdin:
        matches = pixel_regex.findall(line)
        for match in matches:
            print(match)

if __name__ == "__main__":
    try:
        extract_pixel_filenames()
    except KeyboardInterrupt:
        sys.exit(0)
        
