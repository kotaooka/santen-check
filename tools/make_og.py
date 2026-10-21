# SNS 共有用の画像 og.png（1200×630）を作る。
# 使い方：python tools/make_og.py （docs/screenshots/02-play.png と 03-catch.png を使う）
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"   # 番号 0 が日本語
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# 背景：暗い工場の夜（上に青み、下に暖色のぼかし）
img = Image.new("RGB", (W, H), (7, 9, 12))
glow = Image.new("RGB", (W, H), (0, 0, 0))
g = ImageDraw.Draw(glow)
g.ellipse((-200, -420, 900, 300), fill=(28, 37, 48))
g.ellipse((500, 380, 1500, 1000), fill=(34, 24, 16))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(120)), 0.9)

# 右側：ゲーム画面を2枚、少し重ねて置く
def phone(path, h):
    im = Image.open(path).convert("RGB")
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=26, fill=255)
    return im, mask

for path, x, y, h in [(ROOT / "docs/screenshots/03-catch.png", 870, 58, 540), (ROOT / "docs/screenshots/02-play.png", 650, 30, 580)]:
    im, mask = phone(path, h)
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, im.width + 40, im.height + 50), radius=30, fill=(0, 0, 0, 170))
    img.paste(sh.filter(ImageFilter.GaussianBlur(18)), (x - 40, y - 40), sh.filter(ImageFilter.GaussianBlur(18)))
    img.paste(im, (x, y), mask)

# 左側：題字と一文
d = ImageDraw.Draw(img)
gold = (216, 178, 90)
title = ImageFont.truetype(SERIF, 112, index=0)
x = 64
for i, ch in enumerate("三点照合"):
    d.text((x + i * 128, 120), ch, font=title, fill=gold)
d.line((66, 270, 560, 270), fill=(216, 178, 90), width=2)
sub = ImageFont.truetype(SERIF, 34, index=0)
d.text((66, 294), "三つが揃わぬ箱を、", font=sub, fill=(236, 231, 220))
d.text((66, 344), "ひとつも外へ出すな。", font=sub, fill=(236, 231, 220))
body = ImageFont.truetype(SANS, 25, index=0)
for i, line in enumerate(["作業指示書・現品票・現品を見比べて", "出荷か赤箱へ。品質保証の照合ゲーム"]):
    d.text((66, 432 + i * 40), line, font=body, fill=(170, 176, 184))
small = ImageFont.truetype(SANS, 22, index=0)
d.text((66, 556), "kotaooka.github.io/santen-check", font=small, fill=(141, 150, 160))

img.save(ROOT / "og.png", optimize=True)
print("og.png", img.size)
