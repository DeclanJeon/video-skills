#!/usr/bin/env python3
"""Assemble existing panel PNGs in cut-index order; never generates panels."""
import argparse
import csv
from html import escape
import json
from pathlib import Path
import re

from cp2.ids import parse_cut


def assemble(index: Path, images: Path, out: Path, cols: int, rows: int, caption: str) -> list[dict]:
    if not 1 <= cols <= 8 or not 1 <= rows <= 8 or cols * rows > 8:
        raise ValueError('one sheet must contain at most eight cells')
    if out.suffix.lower() != '.png' or caption not in {'id', 'time', 'dialogue', 'camera'}:
        raise ValueError('expected PNG output and a supported caption')
    images = images.resolve(strict=True)
    cells = []
    used = set()
    with index.open(newline='', encoding='utf-8-sig') as stream:
        for row in csv.DictReader(stream):
            cut = row['cut']
            if parse_cut(cut)[2] is not None:
                raise ValueError(f'expected cut, not segment: {cut}')
            for entry in row['panels'].split(';'):
                panel = entry.strip()
                if re.fullmatch(r'P[1-9][0-9]*', panel):
                    panel = f'{cut}-{panel}'
                if not re.fullmatch(rf'{re.escape(cut)}-P[1-9][0-9]*', panel) or panel in used:
                    raise ValueError(f'invalid or duplicate panel: {panel}')
                used.add(panel)
                file = (images / f'{panel}.png').resolve()
                if not file.is_relative_to(images) or not file.is_file():
                    raise ValueError(f'missing PNG: {panel}')
                label = {'id': panel, 'time': f'{row.get("t_start", "")}–{row.get("t_end", "")} s',
                         'dialogue': row.get('dialogue', ''), 'camera': row.get('camera', '')}[caption]
                cells.append(dict(cell=f'cell-{len(cells)+1:02}', panel=panel, image=str(file), caption=label))
    if not cells or len(cells) > cols*rows:
        raise ValueError('split panel index into nonempty sheets of the requested capacity')
    sidecar = out.with_suffix('.cells.json')
    html_path = out.with_suffix('.html')
    if any(path.exists() or path.is_symlink() for path in (out, html_path, sidecar)):
        raise ValueError('refusing to replace or reuse an existing sheet or mapping')
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        target = html_path
        figures = ''.join(f'<figure><img src="{escape(Path(c["image"]).as_uri(), quote=True)}" '
                          f'alt="{escape(c["panel"])}"><figcaption>{escape(c["caption"])}</figcaption></figure>' for c in cells)
        target.write_text(
            '<!doctype html><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<style>\n'
            f'main {{ display: grid; grid-template-columns: repeat({cols}, 1fr); }}\n'
            'img { max-width: 100%; }\n'
            'figcaption { overflow-wrap: anywhere; }\n'
            '@media (max-width: 40rem) {\n'
            '  body { margin: 1rem; }\n'
            '  main { grid-template-columns: minmax(0, 1fr); gap: 1rem; }\n'
            '  figure { margin: 0; }\n'
            '}\n'
            f'</style><main>{figures}</main>',
            encoding='utf-8',
        )
    else:
        target = out
        sheet = Image.new('RGB', (cols*320, rows*210), '#171717')
        draw = ImageDraw.Draw(sheet)
        for n, cell in enumerate(cells):
            x, y = (n % cols)*320, (n // cols)*210
            with Image.open(cell['image']) as source:
                if source.format != 'PNG':
                    raise ValueError(f'not a PNG: {cell["panel"]}')
                view = ImageOps.contain(source.convert('RGB'), (304, 174))
            sheet.paste(view, (x+(320-view.width)//2, y+4))
            draw.text((x+8, y+183), cell['caption'][:45], fill='white')
        sheet.save(target)
    sidecar.write_text(json.dumps({'sheet': target.name, 'cells': cells}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return cells


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('index', 'images', 'out'):
        p.add_argument(f'--{name}', type=Path, required=True)
    p.add_argument('--cols', type=int, default=4)
    p.add_argument('--rows', type=int, default=2)
    p.add_argument('--caption', choices=('id','time','dialogue','camera'), default='id')
    args = p.parse_args()
    try:
        assemble(args.index, args.images, args.out, args.cols, args.rows, args.caption)
    except (OSError, ValueError, KeyError) as error:
        p.error(str(error))
    data = json.loads(args.out.with_suffix('.cells.json').read_text(encoding='utf-8'))
    print(f'{data["sheet"]}: {len(data["cells"])} cells ({Path(data["sheet"]).suffix[1:]})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
