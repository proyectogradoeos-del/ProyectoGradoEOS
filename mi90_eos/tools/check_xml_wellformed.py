import os
import xml.etree.ElementTree as ET

root = r"c:\mi_odoo_addons\mi90_eos"
errors = []
for dirpath, dirnames, filenames in os.walk(root):
    for fname in filenames:
        if fname.lower().endswith('.xml'):
            fpath = os.path.join(dirpath, fname)
            try:
                ET.parse(fpath)
            except ET.ParseError as e:
                errors.append((fpath, str(e)))

if errors:
    print('FOUND_ERRORS')
    for fpath, err in errors:
        print(f'FILE: {fpath}')
        print(f'ERROR: {err}')
else:
    print('ALL_OK')
