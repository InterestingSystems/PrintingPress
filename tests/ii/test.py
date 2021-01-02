from src.PrintingPress import printingpress, placements
from json import load
from PIL import Image
from time import time

thumbnail = Image.open("tests/ii/template-text.png")

with open("tests/ii/placements.json", "r", encoding="utf-8") as pf:
    placements = placements.Placements.parse(load(pf))

stime = time()

printingpress.operate(image=thumbnail, placements=placements, suppress=True).save(
    "tests/ii/output.png"
)

print(time() - stime)
