from pathlib import Path
import re
import sys

# create folders with the date
# copy files into the proper folder

reDate = re.compile('(\d{4}-\d{2}-\d{2})')

workingdir="D:/JPG-Pictures/General Pictures/new"
copytodir="D:/JPG-Pictures/General Pictures"

w = Path(workingdir)
c = Path(copytodir)

wfl = w.glob("*.jpg")

last_dirname = None
last_dir = None


for f in wfl:
    fname=f.name

    m=reDate.search(fname)
    if not m:
        print('Skipping filename: ', fname)
        continue
    
    new_dirname = m.group(1)
    if new_dirname != last_dirname:
        new_dir = c / new_dirname
        if not new_dir.is_dir():
            Path.mkdir(new_dir)
            last_dir = new_dir
    elif last_dir is None:
        print('Skipping - directory exists already - not sure why: ', new_dir)
        continue
    new_file = last_dir / fname
    if not new_file.is_file():
        print(f'{f} -> {new_file}')
        f.rename(new_file)
