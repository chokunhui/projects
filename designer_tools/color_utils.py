import colorsys
from html import escape

from PIL import Image


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    color = value.strip().removeprefix("#")
    if len(color) == 3:
        color = "".join(character * 2 for character in color)
    if len(color) != 6:
        raise ValueError("색상은 3자리 또는 6자리 HEX 값이어야 합니다.")
    try:
        return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as error:
        raise ValueError("HEX 색상에 잘못된 문자가 포함되어 있습니다.") from error


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    return f"#{red:02X}{green:02X}{blue:02X}"


def theme_from_color(color: str) -> dict[str, str]:
    red, green, blue = hex_to_rgb(color)
    hue, lightness, saturation = colorsys.rgb_to_hls(
        red / 255, green / 255, blue / 255
    )
    secondary = colorsys.hls_to_rgb((hue + 0.5) % 1, lightness, saturation)
    background = colorsys.hls_to_rgb(hue, 0.96, min(saturation * 0.25, 0.12))
    return {
        "기본색": rgb_to_hex(red, green, blue),
        "보조색": rgb_to_hex(*(round(channel * 255) for channel in secondary)),
        "배경색": rgb_to_hex(*(round(channel * 255) for channel in background)),
    }


def extract_top_colors(image: Image.Image, limit: int = 5) -> list[tuple[str, int]]:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, "white")
    thumbnail = Image.alpha_composite(background, rgba).convert("RGB")
    thumbnail.thumbnail((400, 400))
    quantized = thumbnail.quantize(colors=limit, method=Image.Quantize.MEDIANCUT)
    colors = quantized.convert("RGB").getcolors(maxcolors=400 * 400) or []
    colors.sort(reverse=True, key=lambda color: color[0])
    return [(rgb_to_hex(*rgb), count) for count, rgb in colors[:limit]]


def render_swatches(colors: dict[str, str]) -> str:
    swatches = []
    for label, color in colors.items():
        hex_to_rgb(color)
        swatches.append(
            '<div style="flex:1;min-width:130px">'
            f'<div style="height:112px;background:{escape(color)};'
            'border-radius:4px;border:1px solid #00000018"></div>'
            f'<div style="font-size:13px;margin-top:8px">{escape(label)}</div>'
            f'<code style="font-size:12px">{escape(color)}</code>'
            '</div>'
        )
    return '<div style="display:flex;gap:12px;flex-wrap:wrap">' + "".join(
        swatches
    ) + "</div>"