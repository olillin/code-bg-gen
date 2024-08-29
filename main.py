from PIL import Image, ImageFont, ImageDraw
from pathlib import Path
import pyautogui
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import ImageFormatter
from pygments.util import ClassNotFound

fontpath = "resources/JetBrainsMonoNerdFont-Regular.ttf"


theme = {
    "font_name": fontpath,
    "background": (10, 10, 10),
}


def render_source(
    source: str,
    resolution: tuple[int, int],
) -> Image.Image:
    scale = 3
    big_resolution = (resolution[0] * scale, resolution[1] * scale)
    margin = (int(big_resolution[0] * 0.01), int(big_resolution[1] * 0.01))
    image = Image.new("RGBA", big_resolution)
    draw = ImageDraw.Draw(image)


#     # Fit onto screen
#     fontsize = 50
#     font = ImageFont.truetype(fontpath, fontsize)

#     # _, _, bb_width, bb_height = font.getbbox(source)
#     # print(bbox)
#     # bb_width = bbox[2] - bbox[0]
#     # bb_height = bbox[3] - bbox[1]
#     # print(bb_width, bb_height)
#     # print(big_resolution)
#     # print(big_resolution[0] / bb_width)
#     # print(big_resolution[1] / bb_height)
#     # fontsize = int(
#     #     fontsize * min(big_resolution[0] / bb_width, big_resolution[1] / bb_height)
#     # )
#     # print(fontsize)
#     length = max([font.getlength(line) for line in source.split("\n")])
#     fontsize = int(0.9 * fontsize * big_resolution[0] / length)
#     font = ImageFont.truetype(fontpath, fontsize)

#     draw.text(margin, source, (255, 255, 255), font)
#     return image.resize(resolution, Image.Resampling.BICUBIC)


def render_header(
    title: str,
    size: tuple[int, int],
    color: tuple[int, int, int] = (0, 0, 0),
    background: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    image = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(image)
    fontsize = size[1] * 0.7
    font = ImageFont.truetype(fontpath, fontsize)

    draw.text((10, 5), title, color, font)

    return image


def render_file(path: Path, size: tuple[int, int]) -> Image.Image:
    with open(path, "r") as f:
        source = f.read()

    header_height = 80

    image = Image.new("RGB", size, theme["background"])
    # Header
    header = render_header(str(path.absolute()), (size[0], header_height))
    image.paste(header, (0, 0))
    # Code
    try:
        lexer = get_lexer_for_filename(path.name)
        formatter = ImageFormatter(font_size=50, **theme)
        code_bytes = highlight(source, lexer, formatter)
        temp_path = "temp.png"
        with open(temp_path, "w+") as f:
            f.buffer.write(code_bytes)
        code = Image.open(temp_path)
        image.paste(code, (0, header_height))
    except ClassNotFound:
        print(f"Failed to find lexer for {path.name}")

    return image


render_file(Path(__file__), pyautogui.size()).save("bg.png")
print("Done")
