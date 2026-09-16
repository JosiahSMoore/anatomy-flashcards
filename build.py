#!/usr/bin/env python3
"""
Build script for the Skeletal System flashcard review app.

Reads:
  - template.html   (the HTML/CSS/JS shell, with __CARDS_JSON__ and __IMAGES_JSON__
                      placeholders)
  - cards.json       (array of card objects — see CONTEXT.md for the schema)
  - images/*.{jpg,png}  (every image referenced by a card's "image" field)

Writes:
  - index.html   (single self-contained file — this repo's GitHub Pages root,
                   also just double-clickable to open directly in a browser)

Usage:
    python3 build.py

No dependencies beyond the Python standard library.
"""
import base64
import json
import mimetypes
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT, 'images')
CARDS_PATH = os.path.join(ROOT, 'cards.json')
TEMPLATE_PATH = os.path.join(ROOT, 'template.html')
OUT_PATH = os.path.join(ROOT, 'index.html')


def build_images_map():
    images = {}
    for fname in sorted(os.listdir(IMAGES_DIR)):
        fpath = os.path.join(IMAGES_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        mime, _ = mimetypes.guess_type(fname)
        if not mime or not mime.startswith('image/'):
            continue
        with open(fpath, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode('ascii')
        images[fname] = f"data:{mime};base64,{b64}"
    return images


def main():
    if not os.path.isfile(CARDS_PATH):
        sys.exit(f"Missing {CARDS_PATH}")
    if not os.path.isfile(TEMPLATE_PATH):
        sys.exit(f"Missing {TEMPLATE_PATH}")
    if not os.path.isdir(IMAGES_DIR):
        sys.exit(f"Missing {IMAGES_DIR}/")

    cards = json.load(open(CARDS_PATH, encoding='utf-8'))
    images = build_images_map()

    # Sanity check: every image a card references should exist.
    referenced = {c['image'] for c in cards if c.get('image')}
    missing = sorted(referenced - set(images.keys()))
    if missing:
        print("WARNING: cards.json references images not found in images/:")
        for m in missing:
            print("   -", m)

    unused = sorted(set(images.keys()) - referenced)
    if unused:
        print("Note: images/ contains files no card currently uses:")
        for u in unused:
            print("   -", u)

    cards_json = json.dumps(cards, ensure_ascii=True).replace('</script', '<\\/script')
    images_json = json.dumps(images, ensure_ascii=True).replace('</script', '<\\/script')

    template = open(TEMPLATE_PATH, encoding='utf-8').read()
    final = template.replace('__CARDS_JSON__', cards_json).replace('__IMAGES_JSON__', images_json)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(final)

    size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"Built {OUT_PATH} ({size_mb:.2f} MB) — {len(cards)} cards, {len(images)} images.")


if __name__ == '__main__':
    main()
