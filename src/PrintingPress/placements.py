from . import internals as Internals
from collections import namedtuple
from PIL import ImageFont, Image
from pathlib import Path


def rgb_list_check(area_name: str, elem_name: str, target: list) -> None:
    assert (
        len(target) == 3
    ), f"Area {area_name}: key {elem_name} has {len(target)} values (expected 3)"

    for elem in target:
        assert (
            elem < 256
        ), f"Area {area_name}: key {elem_name} has values that exceed 255"


def filter_list_check(area_name: str, filter_name: str, target: list) -> None:
    filter_map = {"gaussian_blur": [int], "box_blur": [int]}

    filter_target_mapping = filter_map[filter_name]

    # Check list lengths
    assert len(filter_target_mapping) == len(target), (
        f"Area {area_name}: key filter_data has {len(target)} values "
        f"(expected {len(filter_target_mapping)})"
    )

    for expected, actual in zip(filter_target_mapping, target):
        assert isinstance(
            actual, expected
        ), f"Area {area_name}: key filter_data has values with unexpected types"


class Placements:
    __parse_map__ = {
        # Argument Format: [expected (type), required (bool), fallback (*)]
        "image": {
            "type": None,
            "path": [(str, Image.Image), True, None],
            "xy": [list, True, None],
            "wh": [list, False, None],
            "filter": [str, False, None],
            "filter_data": [list, False, []],
            "opacity": [int, False, 255],
            "rotation": [int, False, 0],
            "beneath": [bool, False, False],
            "image": None,
        },
        "text": {
            "type": None,
            "path": [str, True, None],
            "text": [str, True, None],
            "xy": [list, True, None],
            "wh": [list, True, None],
            "bg_colour": [list, False, [0, 0, 0]],
            "bg_opacity": [int, False, 255],
            "font_colour": [list, False, [255, 255, 255]],
            "font_size": [int, True, None],
            "font_variant": [str, False, None],
            "font_opacity": [int, False, 255],
            "fit": [bool, False, False],
            "beneath": [bool, False, False],
            "rotation": [int, False, 0],
            "font": None,
        },
    }

    __imagearea__ = namedtuple("ImageArea", __parse_map__["image"])
    __textarea__ = namedtuple("TextArea", __parse_map__["text"])

    def parse(places: dict) -> dict:
        assert isinstance(places, dict), "Non-dictionary passed in"

        # Skips .meta
        parsed_places = {".meta": places.pop(".meta")} if ".meta" in places else {}

        for area_name, area_data in places.items():
            parsed_area = {}

            parsed_area["type"] = Internals.retrieve_key(
                target=area_data,
                key="type",
                expected=str,
                required=True,
                extra=f" (area {area_name})",
            )

            # Asserts if parsed_area['type'] is not image or text
            assert any(
                [parsed_area["type"] == "image", parsed_area["type"] == "text"]
            ), (
                f'Area {area_name}: key type has to be "image" or "text", '
                f'not "{parsed_area["type"]}"'
            )

            # Loops through the area-specific mapping and does type/availability checks
            for elem, payload in Placements.__parse_map__[parsed_area["type"]].items():
                if payload is not None:
                    retrieved = Internals.retrieve_key(
                        target=area_data,
                        key=elem,
                        expected=payload[0],
                        required=payload[1],
                        fallback=payload[2],
                        extra=f" (area {area_name})",
                    )

                    if "colour" in elem:
                        rgb_list_check(
                            area_name=area_name, elem_name=elem, target=retrieved
                        )

                    if elem == "rotation" and retrieved > 360:
                        retrieved = 360

                    if "opacity" in elem and retrieved > 255:
                        retrieved = 255

                    if elem == "path" and isinstance(retrieved, str):
                        retrieved = Path(retrieved).absolute()

                    if elem == "xy" or elem == "wh":
                        assert len(retrieved) == 2, (
                            f"Area {area_name}: key {elem} has {len(retrieved)} values "
                            "(expected 2)"
                        )

                    parsed_area[elem] = retrieved

            if parsed_area["type"] == "text":  # Text-specific post-parse operations
                assert parsed_area[
                    "path"
                ].is_file(), f'Area {area_name}: {parsed_area["path"]} is non-existant'

                # Create PIL Font Object
                font = ImageFont.FreeTypeFont(
                    font=str(parsed_area["path"]), size=parsed_area["font_size"]
                )

                # Retrieve font_variant key value
                font_variant = Internals.retrieve_key(
                    target=parsed_area,
                    key="font_variant",
                    expected=(str, type(None)),
                    fallback=None,
                )

                # Attempt to set font_variant
                if font_variant is not None:
                    try:
                        font.set_variation_by_name(bytes(font_variant, "utf-8"))
                    except Exception as e:
                        print(
                            f"Area: {area_name}: font_variant is invalid, continuing. "
                            f"({e})"
                        )

                # Add font into parsed_area
                parsed_area["font"] = font

                parsed_places[area_name] = Placements.__textarea__(
                    **parsed_area
                )  # Create namedtuple

            else:  # Image-specific post-parse operations
                if isinstance(parsed_area["path"], Image.Image):
                    # Users can pass PIL Images into the path key if constructing
                    # a placement dictionary in Python rather than from a JSON file.
                    # le. So, if this happens just use the image from the path key.
                    parsed_area["image"] = parsed_area["path"]

                else:
                    assert parsed_area[
                        "path"
                    ].is_file(), (
                        f'Area {area_name}: {parsed_area["path"]} is non-existant'
                    )

                    # Else, create a PIL Image Object from the path given
                    parsed_area["image"] = Image.open(parsed_area["path"]).convert(
                        "RGBA"
                    )

                if str(parsed_area["filter"]) not in ["gaussian_blur", "box_blur"]:
                    parsed_area["filter"] = None

                else:
                    filter_list_check(
                        area_name=area_name,
                        filter_name=parsed_area["filter"],
                        target=parsed_area["filter_data"],
                    )

                parsed_places[area_name] = Placements.__imagearea__(
                    **parsed_area
                )  # Create namedtuple

        return parsed_places
