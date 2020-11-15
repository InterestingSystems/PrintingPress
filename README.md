# PrintingPress

A tool to place text and images onto a Pillow image object.

## Installation

You can use Pillow `~7.0.0` ([PyPi](https://pypi.org/project/Pillow/) / [Docs](https://pillow.readthedocs.io) / [Website](https://python-pillow.org/)
or the latest version of Pillow-SIMD, `7.0.0post3`. ([PyPi](https://pypi.org/project/Pillow-SIMD) / [GitHub](https://github.com/uploadcare/pillow-simd))

Tested Pillow variants:
- Pillow 8.0.1
- Pillow-SIMD 7.0.0post3

###### If you have a different version of Pillow and were able to use PrintingPress with no issues - please open an issue with describing your variant and version.

If using **Pillow-SIMD** / **PyPy 3.7x** / **building Pillow from scratch**, make sure you have the following prerequistes:
- Debian-based Systems / WSL
  - libjpeg-dev
  - zlib1g-dev
  - libfreetype6-dev (For Text Functionality)

###### Other distros may also need the following dependencies, but I mainly use Debian. If you ended up requiring extra dependencies, open an issue.

## Usage

```python
from PIL import Image
import PrintingPress

# Parse Placements (From JSON file)
import json

with open('placements.json', 'r', encoding='utf-8') as pf:
    placements_json = json.load(pf)
    
# Parse Placements (From dictionary)
placements_py = {
  "area0_image_test": {
    "type": "image",
    "path": "/path/to/image.png",
    "xy": [50, 50],
    "wh": [400, 400],
  },

  "area1_text_test": {
    "type": "text",
    "path": "/path/to/bahnschrift.ttf",
    "text": "Hello Image",
    "xy": [50, 50],
    "wh": [400, 400],
    "font_size": 8,
    "font_variant": "SemiBold Condensed",
    "font_opacity": 76,
  }
}

placements = PrintingPress.Placements.parse(placements_py)
placements = PrintingPress.Placements.parse(placements_json)

# Operate on target file
image = Image.open('base_image.png').convert('RGBA')  # conversion to RGBA is required
output = PrintingPress.operate(image=Image.open('base_image.png'),
                               placements=placements)

# Save the output file
output.save('output.png')
```
