# Copy of draw_wrapper.py in house cat bot
# TODO find a better way to use this in both places (package it?)

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

SMALLEST_FONT = 6


class GeneratorDraw(ImageDraw.ImageDraw):

    def draw_field(self, number, x, y, w, h):
        x2 = x + w
        y2 = y + h
        self.rectangle(((x, y), (x2, y2)), fill=(0, 255, 0, 130))
        self.draw_multiple_line_text(str(number), "white", x, y, w, h, "center", "Impact", 42, None)

    def draw_multiple_line_text(self, text: str, text_color, x, y, area_width, area_height, align, font, fontsize, stroke_size):
        lines, font, font_max_height = self.text_wrap(text, area_width, area_height, font, fontsize)
        # Align text vertically in middle
        y_text = y + ((area_height - ((font_max_height + 1) * len(lines))) / 2)
        for line in lines:
            line_width, line_height = font.getsize(line)
            x_text = self.get_x_pos(x, area_width, line_width, align)
            if stroke_size is not None:
                stroke_color = "black"
                for x_offset in range(-stroke_size, stroke_size + 1, stroke_size):
                    for y_offset in range(-stroke_size, stroke_size + 1, stroke_size):
                        self.text((x_text + x_offset, y_text + y_offset), line, font=font,
                                  fill=stroke_color)
            self.text((x_text, y_text), line, font=font, fill=text_color)
            y_text += line_height + 1

    @staticmethod
    def get_x_pos(x, area_width, line_width, align):
        if align == "center":
            return x + (area_width / 2) - (line_width / 2)
        elif align == "left":
            return x
        else:  # right
            return x + area_width - line_width

    def text_wrap(self, text, max_width, max_height, fontname, fontsize):
        text = text.strip()
        if fontsize < SMALLEST_FONT:
            raise ValueError('Text too big for the field')
        font = ImageFont.truetype("/storage/memes/fonts/%s.ttf" % fontname, fontsize)
        lines = []
        font_max_height = 0
        font_max_width = 0
        # If the width of the text is smaller than image width
        # we don't need to split it, just add it to the lines array
        # and return
        if font.getsize(text)[0] <= max_width:
            font_max_height = font.getsize(text)[1]
            font_max_width = font.getsize(text)[0]
            lines.append(text)
        else:
            # split the line by spaces to get words
            words = text.split(' ')
            i = 0
            # append every word to a line while its width is shorter than image width
            while i < len(words):
                line = ''
                while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                    line = line + words[i] + " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1
                # when the line gets longer than the max width do not append the word,
                # add the line to the lines array
                font_max_height = max(font_max_height, font.getsize(line)[1])
                font_max_width = max(font_max_width, font.getsize(line)[0])
                lines.append(line)
        # If text still too big, rewrap
        # TODO perhaps there is a better way than recursively do this
        if (font_max_height + 1) * len(lines) > max_height or font_max_width > max_width:
            return self.text_wrap(text, max_width, max_height, fontname, fontsize - 1)
        return lines, font, font_max_height
