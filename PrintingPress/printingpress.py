'''
Interesting Systems - PrintingPress
===================================
by hysrx, 2020.
'''

from PIL import Image, ImageFont, ImageDraw
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
                     expected_message: str = 'f:key is type f:type, but expected f:extype',
                     required_message: str = 'f:key is required'):
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
            if type(retrieved) != expected:
                message_formatting_map['f:type'] = str(type(retrieved))
                raise TypeError(Internals.format_message(expected_message,
                                                         message_formatting_map))

            return retrieved


class Placements:
    def parse(places: dict) -> dict:
        assert_prefix = '(printingpress.Placements.parse)'

        def rgb_list_check(area_name: str, elem_name: str, target: list) -> None:
            assert len(target) == 3, f'{assert_prefix} Area {area_name}: {elem_name} has {len(target)} values (expected 3)'  # noqa: E501

            for elem in target:
                assert elem < 256, f'{assert_prefix} Area {area_name}: {elem_name} has values that exceed 255'  # noqa: E501

        assert isinstance(places, dict), f'{assert_prefix} Non-dictionary passed in'

        parse_map = {
            # Argument Format: [expected (type), required (bool), fallback (*)]
            'image': {
                'path': [str, True, None],

                'xy': [list, True, None],

                'colour': [list, False, [0, 0, 0]],
                'opacity': [int, False, 0],
                'rotation': [int, False, 0]
            },

            'text': {
                'path': [str, True, None],

                'xy': [list, True, None],
                'wh': [list, True, None],

                'colour': [list, False, [0, 0, 0]],
                'opacity': [int, False, 0],
                'rotation': [int, False, 0],

                'font_colour': [list, False, [0, 0, 0]],
                'font_size': [int, True, None],
                'font_variant': [str, False, None]
            }
        }

        parsed_places = {}

        for area_name, area_data in places.items():
            parsed_area = {}

            area_type = Internals.retrieve_key(target=area_data, key='type', expected=str,
                                               required=True, extra=f' (area {area_name})')

            # Asserts if area_type is not image or text
            assert any([area_type == 'image', area_type == 'text']), f'{assert_prefix} Area {area_name}: type has to be "image" or "text", not "{area_type}"'  # noqa: E501

            # Loops through the area-specific mapping and does type/availability checks
            for elem, payload in parse_map[area_type].items():
                retrieved = Internals.retrieve_key(target=area_data, key=elem,
                                                   expected=payload[0],
                                                   required=payload[1],
                                                   fallback=payload[2],
                                                   extra=f' (area {area_name})')

                if 'colour' in elem:
                    rgb_list_check(area_name=area_name,
                                   elem_name=elem,
                                   target=retrieved)

                if elem == 'rotation' and retrieved > 360:
                    retrieved = 360

                if elem == 'opacity' and retrieved > 255:
                    retrieved = 255

                if elem == 'path':
                    retrieved = Path(retrieved).absolute()

                parsed_area[elem] = retrieved

            # Path checking
            assert parsed_area['path'].is_file(), f'{assert_prefix} Area {area_name}: path has to be an existant file'  # noqa: E501

            if area_type == 'font':  # Font-specific post-parse operations
                # Create PIL Font Object
                font = ImageFont.FreeTypeFont(font=parsed_area['path'],
                                              size=parsed_area['size'])

                # Retrieve font_variant key value
                font_variant = Internals.retrieve_key(target=parsed_area, key='font_variant',
                                                      expected=str, fallback=None)

                # Attempt to set font_variant
                if font_variant is not None:
                    try:
                        font.set_variation_by_name(bytes(font_variant, 'utf-8'))
                    except Exception as e:
                        print(f'{assert_prefix} Area: {area_name}: font_variant is invalid, continuing. ({e})')  # noqa: E501

                # Deposit font into parsed_area
                parsed_area['font'] = font

            else:  # Image-specific post-parse operations
                # Create PIL Image Object
                parsed_area['image'] = Image.open(parsed_area['path']).convert("RGBA")

            parsed_places[area_name] = parsed_area

        return parsed_places


def operate(image: Image.Image) -> Image.Image:
    assert_prefix = '(printingpress.operate)'
    assert isinstance(image, Image.Image), f'{assert_prefix} Passed image parameter is not a PIL Image'  # noqa: E501
