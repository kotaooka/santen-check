# アプリのアイコン（icons/*.png）を作る。使い方：python tools/make_icons.py
# 段ボール箱に金色のチェック。maskable は端が切られても見えるよう、絵を中央 6 割に収める
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent

def svg(pad):
    # pad：絵の周りの余白（0〜1。viewBox 64 に対する割合）
    s = 1 - pad * 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="100%" height="100%">
  <defs><radialGradient id="bg" cx="50%" cy="30%" r="80%"><stop offset="0" stop-color="#1c2530"/><stop offset="1" stop-color="#07090c"/></radialGradient>
  <linearGradient id="box" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d0a66e"/><stop offset="1" stop-color="#9c7743"/></linearGradient></defs>
  <rect width="64" height="64" fill="url(#bg)"/>
  <g transform="translate({32 - 32 * s} {32 - 32 * s}) scale({s})">
    <path d="M12 26 L52 26 L52 54 Q52 56 50 56 L14 56 Q12 56 12 54 Z" fill="url(#box)"/>
    <path d="M12 26 L19 15 L45 15 L52 26 Z" fill="#c8a06a"/>
    <path d="M12 26 L52 26" stroke="#8a6838" stroke-width="1.2"/>
    <rect x="28" y="26" width="8" height="30" fill="#e8d7b0" opacity=".45"/>
    <path d="M21 41 L29 49 L44 33" fill="none" stroke="#f1d38a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>'''

OUT = [("icon-192.png", 192, 0.06), ("icon-512.png", 512, 0.06), ("icon-maskable-512.png", 512, 0.2), ("apple-touch-icon.png", 180, 0.08)]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, size, pad in OUT:
            pg = await b.new_page(viewport={"width": size, "height": size})
            await pg.set_content(f'<html><body style="margin:0">{svg(pad)}</body></html>')
            await pg.screenshot(path=str(ROOT / "icons" / name), omit_background=False)
            await pg.close()
            print(name, size)
        await b.close()

asyncio.run(main())
