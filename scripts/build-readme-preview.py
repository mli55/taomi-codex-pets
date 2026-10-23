"""Build README stills and animation from the installed sprites and playback timing.

Requires Python with Pillow and Node.js. Pass --font for a Chinese font when
none of the common system font paths below is available.
"""
from pathlib import Path
import argparse
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PETS = [
    ('junior', '初级拉姆'), ('middle', '中级拉姆'),
    ('senior', '高级拉姆'), ('classic', '超级拉姆'),
    ('super', '神力超级拉姆'), ('water', '神奇水系拉姆'),
    ('wood', '弹力木系拉姆'), ('fire', '霹雳火系拉姆'),
    ('nono-normal', '普通 NoNo'), ('nono', '超能 NoNo'),
    ('nono-annual', '至尊 NoNo'),
]
CELL = (192, 208)
ROW_HEIGHT = 244
BACKGROUND = '#e8ecf2'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'docs/images/pets-hover.gif')
    parser.add_argument('--font', type=Path)
    args = parser.parse_args()
    font_paths = [args.font] if args.font else [
        Path('/System/Library/Fonts/Hiragino Sans GB.ttc'),
        Path('/System/Library/Fonts/PingFang.ttc'),
        Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
        Path('C:/Windows/Fonts/msyh.ttc'),
    ]
    font_path = next((p for p in font_paths if p.is_file()), None)
    if font_path is None:
        parser.error('A Chinese font is required; supply its path with --font.')
    title_font = ImageFont.truetype(str(font_path), 13)
    caption_font = ImageFont.truetype(str(font_path), 11)

    # Reuse the player's actual sequence so the demo cannot drift to a generic
    # GIF frame rate or accidentally omit the third repeat / return to idle.
    program = """
        const fs = require('node:fs'), vm = require('node:vm');
        const context = { window: {} };
        vm.runInNewContext(fs.readFileSync('dist/pet-playback.js', 'utf8'), context);
        console.log(JSON.stringify(context.window.PetPlayback.sequence('jumping')));
    """
    sequence = json.loads(subprocess.check_output(
        ['node', '-e', program], cwd=ROOT, text=True))['frames']
    atlases = [Image.open(ROOT / 'dist/assets' / (key + '.png')).convert('RGBA')
               for key, _ in PETS]
    stills_dir = args.output.parent / 'forms'
    stills_dir.mkdir(parents=True, exist_ok=True)
    for (key, _), atlas in zip(PETS, atlases):
        # Keep the complete first idle cell, including its original transparent
        # padding, so the table preserves the installed poses and proportions.
        atlas.crop((0, 0, *CELL)).save(stills_dir / (key + '.png'), optimize=True)
    frames = []
    for index, pose in enumerate(sequence):
        frame = Image.new('RGB', (4 * CELL[0], 3 * ROW_HEIGHT), BACKGROUND)
        draw = ImageDraw.Draw(frame)
        caption = '待机' if pose['state'] == 'idle' else f'悬停 · {index // 5 + 1}/3'
        for pet_index, ((_, name), atlas) in enumerate(zip(PETS, atlases)):
            x, y = pet_index % 4 * CELL[0], pet_index // 4 * ROW_HEIGHT
            draw.text((x + 8, y + 5), name, font=title_font, fill='#26313e')
            draw.text((x + 8, y + 23), caption, font=caption_font, fill='#596675')
            left, top = pose['column'] * CELL[0], pose['row'] * CELL[1]
            sprite = atlas.crop((left, top, left + CELL[0], top + CELL[1]))
            frame.paste(sprite, (x, y + 36), sprite)
        frames.append(frame)

    # One shared palette keeps colors stable as poses and labels change.
    samples = Image.new('RGB', (384, 366 * len(frames)), BACKGROUND)
    for index, frame in enumerate(frames):
        samples.paste(frame.resize((384, 366)), (0, index * 366))
    palette = samples.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE)
               for frame in frames]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    indexed[0].save(args.output, save_all=True, append_images=indexed[1:],
                    duration=[pose['duration'] for pose in sequence],
                    loop=0, disposal=1, optimize=False)
    print(f'{args.output}: {len(frames)} frames, '
          f'{sum(pose["duration"] for pose in sequence)} ms, '
          f'{args.output.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
