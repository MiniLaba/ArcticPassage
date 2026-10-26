"""Tiny deterministic RGBA drawing helper for small code-authored pixel sprites."""
from pathlib import Path
import struct
import zlib


def _color(value):
    if isinstance(value, tuple):
        return tuple(value) if len(value) == 4 else (*value, 255)
    text = value.lstrip("#")
    if len(text) == 6:
        text += "ff"
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4, 6))


class Canvas:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.pixels = bytearray(width * height * 4)

    def _set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 4
            self.pixels[offset:offset + 4] = bytes(color)

    def point(self, xy, fill):
        x, y = map(round, xy)
        self._set(x, y, _color(fill))

    def rectangle(self, xy, fill=None, outline=None, width=1):
        x1, y1, x2, y2 = map(round, xy)
        if fill is not None:
            color = _color(fill)
            for y in range(max(0, y1), min(self.height - 1, y2) + 1):
                for x in range(max(0, x1), min(self.width - 1, x2) + 1):
                    self._set(x, y, color)
        if outline is not None:
            for n in range(width):
                self.line((x1 + n, y1 + n, x2 - n, y1 + n), fill=outline)
                self.line((x2 - n, y1 + n, x2 - n, y2 - n), fill=outline)
                self.line((x2 - n, y2 - n, x1 + n, y2 - n), fill=outline)
                self.line((x1 + n, y2 - n, x1 + n, y1 + n), fill=outline)

    def line(self, xy, fill, width=1):
        values = list(xy)
        points = list(zip(values[::2], values[1::2]))
        color = _color(fill)
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            x0, y0, x1, y1 = map(round, (x0, y0, x1, y1))
            dx, dy = abs(x1 - x0), abs(y1 - y0)
            sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
            err = dx - dy
            while True:
                radius = max(0, width - 1) // 2
                for oy in range(-radius, radius + 1):
                    for ox in range(-radius, radius + 1):
                        self._set(x0 + ox, y0 + oy, color)
                if (x0, y0) == (x1, y1):
                    break
                twice = 2 * err
                if twice > -dy:
                    err -= dy
                    x0 += sx
                if twice < dx:
                    err += dx
                    y0 += sy

    def polygon(self, xy, fill=None, outline=None):
        pts = [(round(x), round(y)) for x, y in xy]
        if fill is not None and len(pts) >= 3:
            color = _color(fill)
            min_y, max_y = max(0, min(y for _, y in pts)), min(self.height - 1, max(y for _, y in pts))
            for y in range(min_y, max_y + 1):
                scan = y + 0.5
                xs = []
                for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                    if (y1 <= scan < y2) or (y2 <= scan < y1):
                        xs.append(x1 + (scan - y1) * (x2 - x1) / (y2 - y1))
                xs.sort()
                for left, right in zip(xs[::2], xs[1::2]):
                    for x in range(max(0, round(left)), min(self.width - 1, round(right)) + 1):
                        self._set(x, y, color)
        if outline is not None:
            for a, b in zip(pts, pts[1:] + pts[:1]):
                self.line((*a, *b), fill=outline)

    def ellipse(self, xy, fill=None, outline=None):
        x1, y1, x2, y2 = map(round, xy)
        rx, ry = max(0.5, (x2 - x1) / 2), max(0.5, (y2 - y1) / 2)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        for y in range(max(0, y1), min(self.height - 1, y2) + 1):
            for x in range(max(0, x1), min(self.width - 1, x2) + 1):
                norm = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if fill is not None and norm <= 1:
                    self._set(x, y, _color(fill))
                elif outline is not None and norm <= 1.35:
                    self._set(x, y, _color(outline))

    def save(self, path):
        def chunk(kind, data):
            raw = kind + data
            return struct.pack(">I", len(data)) + raw + struct.pack(">I", zlib.crc32(raw) & 0xffffffff)
        rows = bytearray()
        stride = self.width * 4
        for y in range(self.height):
            rows.append(0)
            rows.extend(self.pixels[y * stride:(y + 1) * stride])
        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0)
        data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")
        Path(path).write_bytes(data)


class Image:
    @staticmethod
    def new(mode, size):
        if mode != "RGBA":
            raise ValueError("Only RGBA sprites are supported")
        return Canvas(*size)


class ImageDraw:
    @staticmethod
    def Draw(canvas):
        return canvas


def png_size(path):
    with open(path, "rb") as stream:
        header = stream.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Not a PNG: {path}")
    return struct.unpack(">II", header[16:24])
