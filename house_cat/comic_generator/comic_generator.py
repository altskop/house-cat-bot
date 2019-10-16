from PIL import Image
import io


class ComicGenerator:

    def __init__(self, images: list):
        img_list = [io.BytesIO(bytes(x['image'])) for x in images]
        self.images = list(map(Image.open, img_list))

    def generate(self):
        widths, heights = zip(*(i.size for i in self.images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in self.images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        output = io.BytesIO()
        new_im.save(output, format="PNG")
        output.seek(0)
        return output
