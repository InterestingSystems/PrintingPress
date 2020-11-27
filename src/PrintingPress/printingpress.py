# PrintingPress, by hysrx

from PIL import Image, ImageFont, ImageDraw, ImageFilter
from collections import namedtuple
from pathlib import Path


class Internals:
    def print_if(message: str = '', end: str = '\n', condition: bool = True) -> None:
        print(message, end=end) if condition else None

    def format_message(message: str, format_map: dict) -> str:
        for key, value in format_map.items():
            message = message.replace(key, str(value))
        return message

    def retrieve_key(target: dict, key: str, expected: type, required: bool = True,
                     fallback=None, extra: str = '',
                     expected_message: str = 'key f:key is type f:type, but expected f:extype',
                     required_message: str = 'key f:key is required'):
        # Formats all formattable words into their representated.
        message_formatting_map = {
            'f:key': key,
            'f:extype': expected,
            'f:type': None,  # this is manipulated later
            'f:extra': extra
        }

        try:
            retrieved = target[key]

        except KeyError:
            if required:
                raise KeyError(Internals.format_message(required_message,
                                                        message_formatting_map))
            else:
                return fallback

        else:
            if isinstance(retrieved, expected) is False:
                message_formatting_map['f:type'] = str(type(retrieved))
                raise TypeError(Internals.format_message(expected_message,
                                                         message_formatting_map))

            return retrieved

    def rgb_list_check(area_name: str, elem_name: str, target: list) -> None:
        assert len(target) == 3, f'Area {area_name}: key {elem_name} has {len(target)} values (expected 3)'  # noqa: E501

        for elem in target:
            assert elem < 256, f'Area {area_name}: key {elem_name} has values that exceed 255'
    
    def filter_list_check(area_name: str, filter_name: str, target: list) -> None:
        filter_map = {
            'gaussian_blur': [int],
            'box_blur': [int]
        }
        
        filter_target_mapping = filter_map[filter_name]

        # Check list lengths
        assert len(filter_target_mapping) == len(target), f'Area {area_name}: key filter_data has {len(target)} values (expected {len(filter_target_mapping)})'  # noqa: E501

        for expected, actual in zip(filter_target_mapping, target):
            assert isinstance(actual, expected), f'Area {area_name}: key filter_data has values with unexpected types'  # noqa: E501

class Placements:
    __parse_map__ = {
        # Argument Format: [expected (type), required (bool), fallback (*)]
        'image': {
            'type': None,

            'path': [(str, Image.Image), True, None],

            'xy': [list, True, None],
            "wh": [list, False, None],

            'filter': [str, False, None],
            'filter_data': [list, False, []],

            'opacity': [int, False, 255],
            'rotation': [int, False, 0],

            'image': None
        },

        'text': {
            'type': None,

            'path': [str, True, None],
            'text': [str, True, None],

            'xy': [list, True, None],
            'wh': [list, True, None],

            'bg_colour': [list, False, [0, 0, 0]],
            'bg_opacity': [int, False, 255],

            'font_colour': [list, False, [255, 255, 255]],
            'font_size': [int, True, None],
            'font_variant': [str, False, None],
            'font_opacity': [int, False, 255],

            'rotation': [int, False, 0],
            'beneath': [bool, False, False],
            'font': None
        }
    }

    __imagearea__ = namedtuple('ImageArea', __parse_map__['image'])
    __textarea__ = namedtuple('TextArea', __parse_map__['text'])

    def parse(places: dict) -> dict:
        assert isinstance(places, dict), 'Non-dictionary passed in'

        # Skips .meta
        parsed_places = places.pop('.meta') if '.meta' in places else {}

        for area_name, area_data in places.items():
            parsed_area = {}

            parsed_area['type'] = Internals.retrieve_key(target=area_data, key='type', expected=str,
                                                         required=True, extra=f' (area {area_name})')

            # Asserts if parsed_area['type'] is not image or text
            assert any([parsed_area['type'] == 'image', parsed_area['type'] == 'text']), f'Area {area_name}: key type has to be "image" or "text", not "{parsed_area["type"]}"'  # noqa: E501

            # Loops through the area-specific mapping and does type/availability checks
            for elem, payload in Placements.__parse_map__[parsed_area['type']].items():
                if payload is not None:
                    retrieved = Internals.retrieve_key(target=area_data, key=elem,
                                                       expected=payload[0],
                                                       required=payload[1],
                                                       fallback=payload[2],
                                                       extra=f' (area {area_name})')

                    if 'colour' in elem:
                        Internals.rgb_list_check(area_name=area_name,
                                                 elem_name=elem,
                                                 target=retrieved)

                    if elem == 'rotation' and retrieved > 360:
                        retrieved = 360

                    if 'opacity' in elem and retrieved > 255:
                        retrieved = 255

                    if elem == 'path':
                        retrieved = Path(retrieved).absolute()

                    if elem == 'xy' or elem == 'wh':
                        assert len(retrieved) == 2, f'Area {area_name}: key {elem} has {len(retrieved)} values (expected 2)'  # noqa: E501

                    parsed_area[elem] = retrieved

            if parsed_area['type'] == 'text':  # Text-specific post-parse operations
                assert parsed_area['path'].is_file(), f'Area {area_name}: key path has to be an existant file'  # noqa: E501

                # Create PIL Font Object
                font = ImageFont.FreeTypeFont(font=str(parsed_area['path']),
                                              size=parsed_area['font_size'])

                # Retrieve font_variant key value
                font_variant = Internals.retrieve_key(target=parsed_area, key='font_variant',
                                                      expected=(str, type(None)), fallback=None)

                # Attempt to set font_variant
                if font_variant is not None:
                    try:
                        font.set_variation_by_name(bytes(font_variant, 'utf-8'))
                    except Exception as e:
                        print(f'Area: {area_name}: font_variant is invalid, continuing. ({e})')

                # Add font into parsed_area
                parsed_area['font'] = font

                parsed_places[area_name] = Placements.__textarea__(**parsed_area)  # Create namedtuple

            else:  # Image-specific post-parse operations
                if isinstance(parsed_area['path'], Image.Image):
                    # Users can pass PIL Images into the path key if constructing a placement
                    # dictionary in Python rather than from a JSON file. So, if this happens
                    # just use the image from the path key.
                    parsed_area['image'] = parsed_area['path']

                else:
                    assert parsed_area['path'].is_file(), f'Area {area_name}: key path has to be an existant file'  # noqa: E501

                    # Else, create a PIL Image Object from the path given
                    parsed_area['image'] = Image.open(parsed_area['path']).convert("RGBA")

                if str(parsed_area['filter']) not in ['gaussian_blur', 'box_blur']:
                    parsed_area['filter'] = None
                
                else:
                    Internals.filter_list_check(area_name=area_name,
                                                filter_name=parsed_area['filter'],
                                                target=parsed_area['filter_data'])

                parsed_places[area_name] = Placements.__imagearea__(**parsed_area)  # Create namedtuple

        return parsed_places


def operate(image: Image.Image, placements: dict, suppress: bool = False) -> Image.Image:
    def rollover(text: str, area_name, font, drawer, wh: list) -> str:
        # Based on: https://stackoverflow.com/a/62418837
        max_width, max_height = wh

        words = len(text.split())
        lines = [[]]
        current = lambda: '\n'.join([' '.join(line) for line in lines])  # noqa: E731

        w0, h0 = 0, 0

        for word in text.split():
            # Insert word and measure
            lines[-1].append(word)
            w, h = drawer.multiline_textsize(current(), font=font)

            if w > max_width:  # Too wide, roll over text.
                # Move first line to second line (too wide) and measure
                lines.append([lines[-1].pop()])
                w0, h0 = w, h = drawer.multiline_textsize(current(), font=font)

                if h > max_height:  # Rolled over text is too high.
                    if words == 1:  # Check if theres only one word.
                        lines.pop()
                        lines[-1] = '…'

                    else:
                        lines.pop()
                        lines[-1][-1] += '…'

                        # Cycle through text to find last word short enough to add elipsis
                        while drawer.multiline_textsize(current(), font=font)[0] > max_width:
                            lines[-1].pop()
                            lines[-1][-1] += '…'

                        break

        if words == 1 and any([w0 > max_width, h0 > max_width]):
            tw, th = drawer.multiline_textsize(text, font=font)
            print(f'Warning: Area "{area_name}" has a single word that overflows the given box. (Box: {wh}, Text: {tw, th})')  # noqa: E501

        return current()

    assert isinstance(image, Image.Image), 'Passed image parameter is not a PIL Image'

    if 'A' not in image.mode:
        image = image.convert('RGBA')

    suppress = not suppress  # negate for condition in Internals.print_if

    for area_name, area_data in placements.items():
        Internals.print_if(f'\nOperating on area {area_name}. ({area_data.type})',
                           condition=suppress)

        if area_data.type == 'text':  # Text-based operation
            # Subimage creation
            Internals.print_if('  Creating subimage...', end='\r', condition=suppress)
            subimage = Image.new(mode='RGBA',
                                 size=tuple(area_data.wh),
                                 color=(area_data.bg_opacity,) + tuple(area_data.bg_colour))
            Internals.print_if('  Creating subimage... DONE', condition=suppress)

            # Make ImageDraw.Draw
            Internals.print_if('  Making drawer...', end='\r', condition=suppress)
            drawer = ImageDraw.Draw(subimage)
            Internals.print_if('  Making drawer... DONE', condition=suppress)

            # Calculate Rollover
            Internals.print_if('  Calculating rollover...', end='\r', condition=suppress)
            text = rollover(text=area_data.text,
                            area_name=area_name,
                            font=area_data.font,
                            drawer=drawer,
                            wh=area_data.wh)
            Internals.print_if('  Calculating rollover... DONE', condition=suppress)

            # Draw Text
            Internals.print_if('  Drawing text...', end='\r', condition=suppress)

            fill = area_data.font_colour.copy()
            fill.append(area_data.font_opacity)

            drawer.text(xy=(0, 0),
                        text=text,
                        fill=tuple(fill),
                        font=area_data.font)
            Internals.print_if('  Drawing text... DONE', condition=suppress)

            # Rotate subimage
            Internals.print_if('  Rotating subimage...', end='\r', condition=suppress)
            subimage = subimage.rotate(area_data.rotation, expand=True)
            Internals.print_if('  Rotating subimage... DONE', end='\r', condition=suppress)

            # Press subimage onto image
            Internals.print_if('  Pressing subimage into image...', end='\r', condition=suppress)

            # A holder image is neccesary as just pasting, if the subimage is transparent,
            # image becomes transparent as well.
            holder = Image.new('RGBA', image.size)
            holder.paste(im=subimage, box=tuple(area_data.xy), mask=subimage)
            if area_data.beneath:
                image = Image.alpha_composite(holder, image)
            else:
                image = Image.alpha_composite(image, holder)

            Internals.print_if('  Pressing subimage into image... DONE', condition=suppress)

        else:  # Image-based operation
            if area_data.wh is not None:
                # Resize Image
                Internals.print_if('  Resizing image...', end='\r', condition=suppress)
                area_image = area_data.image.resize(area_data.wh)
                Internals.print_if('  Resizing image... DONE', condition=suppress)

            else:
                area_image = area_data.image.copy()
            
            if area_data.filter is not None:  # Filter Application
                Internals.print_if('  Applying filter to image...', end='\r', condition=suppress)

                # Gaussian Blur
                if area_data.filter == 'gaussian_blur':
                    # filter_data = [radius]
                    area_image = area_image.filter(ImageFilter.GaussianBlur(area_data.filter_data[0]))
                
                elif area_data.filter == 'box_blur':
                    # filter_data = [radius]
                    area_image = area_image.filter(ImageFilter.BoxBlur(area_data.filter_data[0]))

                Internals.print_if('  Applying filter to image... DONE', condition=suppress)

            Internals.print_if('  Adjusting image...', end='\r', condition=suppress)
            # Change Image Opacity
            area_image.putalpha(area_data.opacity)

            # Rotate Image
            area_image = area_image.rotate(area_data.rotation, expand=True)
            Internals.print_if('  Adjusting image... DONE', condition=suppress)

            # Paste Image
            Internals.print_if('  Pasting image onto target...', end='\r', condition=suppress)
            if area_data.beneath:
                # A holder is required as the area image needs to be positioned relative
                # to image's dimensions which is not possible merely a paste.
                holder = Image.new(mode='RGBA', size=image.size)
                holder.paste(im=area_image, box=tuple(area_data.xy))
                image = holder.paste(im=image, box=tuple(area_data.xy))
            else:
                image.paste(im=area_image, box=tuple(area_data.xy))
            Internals.print_if('  Pasting image onto target... DONE', condition=suppress)

        Internals.print_if('  All operations complete.', condition=suppress)

    return image
