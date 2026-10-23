"""Present the existing four outdoor map previews together, without inventing geography."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONT = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
def font(size):
    return ImageFont.truetype(FONT, size)

if __name__ == '__main__':
    out = Image.new('RGB', (3200, 2820), '#101f2a')
    draw = ImageDraw.Draw(out)
    draw.text((60, 38), '霜灯港 / FROSTHAVN', font=font(70), fill='#f3ead4')
    draw.text((64, 133), '四区域总览 · 夏季地图预览', font=font(33), fill='#a5c6ce')
    maps = [('Town', '01  镇区'), ('Harbor', '02  外港'),
            ('Icefjord', '03  峡湾'), ('Tundra', '04  苔原')]
    for i, (name, label) in enumerate(maps):
        x, y = 60 + (i % 2) * 1570, 230 + (i // 2) * 1250
        draw.text((x, y), label, font=font(35), fill='#f3ead4')
        source = Image.open(ROOT / 'previews' / f'{name}_summer.png').convert('RGB')
        fit = ImageOps.contain(source, (1510, 1135), Image.Resampling.LANCZOS)
        out.paste(fit, (x + (1510-fit.width)//2, y + 65 + (1135-fit.height)//2))
    draw.text((64, 2750), '现有地图分区展示；排列位置不代表实际方位或统一比例。',
              font=font(27), fill='#a5c6ce')
    path = ROOT / 'previews' / 'Frosthavn_RegionalOverview_summer.png'
    out.save(path)
    print(path)
