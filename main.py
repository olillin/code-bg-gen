from PIL import Image, ImageFont, ImageDraw
import PIL.ImageOps
from pathlib import Path
import pyautogui
from random import Random
from pygments import highlight
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename
from pygments.lexers._mapping import LEXERS
from pygments.style import Style
from pygments.formatters import ImageFormatter
from pygments.util import ClassNotFound
from simpleicons.all import icons
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import glob

from style import AyuMirage

fontpath = "resources/JetBrainsMonoNerdFont-Regular.ttf"
style: type[Style] = AyuMirage


def render_source(
    lexer: Lexer,
    source: str,
    size: tuple[int, int],
    start_line: int = 1,
) -> Image.Image:
    # Render text
    highlight_line = Random().randint(1, source.count("\n") + 1)
    formatter = ImageFormatter(
        font_name=fontpath,
        font_size=50,
        style=style,
        line_pad=8,
        line_number_fg=style.line_number_color,
        line_number_bg=style.line_number_background_color,
        line_number_separator=False,
        hl_lines=[highlight_line],
        line_number_pad=30,
        line_number_start=start_line,
    )
    code_bytes = highlight(source, lexer, formatter)
    temp_image_path = "temp.png"
    with open(temp_image_path, "w+") as f:
        f.buffer.write(code_bytes)
    code = Image.open(temp_image_path)
    code.load()
    os.remove(temp_image_path)

    image = Image.new("RGBA", size, style.background_color)
    code_scale = min(image.height / code.height, image.width / code.width)
    code_size: tuple[int, int] = (
        int(code.width * code_scale),
        int(code.height * code_scale),
    )
    code_resized = code.resize(code_size, Image.Resampling.BICUBIC)
    image.paste(code_resized, (0, 0))
    return image


def render_header(
    title: str,
    size: tuple[int, int],
    color: tuple[int, int, int] | str = (0, 0, 0),
    background: tuple[int, int, int] | str = (255, 255, 255),
    icon: Image.Image = Image.new("RGBA", (0, 0)),
) -> Image.Image:
    image = Image.new("RGBA", size, background)
    # Icon
    icon_size = int(size[1] * 0.6)
    icon_resized = icon.resize((icon_size, icon_size))
    icon_position = (10, int((size[1] - icon_resized.height) / 2))

    # Text
    draw = ImageDraw.Draw(image)
    fontsize = size[1] * 0.45
    font = ImageFont.truetype(fontpath, fontsize)
    _, bbox_top, _, bbox_bottom = font.getbbox(title)
    text_position = (30 + icon_size, (size[1] - bbox_bottom + bbox_top) / 2 - bbox_top)

    # Draw
    draw.text(text_position, title, color, font)
    image.alpha_composite(icon_resized, icon_position)

    return image


def get_shortname(file_name: str) -> str | None:
    for _, _, shortnames, extensions, _ in LEXERS.values():
        for extension in extensions:
            if file_name.endswith(extension.replace("*", "")):
                return shortnames[0]


def get_icon(file_name: str) -> Image.Image:
    empty_icon = Image.new("RGBA", (0, 0))

    shortname = get_shortname(file_name)
    if not shortname:
        return empty_icon
    icon = icons.get(shortname)
    if not icon:
        return empty_icon

    svg: str = icon.svg
    temp_svg_path = "temp.svg"
    with open(temp_svg_path, "w+") as f:
        f.write(svg)
    rlg = svg2rlg(temp_svg_path)
    os.remove(temp_svg_path)
    if not rlg:
        return empty_icon
    temp_image_path = "temp.png"
    renderPM.drawToFile(rlg, temp_image_path, fmt="PNG", dpi=200)
    icon_image: Image.Image = Image.open(temp_image_path)
    icon_image.load()
    os.remove(temp_image_path)
    inverted_icon_image = PIL.ImageOps.invert(icon_image)

    # fmt: off
    matrix = (0.0, 0.0, 0.0, 255, # brightness
              1.0, 0.0, 0.0, 0, # alpha
              0.0, 0.0, 0.0, 0) # unused
    # fmt: on
    converted = inverted_icon_image.convert("RGB", matrix)
    brightness, alpha, _ = converted.split()
    image = Image.merge("RGBA", (brightness, brightness, brightness, alpha))
    return image


def render_file(path: Path, size: tuple[int, int], maxlines: int = 40) -> Image.Image:
    start_line = 0
    with open(path, "r") as f:
        lines = f.readlines()
        if len(lines) > maxlines:
            start_line: int = Random().randint(0, len(lines) - maxlines - 1)
            lines = lines[start_line : start_line + maxlines]
        source = "".join(lines)

    header_height = 70

    image = Image.new("RGB", size, (255, 255, 255))
    # Header
    icon = get_icon(path.name)
    header = render_header(
        str(path),
        (size[0], header_height),
        "#cccac2",
        style.background_color,
        icon,
    )
    image.paste(header, (0, 0))
    # Code
    try:
        lexer = get_lexer_for_filename(path.name)
        code = render_source(
            lexer, source, (size[0], size[1] - header_height), start_line + 1
        )
        image.paste(code, (0, header_height))
    except ClassNotFound as e:
        print(f"Failed to render source code for {path.name}: {e}")
        raise e

    return image


def can_render(path: Path) -> bool:
    try:
        get_lexer_for_filename(path.name)
        with open(path, "r") as f:
            lines = f.readlines()
            if len(lines) == 0:
                return False
            for line in lines:
                if len(line) > 500:
                    return False
    except:
        return False
    return True


def main():
    files = glob.glob("../**/*")
    screen_resolution: tuple[int, int] = pyautogui.size()

    out_dir: Path = Path("out")
    if not out_dir.exists():
        os.makedirs(out_dir)

    i = 0
    for fn in files:
        path = Path(fn).resolve()
        if not can_render(path):
            continue
        print(f"Rendering {path}")
        try:
            bg = render_file(path, screen_resolution)
            bg.save(out_dir.joinpath(f"bg_{i}.png"))
            i += 1
        except ClassNotFound:
            continue
    print("Done")


if __name__ == "__main__":
    main()
