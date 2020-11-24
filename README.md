# PrintingPress

A tool to place text and images onto a Pillow image object.

## Installation

```bash
pip3 install isPrintingPress
```

## Usage

### Using placements from a JSON File

```python
from PIL import Image
import printingpress
import json

# Parse Placements (From JSON file)
with open('placements.json', 'r', encoding='utf-8') as pf:
    placements = json.load(pf)

placements = PrintingPress.Placements.parse(placements)

# Operate on target file
image = Image.open('base_image.png').convert('RGBA')  # conversion to RGBA is required
output = PrintingPress.operate(image=Image.open('base_image.png'),
                               placements=placements)

# Save the output file
output.save('output.png')
```

### Using placements from a Python Dictionary

```python
from PIL import Image
import printingpress

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

# Operate on target file
image = Image.open('base_image.png').convert('RGBA')  # conversion to RGBA is required
output = PrintingPress.operate(image=Image.open('base_image.png'),
                               placements=placements)

# Save the output file
output.save('output.png')
```

## Licenses

### PrintingPress
PrintingPress, by itself, is licensed under then **MIT License**.
([File](https://github.com/InterestingSystems/PrintingPress/blob/master/LICENSE) / [OSI](https://opensource.org/licenses/MIT))

### Anybody
For testing, Etcetera Type Co's Anybody font is used for testing variable font support.

The font is licensed under the **SIL Open Font License 1.1**, and is included alongside the TrueType font file under the
`/tests/` folder.
([File](https://github.com/InterestingSystems/PrintingPress/blob/master/tests/SIL.txt) / [OSI](https://opensource.org/licenses/OFL-1.1))
