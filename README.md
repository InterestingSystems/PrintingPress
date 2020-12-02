# PrintingPress

A tool to place text and images onto a Pillow image object.

## Installation

You can install PrintingPress via PyPI using the following command:

```bash
pip3 install iipp
```

### Dependencies

PrintingPress uses Pillow, with the minimum version officially supported being `7.0.0`.

###### Compatibility for Pillow versions under `7.0.0` is not guaranteed, but you are free to try using --no-deps when installing.

## Changelog

### 1.0.2

- Fix single word text fitting for image type Placement areas

### 1.0.1

- Fix Pillow dependency version

- Fix handling of PIL Image paths for image type Placement areas

- Fix handling of Placement areas named ".meta"

### 1.0.0

- Fix image opacity related issues

- Add a fit option in Placements to fit text

## Usage

### Using placements from a JSON File

```python
from PIL import Image
import PrintingPress
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
import PrintingPress

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

PrintingPress is licensed under then **MIT License**.
([File](https://github.com/interestingimages/PrintingPress/blob/master/LICENSE) / 
[OSI](https://opensource.org/licenses/MIT))
