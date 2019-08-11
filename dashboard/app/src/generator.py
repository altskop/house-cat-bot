# Copy of generator.py in house cat bot
# TODO find a better way to use this in both places (package it?)

from PIL import Image
import io
from .draw_wrapper import GeneratorDraw

# Static vars
NORMAL_FONT = "Arial"
NORMAL_FONTSIZE = 28

BOLD_FONT = "Impact"
BOLD_FONTSIZE = 42
STROKE_SIZE = 3

SMALLEST_FONT = 6


class MemeGenerator:

    def __init__(self, image_blob, metadata, text_list: list):
        self.template = Image.open(io.BytesIO(image_blob))
        self.text_list = text_list
        self.metadata = metadata

        self.smallest_font = SMALLEST_FONT

    def generate(self):
        if len(self.text_list) > 0:
            return self.add_text_to_image()
        else:
            return self.display_fields()

    def add_text_to_image(self):
        image = self.template
        draw = GeneratorDraw(image)
        for i, text in enumerate(self.text_list):
            x = self.metadata['fields'][i]['x']
            y = self.metadata['fields'][i]['y']
            w = self.metadata['fields'][i]['w']
            h = self.metadata['fields'][i]['h']
            color = self.metadata['fields'][i]['color']
            align = self.metadata['fields'][i]['align']
            font = self.metadata['fields'][i]['font']

            if font == "normal":
                fontsize = NORMAL_FONTSIZE
                font = NORMAL_FONT
                stroke_size = None
            else:  # bold
                fontsize = BOLD_FONTSIZE
                font = BOLD_FONT
                stroke_size = STROKE_SIZE

            draw.draw_multiple_line_text(text, color, x, y, w, h, align, font, fontsize, stroke_size)
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return output

    def display_fields(self):
        image = self.template
        image = image.convert("RGBA")
        tmp = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = GeneratorDraw(tmp)
        for i, field in enumerate(self.metadata['fields']):
            x = self.metadata['fields'][i]['x']
            y = self.metadata['fields'][i]['y']
            w = self.metadata['fields'][i]['w']
            h = self.metadata['fields'][i]['h']
            draw.draw_field(i+1, x, y, w, h)
        image = Image.alpha_composite(image, tmp)
        image = image.convert("RGB")
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return output


if __name__ == "__main__":
    gen = MemeGenerator("its-retarded", ["I'm exhausted I tried to clean a hallway today and it was so hard"])
    file = gen.add_text_to_image()
    img = Image.open(file)
    img.show()
