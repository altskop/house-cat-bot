from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os.path
import json
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

    def __init__(self, id: str, text_list: list, color="black"):
        self.id = id
        self.path = os.path.normpath("/storage/memes/templates/" + id + "/")
        self.text_list = text_list
        self.color = color.lower()
        self.metadata = self.read_metadata()

        if self.metadata['font'] == "normal":
            self.fontsize = NORMAL_FONTSIZE
            self.font = NORMAL_FONT
            self.stroke_size = None
        elif self.metadata['font'] == "bold":
            self.fontsize = BOLD_FONTSIZE
            self.font = BOLD_FONT
            self.stroke_size = STROKE_SIZE
        else:
            raise ValueError('Font style %s is not supported' % self.metadata['font'])

        self.smallest_font = SMALLEST_FONT

    @property
    def template(self):
        template = Image.open(self.path + "/template.png")
        return template

    def read_metadata(self):
        with open(self.path + "/metadata.json", 'r') as metadata_file:
            data = json.load(metadata_file)
            return data

    def generate(self):
        if len(self.text_list)>0:
            return self.add_text_to_image()
        else:
            return self.display_fields()

    def add_text_to_image(self):
        image = self.template
        # draw = ImageDraw.Draw(image)
        draw = GeneratorDraw(image, self.font, self.fontsize, self.stroke_size)
        for i, text in enumerate(self.text_list):
            point_1 = self.metadata['fields'][i]['point_1']
            point_2 = self.metadata['fields'][i]['point_2']
            draw.draw_multiple_line_text(text, self.color, point_1, point_2)
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return output

    def display_fields(self):
        image = self.template
        image = image.convert("RGBA")
        tmp = Image.new('RGBA', image.size, (0, 0, 0, 0))
        # draw = ImageDraw.Draw(tmp)
        draw = GeneratorDraw(tmp, self.font, self.fontsize, self.stroke_size)
        for i, field in enumerate(self.metadata['fields']):
            point_1 = field['point_1']
            point_2 = field['point_2']
            draw.draw_field(i+1, point_1, point_2)
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
