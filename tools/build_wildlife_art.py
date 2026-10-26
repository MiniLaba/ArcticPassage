"""Draw the small code-authored wildlife atlas used by the runtime sighting layer."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Code/ArcticPassage/Runtime/assets/wildlife/sightings.png"
W, H = 32, 24
SPECIES = ["bear", "fox", "caribou", "seal", "walrus", "owl", "kittiwake", "sleddog", "whale", "shark"]

def frame(kind: str, phase: int) -> Image.Image:
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    def rect(box, fill, outline=None): d.rectangle(box, fill=fill, outline=outline)
    def ellipse(box, fill, outline=None): d.ellipse(box, fill=fill, outline=outline)
    def line(points, fill, width=1): d.line(points, fill=fill, width=width)
    ink="#334b5a"; snow="#eef1e8"; shade="#aabfc5"; warm="#c8b795"
    leg=phase % 2
    if kind in {"bear", "fox", "caribou", "sleddog"}:
        body={"bear":"#e7ebe3","fox":"#deddd0","caribou":"#8c6e52","sleddog":"#d4d5c9"}[kind]
        highlight={"bear":"#fbf4e4","fox":"#f4eee0","caribou":"#c0a077","sleddog":"#f0e6d2"}[kind]
        ellipse((6,8,24,18),body,ink); ellipse((17,6,27,14),body,ink)
        rect((8,11,20,14),highlight)
        for x in (9,20):
            dx=leg*2 if x==9 else -leg*2
            line([(x,16),(x+dx,20),(x+dx+2,21)],ink,2)
        if kind=="bear":
            ellipse((23,5,26,8),highlight,ink); rect((26,10,29,12),ink); line([(5,12),(2,11)],ink,2)
            rect((19,8,23,9),shade)
        elif kind=="fox":
            line([(7,12),(3,10),(1,12),(4,15),(8,15)],"#c56b48",3)
            rect((25,8,28,10),"#bd6547"); rect((26,11,29,12),"#272f3a"); rect((21,8,23,9),ink)
            rect((10,9,16,10),"#d48b61")
        elif kind=="caribou":
            rect((26,9,30,11),"#e7d1a4"); rect((28,7,29,9),"#e7d1a4")
            line([(23,7),(22,3),(19,2),(21,4),(20,1)],"#d4c09a",2)
            line([(24,7),(26,3),(29,3),(27,5),(30,5)],"#d4c09a",2)
            rect((17,9,22,10),"#a68b67")
        elif kind=="sleddog":
            rect((11,12,21,14),"#b65349",ink); line([(4,15),(3,17),(6,17)],"#d8c89f",2)
            rect((24,7,26,9),"#5d6970"); rect((27,9,29,10),ink); rect((20,8,23,9),"#7d8f91")
    elif kind=="seal":
        ellipse((4,12,27,19),"#788f96",ink); ellipse((21,9,29,16),"#9aadb0",ink)
        ellipse((25,11,26,12),ink); line([(6,17),(2,20),(9,19)],"#667f89",2)
        for x,y in [(10,14),(14,16),(18,13)]: ellipse((x,y,x+1,y+1),"#c4d1cd")
        line([(15,18),(18,22),(21,19)],"#637983",2)
    elif kind=="walrus":
        ellipse((4,10,27,20),"#8a6653",ink); ellipse((22,8,30,15),"#a27a60",ink)
        ellipse((25,10,26,11),ink); line([(27,13),(29,20),(28,20)],"#f0e0be",2)
        line([(24,13),(25,20),(24,20)],"#e5d3b0",2)
        line([(8,17),(4,21),(11,20)],"#735643",2); line([(16,18),(13,22),(20,21)],"#735643",2)
        ellipse((10,12,12,14),"#b38f71")
    elif kind=="owl":
        ellipse((8,3,24,21),"#e7e6d9",ink); ellipse((5,7,12,18),"#bac8c8",ink); ellipse((20,7,27,18),"#bac8c8",ink)
        line([(10,6),(8,1),(14,5)],ink,2); line([(19,5),(24,1),(23,7)],ink,2)
        ellipse((11,8,15,12),"#d39a57"); ellipse((18,8,22,12),"#d39a57")
        ellipse((13,9,14,11),ink); ellipse((19,9,20,11),ink); line([(15,13),(17,15),(19,13)],"#9a6c46",2)
        for y in (16,19): line([(11,y),(14,y+1),(17,y),(20,y+1)],"#bdc9c4")
    elif kind=="kittiwake":
        ellipse((6,9,24,18),"#f0eee3",ink); ellipse((21,7,28,14),"#f8f0db",ink)
        line([(10,11),(17,5),(23,8),(17,10)],"#536a7d",3)
        rect((27,9,31,10),"#c47751"); ellipse((24,9,25,10),ink)
        line([(11,17),(10,20),(13,20)],"#ad6a50",1); line([(17,17),(17,20),(20,20)],"#ad6a50",1)
    elif kind=="whale":
        ellipse((2,13,29,22),"#475f70",ink); ellipse((6,12,24,16),"#617c89")
        line([(4,17),(1,14),(3,20)],"#405b6b",2); line([(27,15),(30,11),(31,17)],"#405b6b",2)
        rect((9,15,11,15),"#8ea6aa"); rect((18,12,19,13),"#a3b7b5")
        if phase==0:
            line([(15,13),(15,9),(14,7)],"#dce7e4",2); line([(15,9),(18,7)],"#dce7e4",1)
    elif kind=="shark":
        ellipse((3,10,28,18),"#647b84",ink); line([(10,11),(15,4),(20,11)],"#647b84",2)
        line([(18,16),(23,22),(25,16)],"#4f6670",2); line([(4,13),(0,10),(1,16)],"#526c75",2)
        rect((7,13,8,14),"#b8cbd0"); line([(11,15),(13,16),(15,15)],"#40535f",1)
        ellipse((24,12,25,13),"#293b47")
        for x in (10,13,16,19,22): rect((x,16,x+1,17),"#b9c9c9")
    # Tiny shared ground cue keeps the animal rooted without touching map collision.
    if kind not in {"whale", "shark", "kittiwake"}:
        ellipse((5,21,27,22),"#71869255")
    return im

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet=Image.new("RGBA",(W*len(SPECIES),H*2))
    for i,name in enumerate(SPECIES):
        sheet.alpha_composite(frame(name,0),(i*W,0))
        sheet.alpha_composite(frame(name,1),(i*W,H))
    sheet.save(OUT)
    print(f"Drew 10 two-frame Arctic wildlife sprites: {OUT}")

if __name__=="__main__": main()
