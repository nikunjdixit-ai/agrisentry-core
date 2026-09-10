from pathlib import Path
import hashlib
import shutil

ROOT = Path(r"C:\Users\HP\agrisentry-core\ml\computer_vision\data\plantvillage")
OUTPUT = ROOT / "clean_test"

splits = ["train", "val", "test"]
hashes = {}

for split in splits:
    image_dir = ROOT / "images" / split

    for image in image_dir.glob("*.jpg"):
        md5 = hashlib.md5(image.read_bytes()).hexdigest()

        if md5 not in hashes:
            hashes[md5] = []

        hashes[md5].append((split, image))

clean_images = []

for md5, files in hashes.items():
    split_names = {split for split, _ in files}

    if len(split_names) == 1:
        split, image = files[0]

        if split == "test":
            clean_images.append(image)

for image in clean_images:
    shutil.copy2(image, OUTPUT / image.name)

print(f"Clean test images created: {len(clean_images)}")
print(f"Output folder: {OUTPUT}")