from src.PrintingPress import printingpress, placements
from PIL import Image


img = Image.new(mode="RGBA", size=(4000, 4000))

places = placements.Placements.parse(
    {
        "rollover": {
            "type": "text",
            "path": "tests/Manrope.ttf",
            "text": "What Goes Up Must Come Down",
            "xy": [100, 100],
            "wh": [3800, 3800],
            "font_size": 1000,
            "fit": True,
            "font_variant": "Bold",
            "font_colour": [0, 255, 255],
            "font_opacity": 255,
            "bg_colour": [255, 0, 255],
            "bg_opacity": 128,
        }
    }
)

printingpress.operate(image=img, placements=places).save("tests/rollover/output.png")
