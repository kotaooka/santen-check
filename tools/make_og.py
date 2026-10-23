# SNS 共有用の画像 og.png（1200×630）を作る。
# 使い方：python tools/make_og.py （docs/screenshots/02-play.png と 03-catch.png を使う）
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"    # 太字のゴシック（番号 0 が日本語）
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# 背景：QC Workbench の青（#1d5c96）
img = Image.new("RGB", (W, H), (29, 92, 150))
glow = Image.new("RGB", (W, H), (0, 0, 0))
g = ImageDraw.Draw(glow)
# 下に向けて少し暗くする（DESIGN.md 1.5）
for y in range(H):
    k = y / H
    g.line((0, y, W, y), fill=(int(29 - 9 * k), int(92 - 26 * k), int(150 - 40 * k)))
img = glow

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
white = (255, 255, 255)
title = ImageFont.truetype(BOLD, 112, index=0)
x = 64
for i, ch in enumerate("三点照合"):
    d.text((x + i * 124, 120), ch, font=title, fill=white)
d.line((66, 270, 560, 270), fill=(255, 255, 255), width=2)
sub = ImageFont.truetype(BOLD, 34, index=0)
d.text((66, 294), "三つがそろわない箱は、", font=sub, fill=white)
d.text((66, 344), "外へ出さない。", font=sub, fill=white)
body = ImageFont.truetype(SANS, 25, index=0)
for i, line in enumerate(["作業指示書・現品票・現品を見比べて", "出荷するか止めるか。品質保証の照合ゲーム"]):
    d.text((66, 432 + i * 40), line, font=body, fill=(214, 228, 242))
small = ImageFont.truetype(SANS, 22, index=0)
d.text((66, 556), "kotaooka.github.io/santen-check", font=small, fill=(190, 210, 230))

img.save(ROOT / "og.png", optimize=True)
print("og.png", img.size)
