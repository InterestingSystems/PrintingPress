# PrintingPress

A tool to place text and images onto a Pillow image object.

## Installation

You can use Pillow `~7.0.0` ([PyPi](https://pypi.org/project/Pillow/) / [Docs](https://pillow.readthedocs.io) / [Website](https://python-pillow.org/)
or the latest version of Pillow-SIMD, `7.0.0post3`. ([PyPi](https://pypi.org/project/Pillow-SIMD) / [GitHub](https://github.com/uploadcare/pillow-simd))

Support for Pillow-SIMD is active, so if you encounter issues with Pillow - you should try using an earlier version closer to `7.0.0`.

## Usage

```python
from PIL import Image
import printingpress

# Parse Placements (From JSON file)
import json

with open('placements.json', 'r', encoding='utf-8') as pf:
    placements = iipp.Placements(json.load(pf))
    
# Parse Placements (From dictionary)
placements = iipp.Placements.parse({
  "area0": {
    "type": "image",
    "path": "image.png",
    "xy": [0, 0],
    "wh": [0, 0],
    "colour": [0, 0, 0],
    "opacity": 0,
    "rotation": 0
  },
  "area1": {
    "type": "text",
    "path": "bahnschrift.ttf",
    "xy": [0, 0],
    "wh": [0, 0],
    "font_colour": [0, 0, 0],
    "font_size": 12,
    "font_variant": "SemiBold Condensed",
    "colour": [0, 0, 0],
    "opacity": 0,
    "rotation": 0
  }
})

# Operate on target file
image = Image.open('base_image.png').convert('RGBA')  # conversion to RGBA is required
output = iipp.PrintingPress.operate(Image.open('base_image.png'))

# Save the output file
output.save('output.png')
```
