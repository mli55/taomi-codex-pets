"""Reproduce reviewed loop edits from a pinned, committed atlas revision.

Reorder complete original frames, including every color variant and body mask.
The one expanded expression uses the committed neutral/probe preview, not new
artwork or interpolated poses. All source reads precede output writes, so this
can be rerun without applying a permutation or resampling twice.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import io
import json
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATES = ['idle', 'running-right', 'running-left', 'waving', 'jumping',
          'failed', 'waiting', 'running', 'review']
COUNTS = [6, 8, 8, 4, 5, 8, 6, 6, 6]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/assets')
    args = parser.parse_args()
    plan = json.loads((ROOT / 'scripts/loop-refinements.json').read_text())
    revision = plan['baselineCommit']
    cache = {}

    def read(relative):
        if relative not in cache:
            cache[relative] = subprocess.check_output(
                ['git', 'show', f'{revision}:{relative}'], cwd=ROOT)
        return cache[relative]

    def metadata(filename):
        return json.loads(read('dist/assets/' + filename))

    images = {}

    def image(filename):
        if filename not in images:
            images[filename] = Image.open(io.BytesIO(read('dist/assets/' + filename))).copy()
        return images[filename]

    def tile(atlas, row, column):
        return atlas.crop((column * 192, row * 208, (column + 1) * 192, (row + 1) * 208))

    records = {name: metadata(name) for name in [
        'animation-sources.json', 'ram-level-animation-sources.json',
        'nono-animation-sources.json', 'nono-normal-animation-sources.json',
        'nono-annual-animation-sources.json']}
    clips = json.loads(read('scripts/selected-pet-clips.json'))
    colors = metadata('palette.json')
    nono_colors = metadata('nono-palette.json')
    changed_metadata = set()
    for edit in plan['edits']:
        form, state = edit['form'], edit['state']
        row = STATES.index(state)
        is_nono = form.startswith('nono')
        filename = (form + '-animation-sources.json' if is_nono else
                    'animation-sources.json' if form in ['super', 'water', 'wood', 'fire'] else
                    'ram-level-animation-sources.json')
        rows = records[filename] if is_nono else records[filename][form]['rows']
        entry = rows[row]
        frame_key = 'originalFrames' if is_nono else 'actionFrames'
        old_frames = entry[frame_key]
        if old_frames != edit['fromFrames']:
            raise ValueError(f'{form}/{state}: unexpected baseline selection')
        variant = {'nono': 'super', 'nono-normal': 'normal', 'nono-annual': 'annual'}.get(form, form)
        family = 'nono' if is_nono else 'ram'
        selection = clips[family][variant].setdefault(state, {'sourceState': state})
        if 'columns' in edit:
            indices = edit['columns']
            if len(indices) != COUNTS[row] or any(i < 0 or i >= COUNTS[row] for i in indices):
                raise ValueError(f'{form}/{state}: invalid frame permutation')
            targets = ([form + '.png'] + [form + '-color-' + c['id'] + '.png'
                       for c in nono_colors if c['rgb'] is not None]) if is_nono else (
                       [form + '.png', form + '-neutral.png', form + '-mask.png'] +
                       [form + '-' + key + '.png' for key in colors])
            for target in targets:
                atlas = image(target)
                original = atlas.copy()
                for column, index in enumerate(indices):
                    atlas.paste(tile(original, row, index), (column * 192, row * 208))
            entry[frame_key] = [old_frames[i] for i in indices]
            if not is_nono:
                entry['frames'] = [entry['frames'][i] for i in indices]
        elif 'prepared' in edit:
            # Checked-in, full original poses and their aligned color masks.
            # These are already packed once; rebuilding must not resample them.
            prepared = edit['prepared']
            manifest_path = ROOT / prepared['manifest']
            manifest = json.loads(manifest_path.read_text())
            source = manifest['rows'][state]
            new_frames = edit['frames']
            if source['frames'] != new_frames or len(new_frames) != COUNTS[row]:
                raise ValueError(f'{form}/{state}: prepared selection mismatch')
            if source['action'] != entry['gameAction']:
                raise ValueError(f'{form}/{state}: prepared action mismatch')
            for suffix, key in [('-neutral.png', 'neutral'), ('-mask.png', 'mask')]:
                asset = manifest[key]
                data = (manifest_path.parent / asset['file']).read_bytes()
                if hashlib.sha256(data).hexdigest() != asset['sha256']:
                    raise ValueError(f'{form}/{state}: prepared {key} checksum mismatch')
                sheet = Image.open(io.BytesIO(data))
                source_row = source['sourceRow']
                if sheet.size != (1536, 208 * len(manifest['rows'])):
                    raise ValueError('Invalid prepared source sheet size')
                image(form + suffix).paste(
                    sheet.crop((0, source_row * 208, 1536, (source_row + 1) * 208)),
                    (0, row * 208))
            entry[frame_key] = new_frames
            entry['frames'] = source['absoluteFrames']
            entry['preparedFrames'] = copy.deepcopy(prepared)
            if source['registration'] is None:
                entry.pop('registration', None)
                selection.pop('registration', None)
            else:
                entry['registration'] = copy.deepcopy(source['registration'])
                selection['registration'] = copy.deepcopy(source['registration'])
        else:
            # Source frame coordinates are retained; apply one affine transform
            # to the entire expression and its color mask, never per-frame fit.
            preview = edit['preview']
            source_info = metadata(preview['manifest'])[preview['action']]
            source_start = entry['frames'][0] - old_frames[0]
            new_frames = edit['frames']
            if len(new_frames) != COUNTS[row]:
                raise ValueError('Incorrect expanded expression length')
            scale = preview['scale']
            sx, sy = preview['sourceAnchor']
            dx, dy = preview['targetAnchor']
            affine = (1 / scale, 0, sx - dx / scale, 0, 1 / scale, sy - dy / scale)
            for suffix, source_key in [('-neutral.png', 'image'), ('-mask.png', 'mask')]:
                source = Image.open(io.BytesIO(read('dist/assets/ram-preview/' + source_info[source_key])))
                atlas = image(form + suffix)
                for column, frame in enumerate(new_frames):
                    index = source_info['sourceFrames'].index(source_start + frame)
                    pose = tile(source, index // 8, index % 8)
                    pose = pose.transform((192, 208), Image.Transform.AFFINE, affine,
                                          resample=Image.Resampling.BICUBIC)
                    atlas.paste(pose, (column * 192, row * 208))
            entry[frame_key] = new_frames
            entry['frames'] = [source_start + frame for frame in new_frames]
            entry['preparedPreview'] = copy.deepcopy(preview)
        selection['frames'] = entry[frame_key]
        entry['loopReview'] = edit['reason']
        changed_metadata.add(filename)

    # Validate the complete proposed result before touching the output files.
    for name, atlas in images.items():
        if name.endswith('-mask.png'):
            continue
        for row, count in enumerate(COUNTS):
            for column in range(count):
                box = tile(atlas, row, column).getbbox()
                if box is None or box[0] <= 0 or box[1] <= 0 or box[2] >= 192 or box[3] >= 208:
                    raise ValueError(f'{name}/{row}/{column}: empty or clipped pose')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, atlas in images.items():
        destination = args.output / name
        if destination.exists():
            existing = Image.open(destination)
            if existing.mode == atlas.mode and existing.size == atlas.size and existing.tobytes() == atlas.tobytes():
                continue
        atlas.save(destination, optimize=True)
    for filename in changed_metadata:
        (args.output / filename).write_text(json.dumps(records[filename], ensure_ascii=False, indent=2) + '\n')
    if args.output.resolve() == (ROOT / 'dist/assets').resolve():
        (ROOT / 'scripts/selected-pet-clips.json').write_text(json.dumps(clips, ensure_ascii=False, indent=2) + '\n')
    else:
        (args.output / 'selected-pet-clips.json').write_text(json.dumps(clips, ensure_ascii=False, indent=2) + '\n')
    palette_forms = sorted({e['form'] for e in plan['edits'] if 'preview' in e or 'prepared' in e})
    print(f'{len(plan["edits"])} reviewed rows written. Rebuild palettes: {", ".join(palette_forms)}.')


if __name__ == '__main__':
    main()
