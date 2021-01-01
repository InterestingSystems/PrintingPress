print("rollover test")

from src import PrintingPress as pp
from PIL import Image


img = Image.new(mode="RGBA", size=(4000, 4000))

places = pp.Placements.parse(
    {
        "rollover": {
            "type": "text",
            "path": "tests/Manrope.ttf",
            "text": "You, say, isn't it hard? Paddling out, paddling out?, g",
            "xy": [0, 0],
            "wh": [4000, 4000],
            "font_size": 700,
            "fit": True,
            "font_variant": "Bold",
        }
    }
)

pp.operate(image=img, placements=places).save("tests/rollover/output.png")
