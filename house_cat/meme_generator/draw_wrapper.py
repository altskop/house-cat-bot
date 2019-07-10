from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class GeneratorDraw(ImageDraw.ImageDraw):

    def __init__(self, im, font, fontsize, stroke_size=None, smallest_font=6):
        super().__init__(im)
        self.font = font
        self.fontsize = fontsize
        self.stroke_size = stroke_size
        self.smallest_font = smallest_font

    def draw_field(self, number, point_1, point_2):
        self.rectangle(((point_1['x'], point_1['y']), (point_2['x'], point_2['y'])), fill=(0, 255, 0, 130))
        self.draw_multiple_line_text(str(number), "white", point_1, point_2)

    def draw_multiple_line_text(self, text: str, text_color, point_1, point_2):
        area_width = abs(point_2['x'] - point_1['x'])
        area_height = abs(point_2['y'] - point_1['y'])
        lines, font, font_max_height = self.text_wrap(text, area_width, area_height, self.fontsize)
        # Align text vertically in middle
        y_text = point_1['y'] + ((area_height - ((font_max_height + 1) * len(lines))) / 2)
        for line in lines:
            line_width, line_height = font.getsize(line)
            x = point_1['x'] + (area_width / 2) - (line_width / 2)  # Center the text
            if self.stroke_size is not None:
                stroke_color = "black"
                for x_offset in range(-self.stroke_size, self.stroke_size + 1, self.stroke_size):
                    for y_offset in range(-self.stroke_size, self.stroke_size + 1, self.stroke_size):
                        self.text((x + x_offset, y_text + y_offset), line, font=font,
                                  fill=stroke_color)
                text_color = "white"
            self.text((x, y_text), line, font=font, fill=text_color)
            y_text += line_height + 1

    def text_wrap(self, text, max_width, max_height, fontsize):
        text = text.strip()
        if fontsize < self.smallest_font:
            raise ValueError('Text too big for the field')
        font = ImageFont.truetype("/storage/memes/fonts/%s.ttf" % self.font, fontsize)
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
            return self.text_wrap(text, max_width, max_height, fontsize - 1)
        return lines, font, font_max_height
