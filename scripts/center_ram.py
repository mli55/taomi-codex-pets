"""Center elemental Ram animation rows without changing their internal motion."""
from pathlib import Path
import argparse
from PIL import Image

COUNTS=[6,8,8,4,5,8,6,6,6]
def center(assets):
    for form in ['water','wood','fire']:
        neutral=Image.open(assets/f'{form}-neutral.png').convert('RGBA')
        mask=Image.open(assets/f'{form}-mask.png').convert('RGB')
        output=Image.new('RGBA',neutral.size)
        mask_output=Image.new('RGB',mask.size)
        offsets=[]
        for row,count in enumerate(COUNTS):
            boxes=[]
            for col in range(count):
                frame=neutral.crop((col*192,row*208,(col+1)*192,(row+1)*208))
                boxes.append(frame.getbbox())
            # One translation per animation, preserving frame-to-frame motion.
            left=min(b[0] for b in boxes);right=max(b[2] for b in boxes)
            dx=round(96-(left+right)/2)
            assert left+dx>=0 and right+dx<=192
            offsets.append(dx)
            for col in range(count):
                box=(col*192,row*208,(col+1)*192,(row+1)*208)
                for source,target in [(neutral,output),(mask,mask_output)]:
                    cell=Image.new(source.mode,(192,208))
                    cell.paste(source.crop(box),(dx,0))
                    target.paste(cell,(col*192,row*208))
        output.save(assets/f'{form}-neutral.png',optimize=True)
        mask_output.save(assets/f'{form}-mask.png',optimize=True)
        print(form,'horizontal row offsets:',offsets)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--assets',type=Path,default=Path('dist/assets'));center(p.parse_args().assets)
