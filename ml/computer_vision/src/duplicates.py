from pathlib import Path
import hashlib
from collections import defaultdict

ROOT = Path(r"C:\Users\HP\agrisentry-core\ml\computer_vision\data\plantvillage\images")

splits = ["train", "val", "test"]
hashes = defaultdict(list)

for split in splits:
    for image in (ROOT / split).glob("*.jpg"):
        h = hashlib.md5(image.read_bytes()).hexdigest()
        hashes[h].append((split, image.name))

cross_split = []

for h, files in hashes.items():
    split_names = {x[0] for x in files}
    if len(split_names) > 1:
        cross_split.append((h, files))

print(f"Total unique hashes: {len(hashes)}")
print(f"Cross-split duplicate groups: {len(cross_split)}")

for h, files in cross_split:
    print("\nMD5:", h)
    for split, name in files:
        print(f"  {split}: {name}")