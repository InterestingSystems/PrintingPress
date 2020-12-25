from src import PrintingPress as printingpress
from json import load
from PIL import Image

thumbnail = Image.open('tests/ii/template-text.png')

with open('tests/ii/placements.json', 'r', encoding='utf-8') as pf:
    placements = printingpress.Placements.parse(load(pf))
    print(placements)

printingpress.operate(image=thumbnail, placements=placements, suppress=False).save('tests/ii/output.png')
