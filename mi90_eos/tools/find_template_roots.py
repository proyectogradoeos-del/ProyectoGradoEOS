import os
from xml.etree import ElementTree as ET
root = r"c:\mi_odoo_addons\mi90_eos\views"
results = []
for fname in os.listdir(root):
    if not fname.lower().endswith('.xml'):
        continue
    fpath = os.path.join(root, fname)
    try:
        tree = ET.parse(fpath)
        root_tag = tree.getroot().tag
        results.append((fname, root_tag))
    except Exception as e:
        results.append((fname, 'PARSE_ERROR: '+str(e)))

for fname, tag in results:
    print(f"{fname}: {tag}")
