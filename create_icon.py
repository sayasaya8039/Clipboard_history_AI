"""本番用アプリアイコン生成スクリプト"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BASE_SIZE = 1024
OUT_DIR = Path(__file__).resolve().parent / "resources"
ICON_SIZES = [16, 32, 48, 64, 128, 256]


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in range(0, 6, 2)) + (alpha,)


def blend(color_a: tuple[int, int, int, int], color_b: tuple[int, int, int, int], t: float) -> tuple[int, int, int, int]:
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(color_a, color_b))


def vertical_gradient(width: int, height: int, top: tuple[int, int, int, int], bottom: tuple[int, int, int, int]) -> Image.Image:
    gradient = Image.new("RGBA", (1, height))
    pixels = gradient.load()
    for y in range(height):
        t = y / max(1, height - 1)
        pixels[0, y] = blend(top, bottom, t)
    return gradient.resize((width, height), Image.Resampling.BICUBIC)


def rounded_mask(size: int, rect: tuple[int, int, int, int], radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(rect, radius=radius, fill=255)
    return mask


def draw_card_shadow(size: int) -> Image.Image:
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((330, 318, 694, 734), radius=76, fill=rgba("#000000", 110))
    draw.rounded_rectangle((392, 232, 632, 344), radius=44, fill=rgba("#000000", 92))
    return layer.filter(ImageFilter.GaussianBlur(20))


def create_master_icon() -> Image.Image:
    canvas = Image.new("RGBA", (BASE_SIZE, BASE_SIZE), (0, 0, 0, 0))

    background = vertical_gradient(
        BASE_SIZE,
        BASE_SIZE,
        rgba("#0b1220"),
        rgba("#14213d"),
    )
    background.putalpha(rounded_mask(BASE_SIZE, (72, 72, BASE_SIZE - 72, BASE_SIZE - 72), 220))
    canvas = Image.alpha_composite(canvas, background)

    glow = Image.new("RGBA", (BASE_SIZE, BASE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((-120, -80, 760, 740), fill=rgba("#2d7ff9", 90))
    draw.ellipse((560, 32, 1120, 592), fill=rgba("#06b6d4", 54))
    draw.ellipse((192, 164, 832, 804), fill=rgba("#60a5fa", 34))
    glow = glow.filter(ImageFilter.GaussianBlur(96))
    canvas = Image.alpha_composite(canvas, glow)

    border = Image.new("RGBA", (BASE_SIZE, BASE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(border)
    draw.rounded_rectangle(
        (72, 72, BASE_SIZE - 72, BASE_SIZE - 72),
        radius=220,
        outline=rgba("#a5c8ff", 30),
        width=10,
    )
    canvas = Image.alpha_composite(canvas, border)

    canvas = Image.alpha_composite(canvas, draw_card_shadow(BASE_SIZE))

    body = vertical_gradient(
        BASE_SIZE,
        BASE_SIZE,
        rgba("#ffffff"),
        rgba("#edf3fb"),
    )
    body_mask = rounded_mask(BASE_SIZE, (350, 296, 674, 720), 72)
    body.putalpha(body_mask.crop((0, 0, BASE_SIZE, BASE_SIZE)))
    canvas = Image.alpha_composite(canvas, body)

    clip = vertical_gradient(
        BASE_SIZE,
        BASE_SIZE,
        rgba("#f8fbff"),
        rgba("#dfe7f2"),
    )
    clip_mask = rounded_mask(BASE_SIZE, (414, 220, 610, 356), 42)
    clip.putalpha(clip_mask.crop((0, 0, BASE_SIZE, BASE_SIZE)))
    canvas = Image.alpha_composite(canvas, clip)

    accent = Image.new("RGBA", (BASE_SIZE, BASE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(accent)
    line_color = rgba("#2d7ff9")
    draw.rounded_rectangle((414, 446, 610, 474), radius=14, fill=line_color)
    draw.rounded_rectangle((414, 520, 582, 548), radius=14, fill=line_color)
    draw.rounded_rectangle((414, 594, 558, 622), radius=14, fill=line_color)
    draw.ellipse((606, 416, 634, 444), fill=rgba("#2d7ff9", 220))
    draw.ellipse((616, 404, 640, 428), fill=rgba("#ffffff", 220))
    accent = accent.filter(ImageFilter.GaussianBlur(0.4))
    canvas = Image.alpha_composite(canvas, accent)

    outline = Image.new("RGBA", (BASE_SIZE, BASE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(outline)
    draw.rounded_rectangle((350, 296, 674, 720), radius=72, outline=rgba("#0f172a", 26), width=8)
    draw.rounded_rectangle((414, 220, 610, 356), radius=42, outline=rgba("#0f172a", 18), width=6)
    canvas = Image.alpha_composite(canvas, outline)

    return canvas


def create_production_app_icon() -> None:
    """本番用アプリアイコンを生成する。"""
    OUT_DIR.mkdir(exist_ok=True)
    master = create_master_icon()

    png = master.resize((256, 256), Image.Resampling.LANCZOS)
    png.save(OUT_DIR / "icon.png", format="PNG")

    master.save(
        OUT_DIR / "icon.ico",
        format="ICO",
        sizes=[(size, size) for size in ICON_SIZES],
    )

    print("アイコンを生成しました:")
    print("  - resources/icon.ico")
    print("  - resources/icon.png")


if __name__ == "__main__":
    create_production_app_icon()
