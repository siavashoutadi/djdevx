import colorsys


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
    )


def generate_palette(base_hex):
    base_rgb = hex_to_rgb(base_hex)
    hue, lightness, saturation = colorsys.rgb_to_hls(*base_rgb)

    lightness_scale = {
        50: min(1, lightness + (1 - lightness) * 0.80),
        100: min(1, lightness + (1 - lightness) * 0.65),
        200: min(1, lightness + (1 - lightness) * 0.45),
        300: min(1, lightness + (1 - lightness) * 0.30),
        400: min(1, lightness + (1 - lightness) * 0.12),
        500: lightness,
        600: max(0, lightness * 0.88),
        700: max(0, lightness * 0.75),
        800: max(0, lightness * 0.56),
        900: max(0, lightness * 0.35),
    }

    palette = {}
    for shade, new_l in lightness_scale.items():
        new_rgb = colorsys.hls_to_rgb(hue, new_l, saturation)
        palette[shade] = rgb_to_hex(new_rgb)

    return palette
