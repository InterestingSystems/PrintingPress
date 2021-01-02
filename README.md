# PrintingPress

A tool to place text and images onto a Pillow image object.

- [Installation](#Installation)
  - [Dependencies](#Dependencies)

- [Changelog](#Changelog)

- [Placements](#Placements)
  - [Introduction](#Introduction)
  - [Characteristics](#Characteristics)

- [Usage](#Usage)
  - [JSON Dictionary to Placements](#JSON-Dictionary-to-Placements)
  - [Python Dictionary to Placements](#Python-Dictionary-to-Placements)

- [Testing](#Testing)

- [Licenses](#Licenses)

## Installation

You can install PrintingPress via PyPI using the following command:

```bash
pip3 install iipp
```

### Dependencies

PrintingPress requires at minimum Pillow `8.0.0`.

## Changelog

### 1.2.0

- Major
  - Fast text fitting _(~900% faster, real world application performance increase slightly differs)_
  - Text clipping during rollover for one word text
  - Fix rollover causing clipping for certain texts

- Minor
  - Fixed `bg_opacity` and `font_opacity` independence

### 1.1.0

- Rework rollover method and fix ignored font descent issue

### 1.0.2

- Fix single word text fitting for image type Placement areas

## Placements

### Introduction

Operation with PrintingPress uses a dictionary called "Placements". Placements are made up of area dictionaries, which can be an `image` or `text` type. Within the area dictionaries are key and value pairs that describe the characteristics of the area.

**Image Type Placement Area Example**

```json
{
  "area0": {
    "type": "image",
    "path": "/path/to/image.png",

    "xy": [0, 0],
    "wh": [1920, 1080],
  }
}
```

_Note: In the context of a text type area, `wh` represents the size of the image. It is recommended to process the image externally. If the image's resolution differs from the given `wh` key value, it will be resized in order to meet the defined resolution._

**Text Type Placement Area Example**

```json
{
  "area1": {
    "type": "text",
    "path": "/path/to/font.ttf",
    "text": "hello world",

    "xy": [0, 0],
    "wh": [500, 500],

    "font_colour": [128, 0, 128],
    "font_size": 50,
    "font_variant": "Bold"
  }
}
```

_Note: In the context of a text type area, `wh` represents a box of which the text will be contained in. If the text exceeds the box, it will not be rendered outside of the given box defined by the `wh` key._

### Characteristics

- [type](#type)
- [path](#path)
- [text](#text)
- [xy](#xy)
- [wh](#wh)
- [filter](#filter)
- [filter_data](#filter_data)
- [font_colour](#font_colour)
- [font_size](#font_size)
- [font_variant](#font_variant)
- [font_opacity](#font_opacity)
- [bg_colour](#bg_colour)
- [bg_opacity](#bg_opacity)
- [fit](#fit)
- [opacity](#opacity)
- [rotation](#rotatiion)
- [beneath](#beneath)

---

#### type 

`str`: A string representing either `text` for text type areas, or `image` for image type areas

Example: `text`

---

#### path

`str`: A string representing the relative or absolute path to an image file or a font file supported by Pillow.

Example: `fonts/Manrope.ttf`

_Note: While constructing the dictionary in Python or after parsed by `json.load()`, the this can be set to a `PIL.Image.Image` object for image type areas._

---

#### text

**Specific to text type Placement areas**

`str`: A string representing the text that will be displayed on screen

---

#### xy

`list`: A list containing _two integers_ representing the X and Y coordinates of where the image/text will be placed in relative to the operation image.

Example: `[100, 100]`

---

#### wh

`list`: A list containing _two integers_ representing the pixel width and pixel height of the image for image type areas, while for text type areas it will represent the pixel width and pixel height of the textbox.

Example: `[100, 100]`

---

#### filter

**Specific to image type Placement areas**

`str` (Optional): A string representing the name of a filter.

Valid Options:

- `gaussian_blur`
- `box_blur`

---

#### filter_data

**Specific to image type Placement areas**

`list` (Optional): A list containing the appropriate data of the specified filter from `filter`.

- `gaussian_blur`: A one-item list containing the the blur radius in pixels.
- `box_blur`: A one-item list containing the the blur radius in pixels.

---

#### font_colour

**Specific to text type Placement areas**

`list` (Optional, Default: `[0, 0, 0]`): A three-item list containing integers representing an RGB color (Range 0-255).

Example: `[255, 0, 128]`

---

#### font_size

**Specific to text type Placement areas**

`int`: An integer representing the size of the font.

Example: `12`

---

#### font_variant

**Specific to text type Placement areas**

`str` (Optional): A string defining the variant of the font to use.

Example: `SemiBold`

Usually, you can find this out through your main graphic editing software, e.g. Adobe Illustrator - or, you can use the following code in a REPL:

```python
>>> from PIL import ImageFont
>>> font = ImageFont.truetype('tests/Manrope.ttf', 12)
>>> font.get_variation_names()
[b'ExtraLight', b'Light', b'Regular', b'Medium', b'SemiBold', b'Bold', b'ExtraBold']
```

---

#### font_opacity

**Specific to text type Placement areas**

`int` (Optional, Default: `255`): An integer representing the opacity of the text.

`0` represents full transparency.

Example: `128`

---

#### bg_colour

**Specific to text type Placement areas**

`list` (Optional, Default: `[0, 0, 0]`): A three-item list containing integers representing an RGB color (Range 0-255). This enable a background for the textbox, and will set it to the defined colour.

Example: `[255, 0, 128]`

---

#### bg_opacity

**Specific to text type Placement areas**

`int` (Optional, Default: `255`): An integer representing the opacity of the given textboc background, if a non-default bg_colour value was given. 

`0` represents full transparency.

Example: `128`

---

#### fit

**Specific to text type Placement areas**

`bool` (Optional, Default: `False`): A boolean specifying that if the text rolls over the given textbox, rather than an elipsis replacing the last visible character, PrintingPress programmatically finds the maximum font size for the text that would fit inside the textbox.

Example: `False`

_Note: This is currently extremely slow! Why? As of 1.1.0 - the way text fitting is done is that if the text does not fit the textbox, it will decrement the font size by 1. This is horribly inefficient - but I do not have the time nor knowledge to implement a better method. Contributions Welcome!_

---

#### opacity

**Specific to image type Placement areas**

`int` (Optional, Default: `255`): An integer representing the opacity of the image.

`0` represents full transparency.

Example: `128`

---

#### rotation

`int` (Optional, Default: `0`): An integer depicting desired counterclockwise rotation from center of image/textbox.

Example: `270`

---

#### beneath

`bool` (Optional, Default: `True`): A boolean depicting whether image/text will be placed be below operating image.

_Note: Operation on the operating image is sequential and based on the order of the areas given in the placements. Take note of this when ordering where an area with a `True` beneath key will be placed._

## Usage

### JSON Dictionary to Placements

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

### Python Dictionary to Placements

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

## Testing

When modifying PrintingPress, you may want to test certain aspects of the program.


### Default Suite

Currently there are two tests:

- `tests.ii.test`: More conventional rollover functionality testing using the interesting images Catalogue Entry Thumbnail and a portion of the placements found in [interestingimages/Format](https://github.com/interestingimages/Format)

- `tests.rollover.test`: Tests rollover functionality

### Running Tests

`python -c "import <test_import_path>"`

Replace `<test_import_path>` with any loaded test, such as `tests.ii.test`.

### Adding Tests

Adding tests are as simple as adding a folder containing a `test.py` file, and adding an import entry with the format of `from . import <folder_name>` into `tests/__init__.py`.

_Note: When making placements and/or the test script itself, either make an effort to use `pathlib` and append the test script's parent directort to all paths used in the test, or use paths relative to the root folder of the repository._

## Licenses

### PrintingPress

PrintingPress is licensed under the **MIT License**.
([File](https://github.com/interestingimages/PrintingPress/blob/master/LICENSE) / 
[OSI](https://opensource.org/licenses/MIT))

### manrope

manrope, located in `fonts/Manrope.ttf`, is licensed under the **Open Font License**.

```
Copyright 2018 The Manrope Project Authors (https://github.com/sharanda/manrope)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
http://scripts.sil.org/OFL


-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded, 
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply
to any document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components as
distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to a
new environment.

"Author" refers to any designer, engineer, programmer, technical
writer or other person who contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.
```
