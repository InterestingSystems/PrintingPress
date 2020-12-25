# PrintingPress, by hysrx

from PIL import Image, ImageFont, ImageDraw, ImageFilter
from . import (
    internals as Internals,
    exceptions
)


def operate(image: Image.Image, placements: dict, suppress: bool = False) -> Image.Image:
    assert isinstance(image, Image.Image), 'Passed image parameter is not a PIL Image'

    if 'A' not in image.mode:
        image = image.convert('RGBA')

    suppress = not suppress  # negate for condition in Internals.print_if

    if '.meta' in placements:
        placements.pop('.meta')

    for area_name, area_data in placements.items():
        Internals.print_if(f'\nOperating on area {area_name}. ({area_data.type})',
                           condition=suppress)

        if area_data.type == 'text':  # Text-based operation
            def rollover(
                text: str,
                area_name: str,
                font: ImageFont.ImageFont,
                wh: list,
                raise_err: bool = False
            ) -> list:
                # Rollover
                max_width, max_height = wh

                text = text.split()
                words = len(text)

                wcurr = lambda: '\n'.join([' '.join(l) for l in lines])
                wlast = lambda: ' '.join(lines[-1])

                line_h_local = 0

                lines = [[]]
                line_h = []

                for word in text:
                    lines[-1].append(word)
                    _, _, txtw, txth = font.getmask(' '.join(lines[-1])).getbbox()

                    if txtw > max_width:  # Too wide, rollover
                        lines.append([lines[-1].pop(-1)])

                        if line_h_local == 0:
                            line_h_local = txth + font.font.descent

                        line_h.append(line_h_local)
                        line_h.append(txth)

                    else:
                        line_h_local = max([line_h_local, txth + font.font.descent])

                    if sum(line_h) > max_height or line_h_local > max_height:
                        if raise_err:  # Too tall even after rollover, need to change font size
                            raise exceptions.RolloverError()

                        if words == 1:
                            print(f'Warning: Area {area_name}\'s text exceeds the box and will not be displayed properly. [Text: ({txtw}, {txth}), Box: {wh}]')

                        lines.pop(-1)
                        try:
                            lines[-1][-1] = '…'
                        except IndexError:
                            pass

                if lines[0] == []:
                    lines.pop(0)

                return lines

            # Subimage creation
            Internals.print_if('  Creating subimage...', end='\r', condition=suppress)
            subimage = Image.new(mode='RGBA',
                                 size=tuple(area_data.wh),
                                 color=(area_data.bg_opacity,) + tuple(area_data.bg_colour))
            Internals.print_if('  Creating subimage... DONE', condition=suppress)

            # Rollover/Fit Calculation
            if area_data.fit:
                Internals.print_if('  Calculating minimum font size...', end='\r',
                                   condition=suppress)

                def recreate(size: int = area_data.font_size) -> ImageFont.ImageFont:
                    font = ImageFont.FreeTypeFont(font=str(area_data.path), size=size)
                    try:
                        area_data.font_variant
                    except Exception:
                        pass
                    else:
                        try:
                            font.set_variation_by_name(area_data.font_variant)
                        except Exception:
                            pass
                    return font
                

                size = area_data.font_size
                font = area_data.font
                tries = 1

                while True:
                    try:
                        text = rollover(text=area_data.text,
                                        area_name=area_name,
                                        font=font,
                                        wh=area_data.wh,
                                        raise_err=True)
                    except exceptions.RolloverError:
                        # This is slow - but this will do for now.
                        size -= 1
                        tries += 1
                        font = recreate(size)
                    else:
                        break

                    Internals.print_if(f'  Calculating minimum font size... ({tries})',
                                       end='\r', condition=suppress)

                Internals.print_if(f'  Calculating minimum font size... DONE ({tries}, {area_data.font_size} -> {size})',
                                   condition=suppress)

            else:
                font = area_data.font
                Internals.print_if('  Calculating rollover...', end='\r', condition=suppress)
                text = rollover(text=area_data.text,
                                area_name=area_name,
                                font=font,
                                wh=area_data.wh)
                Internals.print_if('  Calculating rollover... DONE', condition=suppress)


            # Draw Text
            Internals.print_if('  Drawing text...', end='\r', condition=suppress)

            drawer = ImageDraw.Draw(subimage)
            fill = area_data.font_colour.copy()
            fill.append(area_data.font_opacity)

            x, y = 0, 0

            for line_no, line in enumerate(text):
                # TODO: Support ltr or centered text by changing x coords
                text = ' '.join(line)
                txth = font.getmask(text).getbbox()[3]

                if line_no == 0:
                    y = 0 - (font.font.descent / 2)

                drawer.text(xy=(x, y),
                            text=text,
                            fill=tuple(fill),
                            font=font)

                y += txth + font.font.descent

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

            holder = Image.new(mode='RGBA', size=image.size)
            holder.paste(im=area_image, box=tuple(area_data.xy))

            if area_data.beneath:
                image = Image.alpha_composite(holder, image)
            else:
                image = Image.alpha_composite(image, holder)

            Internals.print_if('  Pasting image onto target... DONE', condition=suppress)

        Internals.print_if('  All operations complete.', condition=suppress)

    return image
