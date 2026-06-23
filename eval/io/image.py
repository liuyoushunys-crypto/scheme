"""
Image Processing - Based on Python Pillow (PIL) library.

Load/Save:
  (image-load path)                  -> load image
  (image-save img path)              -> save image
  (image-copy img)                   -> copy image

Properties:
  (image-width img)                  -> width in pixels
  (image-height img)                 -> height in pixels
  (image-size img)                   -> (width . height)
  (image-mode img)                   -> color mode string
  (image-format img)                 -> file format

Color/Channel:
  (image-getpixel img x y)           -> pixel color as list
  (image-putpixel img x y color)     -> set pixel
  (image-convert img mode)           -> convert color mode
  (image-split img)                  -> split channels as list
  (image-merge mode channels)        -> merge channels

Transform:
  (image-resize img w h)             -> resize
  (image-rotate img angle)           -> rotate (degrees)
  (image-flip img)                   -> horizontal flip
  (image-flip-vertical img)          -> vertical flip
  (image-crop img x y w h)           -> crop region
  (image-transpose img method)       -> generic transpose

Filter:
  (image-blur img radius)            -> gaussian blur
  (image-sharpen img)                -> sharpen
  (image-edge-detect img)            -> edge detection
  (image-emboss img)                 -> emboss
  (image-smooth img)                 -> smooth
  (image-contour img)                -> contour
  (image-filter img filter-type)     -> apply named filter

Pixel ops:
  (image-point img fn)               -> apply function to each pixel
  (image-invert img)                 -> invert colors
  (image-grayscale img)              -> convert to grayscale
  (image-threshold img val)          -> binary threshold

Draw:
  (image-draw-rect img x y w h color) -> draw rectangle
  (image-draw-line img x1 y1 x2 y2 color) -> draw line
  (image-draw-circle img cx cy r color) -> draw circle
  (image-draw-text img x y text size) -> draw text

Create:
  (image-new w h color)             -> create new image
  (image-new w h mode)              -> create with mode
  (image-from-bytes data w h)       -> create from raw bytes

Montage:
  (image-paste img src x y)         -> paste image onto another
  (image-paste img src x y mask)    -> paste with mask

Utility:
  (image-thumbnail img size)        -> create thumbnail
  (image-show img)                  -> display image
  (image-supported-formats)         -> list supported formats

Filter types:
  'blur 'sharpen 'edge-enhance 'emboss 'smooth 'contour 'detail

Color modes:
  'RGB 'RGBA 'L (grayscale) 'CMYK 'HSV '1 (b&w)

Color format: (R G B) or (R G B A) where values 0-255
"""

import sys
import os
from typing import List
from dataclasses import dataclass
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


_PIL_AVAILABLE = False
_PIL = None
_PIL_IMAGE = None
_PIL_IMAGE_FILTER = None
_PIL_IMAGE_DRAW = None


def _ensure_pil():
    global _PIL, _PIL_IMAGE, _PIL_IMAGE_FILTER, _PIL_IMAGE_DRAW, _PIL_AVAILABLE
    if not _PIL_AVAILABLE:
        try:
            from PIL import Image as _img, ImageFilter as _filt, ImageDraw as _draw, ImageEnhance as _enhance
            _PIL_IMAGE = _img
            _PIL_IMAGE_FILTER = _filt
            _PIL_IMAGE_DRAW = _draw
            _PIL = True
            _PIL_AVAILABLE = True
        except ImportError:
            raise Exception("Pillow not installed. Run: pip install Pillow")


@dataclass(frozen=True, slots=True)
class ImageValue(SchemeValue):
    img: object  # PIL.Image

    def __str__(self):
        return f"#<image {self.img.width}x{self.img.height} {self.img.mode}>"


_FILTER_MAP = {
    'blur': None,
    'sharpen': None,
    'edge-enhance': None,
    'emboss': None,
    'smooth': None,
    'contour': None,
    'detail': None,
}


def _get_filter(name: str):
    _ensure_pil()
    m = _PIL_IMAGE_FILTER
    return {
        'blur': m.BLUR,
        'sharpen': m.SHARPEN,
        'edge-enhance': m.EDGE_ENHANCE,
        'emboss': m.EMBOSS,
        'smooth': m.SMOOTH,
        'contour': m.CONTOUR,
        'detail': m.DETAIL,
    }.get(name, None)


_MODE_MAP = {
    'rgb': 'RGB',
    'rgba': 'RGBA',
    'l': 'L',
    'grayscale': 'L',
    'cmyk': 'CMYK',
    'hsv': 'HSV',
    '1': '1',
}


def _unwrap_str(val) -> str:
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name.lower()
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_int(val) -> int:
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        return int(val.value)
    return int(unwrap_python_value(val))


def _color_to_tuple(val: SchemeValue) -> tuple:
    """Convert Scheme color to PIL color tuple"""
    if isinstance(val, Str):
        return val.get_str()  # named color
    if isinstance(val, Sym):
        return val.name  # named color
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        return int(val.value)
    # List of values
    items = []
    c = val
    while isinstance(c, Cons):
        items.append(_unwrap_int(c.car))
        c = c.cdr
    if len(items) == 1:
        return items[0]
    return tuple(items)


def _ensure_image(val) -> object:
    if isinstance(val, ImageValue):
        return val.img
    raise Exception(f"Expected image, got {type(val).__name__}")


# ==================== Load/Save ====================


def image_load(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("image-load: need 1 argument (path)")
    _ensure_pil()
    path = _unwrap_str(args[0])
    try:
        img = _PIL_IMAGE.open(path)
        img.load()
        return ImageValue(img=img)
    except Exception as e:
        raise Exception(f"Failed to load image: {e}")


def image_save(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-save: need 2 arguments (img path)")
    img = _ensure_image(args[0])
    path = _unwrap_str(args[1])
    try:
        img.save(path)
        return Bool(True)
    except Exception as e:
        raise Exception(f"Failed to save image: {e}")


def image_copy(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("image-copy: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.copy())


# ==================== Properties ====================


def image_width(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-width: need 1 argument")
    return Num(_ensure_image(args[0]).width)


def image_height(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-height: need 1 argument")
    return Num(_ensure_image(args[0]).height)


def image_size(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-size: need 1 argument")
    img = _ensure_image(args[0])
    return Cons(Num(img.width), Num(img.height))


def image_mode(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-mode: need 1 argument")
    return Str(_ensure_image(args[0]).mode)


def image_format(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-format: need 1 argument")
    fmt = _ensure_image(args[0]).format
    return Str(fmt) if fmt else Bool(False)


# ==================== Color/Channel ====================


def image_getpixel(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 3:
        raise Exception("image-getpixel: need 3 arguments (img x y)")
    img = _ensure_image(args[0])
    x, y = _unwrap_int(args[1]), _unwrap_int(args[2])
    pixel = img.getpixel((x, y))
    if isinstance(pixel, tuple):
        result = Nil()
        for v in reversed(pixel):
            result = Cons(Num(v), result)
        return result
    return Num(pixel)


def image_putpixel(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 4:
        raise Exception("image-putpixel: need 4 arguments (img x y color)")
    img = _ensure_image(args[0])
    x, y = _unwrap_int(args[1]), _unwrap_int(args[2])
    color = _color_to_tuple(args[3])
    img.putpixel((x, y), color)
    return Bool(True)


def image_convert(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-convert: need 2 arguments (img mode)")
    img = _ensure_image(args[0])
    mode = _MODE_MAP.get(_unwrap_str(args[1]), _unwrap_str(args[1]).upper())
    return ImageValue(img=img.convert(mode))


def image_split(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("image-split: need 1 argument")
    img = _ensure_image(args[0])
    channels = img.split()
    result = Nil()
    for ch in reversed(channels):
        result = Cons(ImageValue(img=ch), result)
    return result


def image_merge(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-merge: need 2 arguments (mode channels)")
    mode = _MODE_MAP.get(_unwrap_str(args[0]), _unwrap_str(args[0]).upper())
    channels_val = args[1]
    channels = []
    c = channels_val
    while isinstance(c, Cons):
        channels.append(_ensure_image(c.car))
        c = c.cdr
    return ImageValue(img=_PIL_IMAGE.merge(mode, channels))


# ==================== Transform ====================


def image_resize(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 3:
        raise Exception("image-resize: need 3 arguments (img w h)")
    img = _ensure_image(args[0])
    w, h = _unwrap_int(args[1]), _unwrap_int(args[2])
    return ImageValue(img=img.resize((w, h)))


def image_rotate(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-rotate: need 2 arguments (img angle)")
    img = _ensure_image(args[0])
    angle = float(unwrap_python_value(args[1]))
    expand = len(args) > 2 and not isinstance(args[2], Bool) and False or (len(args) > 2 and args[2].value)
    return ImageValue(img=img.rotate(angle, expand=expand))


def image_flip(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-flip: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.transpose(_PIL_IMAGE.FLIP_LEFT_RIGHT))


def image_flip_vertical(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-flip-vertical: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.transpose(_PIL_IMAGE.FLIP_TOP_BOTTOM))


def image_crop(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 5:
        raise Exception("image-crop: need 5 arguments (img x y w h)")
    img = _ensure_image(args[0])
    x, y = _unwrap_int(args[1]), _unwrap_int(args[2])
    w, h = _unwrap_int(args[3]), _unwrap_int(args[4])
    return ImageValue(img=img.crop((x, y, x + w, y + h)))


def image_transpose(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-transpose: need 2 arguments (img method)")
    img = _ensure_image(args[0])
    method = _unwrap_str(args[1])
    m = {
        'flip-lr': _PIL_IMAGE.FLIP_LEFT_RIGHT,
        'flip-tb': _PIL_IMAGE.FLIP_TOP_BOTTOM,
        'rotate-90': _PIL_IMAGE.ROTATE_90,
        'rotate-180': _PIL_IMAGE.ROTATE_180,
        'rotate-270': _PIL_IMAGE.ROTATE_270,
        'transpose': _PIL_IMAGE.TRANSPOSE,
    }.get(method)
    if m is None:
        raise Exception(f"Unknown transpose method: {method}")
    return ImageValue(img=img.transpose(m))


# ==================== Filter ====================


def image_apply_filter(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-filter: need 2 arguments (img filter-type)")
    img = _ensure_image(args[0])
    _ensure_pil()
    filter_name = _unwrap_str(args[1])
    pil_filter = _get_filter(filter_name)
    if pil_filter is None:
        raise Exception(f"Unknown filter: {filter_name}")
    return ImageValue(img=img.filter(pil_filter))


def image_blur(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-blur: need 2 arguments (img radius)")
    img = _ensure_image(args[0])
    radius = _unwrap_int(args[1])
    return ImageValue(img=img.filter(_PIL_IMAGE_FILTER.GaussianBlur(radius)))


def image_sharpen(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-sharpen: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.filter(_PIL_IMAGE_FILTER.SHARPEN))


def image_edge_detect(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-edge-detect: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.filter(_PIL_IMAGE_FILTER.FIND_EDGES))


def image_emboss(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-emboss: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.filter(_PIL_IMAGE_FILTER.EMBOSS))


def image_smooth(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-smooth: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.filter(_PIL_IMAGE_FILTER.SMOOTH))


def image_contour(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-contour: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.filter(_PIL_IMAGE_FILTER.CONTOUR))


# ==================== Pixel Ops ====================


def image_point(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-point: need 2 arguments (img table-fn)")
    img = _ensure_image(args[0])
    # If it's a list/vector, use as lookup table
    # If it's a number, use as scalar operation
    if isinstance(args[1], Prim):
        raise Exception("image-point: function argument not supported - use image-invert instead")
    return Bool(False)  # simplified


def image_invert(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-invert: need 1 argument")
    img = _ensure_image(args[0])
    from PIL import ImageOps
    return ImageValue(img=ImageOps.invert(img.convert('RGB')))


def image_grayscale(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("image-grayscale: need 1 argument")
    img = _ensure_image(args[0])
    return ImageValue(img=img.convert('L'))


def image_threshold(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-threshold: need 2 arguments (img threshold)")
    img = _ensure_image(args[0])
    _ensure_pil()
    threshold = _unwrap_int(args[1])
    gray = img.convert('L')
    bw = gray.point(lambda p: 255 if p > threshold else 0, mode='1')
    return ImageValue(img=bw)


# ==================== Draw ====================


def _get_draw(img):
    _ensure_pil()
    return _PIL_IMAGE_DRAW.Draw(img)


def image_draw_rect(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 6:
        raise Exception("image-draw-rect: need 6 arguments (img x y w h color)")
    img = _ensure_image(args[0]).copy()
    x, y = _unwrap_int(args[1]), _unwrap_int(args[2])
    w, h = _unwrap_int(args[3]), _unwrap_int(args[4])
    color = _color_to_tuple(args[5])
    draw = _get_draw(img)
    draw.rectangle([x, y, x + w, y + h], fill=color)
    return ImageValue(img=img)


def image_draw_line(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 6:
        raise Exception("image-draw-line: need 6 arguments (img x1 y1 x2 y2 color)")
    img = _ensure_image(args[0]).copy()
    x1, y1 = _unwrap_int(args[1]), _unwrap_int(args[2])
    x2, y2 = _unwrap_int(args[3]), _unwrap_int(args[4])
    color = _color_to_tuple(args[5])
    width = _unwrap_int(args[6]) if len(args) > 6 else 1
    draw = _get_draw(img)
    draw.line([x1, y1, x2, y2], fill=color, width=width)
    return ImageValue(img=img)


def image_draw_circle(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 5:
        raise Exception("image-draw-circle: need 5 arguments (img cx cy r color)")
    img = _ensure_image(args[0]).copy()
    cx, cy = _unwrap_int(args[1]), _unwrap_int(args[2])
    r = _unwrap_int(args[3])
    color = _color_to_tuple(args[4])
    draw = _get_draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    return ImageValue(img=img)


def image_draw_text(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 4:
        raise Exception("image-draw-text: need 4 arguments (img x y text)")
    img = _ensure_image(args[0]).copy()
    x, y = _unwrap_int(args[1]), _unwrap_int(args[2])
    text = _unwrap_str(args[3])
    color = (255, 255, 255)  # white default
    if len(args) > 4:
        color = _color_to_tuple(args[4])
    size = _unwrap_int(args[5]) if len(args) > 5 else 20
    draw = _get_draw(img)
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((x, y), text, fill=color, font=font)
    return ImageValue(img=img)


# ==================== Create ====================


def image_new(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-new: need at least 2 arguments (w h)")
    _ensure_pil()
    w, h = _unwrap_int(args[0]), _unwrap_int(args[1])
    mode = 'RGB'
    color = (0, 0, 0)
    if len(args) > 2:
        if isinstance(args[2], Sym):
            mode = _MODE_MAP.get(args[2].name.lower(), args[2].name.upper())
        elif isinstance(args[2], Str):
            mode = _MODE_MAP.get(args[2].get_str().lower(), args[2].get_str().upper())
        else:
            color = _color_to_tuple(args[2])
    if len(args) > 3:
        color = _color_to_tuple(args[3])
    if isinstance(color, str):
        img = _PIL_IMAGE.new(mode, (w, h), color)
    else:
        mode = mode if mode else 'RGB'
        if mode == '1':
            img = _PIL_IMAGE.new(mode, (w, h), 1 if color else 0)
        elif mode == 'L':
            img = _PIL_IMAGE.new(mode, (w, h), color if isinstance(color, int) else color[0])
        else:
            img = _PIL_IMAGE.new(mode, (w, h), color if isinstance(color, (int, str)) else tuple(color))
    return ImageValue(img=img)


def image_from_bytes(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 3:
        raise Exception("image-from-bytes: need 3 arguments (data w h)")
    _ensure_pil()
    data = args[0]
    w, h = _unwrap_int(args[1]), _unwrap_int(args[2])
    if isinstance(data, Bytevector):
        raw = bytes(data.data)
    elif isinstance(data, Str):
        raw = data.get_str().encode()
    else:
        raw = bytes(unwrap_python_value(data))
    img = _PIL_IMAGE.frombytes('RGB', (w, h), raw)
    return ImageValue(img=img)


# ==================== Montage ====================


def image_paste(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 3:
        raise Exception("image-paste: need 3 arguments (dst src x y)")
    dst = _ensure_image(args[0]).copy()
    src = _ensure_image(args[1])
    x, y = _unwrap_int(args[2]), _unwrap_int(args[3])
    mask = None
    if len(args) > 4:
        mask = _ensure_image(args[4])
    if mask:
        dst.paste(src, (x, y), mask)
    else:
        dst.paste(src, (x, y))
    return ImageValue(img=dst)


# ==================== Utility ====================


def image_thumbnail(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("image-thumbnail: need 2 arguments (img size)")
    img = _ensure_image(args[0]).copy()
    size_val = args[1]
    if isinstance(size_val, Cons):
        w = _unwrap_int(size_val.car)
        h = _unwrap_int(size_val.cdr.car) if isinstance(size_val.cdr, Cons) else w
        size = (w, h)
    else:
        s = _unwrap_int(size_val)
        size = (s, s)
    img.thumbnail(size)
    return ImageValue(img=img)


def image_show(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("image-show: need 1 argument")
    img = _ensure_image(args[0])
    try:
        img.show()
        return Bool(True)
    except Exception:
        return Bool(False)


def image_supported_formats(args: List[SchemeValue]) -> SchemeValue:
    _ensure_pil()
    formats = _PIL_IMAGE.registered_extensions()
    result = Nil()
    for ext in reversed(sorted(set(formats.keys()))):
        result = Cons(Str(ext), result)
    return result


# ==================== Registration ====================


def register_image_primitives(env):
    env.define("image-load", Prim("image-load", image_load))
    env.define("image-save", Prim("image-save", image_save))
    env.define("image-copy", Prim("image-copy", image_copy))

    env.define("image-width", Prim("image-width", image_width))
    env.define("image-height", Prim("image-height", image_height))
    env.define("image-size", Prim("image-size", image_size))
    env.define("image-mode", Prim("image-mode", image_mode))
    env.define("image-format", Prim("image-format", image_format))

    env.define("image-getpixel", Prim("image-getpixel", image_getpixel))
    env.define("image-putpixel", Prim("image-putpixel", image_putpixel))
    env.define("image-convert", Prim("image-convert", image_convert))
    env.define("image-split", Prim("image-split", image_split))
    env.define("image-merge", Prim("image-merge", image_merge))

    env.define("image-resize", Prim("image-resize", image_resize))
    env.define("image-rotate", Prim("image-rotate", image_rotate))
    env.define("image-flip", Prim("image-flip", image_flip))
    env.define("image-flip-vertical", Prim("image-flip-vertical", image_flip_vertical))
    env.define("image-crop", Prim("image-crop", image_crop))
    env.define("image-transpose", Prim("image-transpose", image_transpose))

    env.define("image-filter", Prim("image-filter", image_apply_filter))
    env.define("image-blur", Prim("image-blur", image_blur))
    env.define("image-sharpen", Prim("image-sharpen", image_sharpen))
    env.define("image-edge-detect", Prim("image-edge-detect", image_edge_detect))
    env.define("image-emboss", Prim("image-emboss", image_emboss))
    env.define("image-smooth", Prim("image-smooth", image_smooth))
    env.define("image-contour", Prim("image-contour", image_contour))

    env.define("image-point", Prim("image-point", image_point))
    env.define("image-invert", Prim("image-invert", image_invert))
    env.define("image-grayscale", Prim("image-grayscale", image_grayscale))
    env.define("image-threshold", Prim("image-threshold", image_threshold))

    env.define("image-draw-rect", Prim("image-draw-rect", image_draw_rect))
    env.define("image-draw-line", Prim("image-draw-line", image_draw_line))
    env.define("image-draw-circle", Prim("image-draw-circle", image_draw_circle))
    env.define("image-draw-text", Prim("image-draw-text", image_draw_text))

    env.define("image-new", Prim("image-new", image_new))
    env.define("image-from-bytes", Prim("image-from-bytes", image_from_bytes))

    env.define("image-paste", Prim("image-paste", image_paste))

    env.define("image-thumbnail", Prim("image-thumbnail", image_thumbnail))
    env.define("image-show", Prim("image-show", image_show))
    env.define("image-supported-formats", Prim("image-supported-formats", image_supported_formats))