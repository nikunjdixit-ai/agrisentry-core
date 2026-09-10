from pathlib import Path
import random
import shutil

DATASET = Path(__file__).resolve().parent.parent / "data" / "plantvillage"

IMAGE_DIR = DATASET / "images"
LABEL_DIR = DATASET / "labels"

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

SEED = 42

random.seed(SEED)

images = sorted(
    list(IMAGE_DIR.glob("*.jpg")) +
    list(IMAGE_DIR.glob("*.jpeg")) +
    list(IMAGE_DIR.glob("*.png"))
)

print(f"Images found: {len(images)}")

pairs = []

for image in images:
    label = LABEL_DIR / f"{image.stem}.txt"

    if label.exists():
        pairs.append((image, label))

print(f"Valid image-label pairs: {len(pairs)}")

if len(images) != len(pairs):
    raise RuntimeError(
        f"Mismatch detected: {len(images)} images but "
        f"{len(pairs)} valid labels."
    )

random.shuffle(pairs)

total = len(pairs)

train_end = int(total * TRAIN_RATIO)
val_end = train_end + int(total * VAL_RATIO)

splits = {
    "train": pairs[:train_end],
    "val": pairs[train_end:val_end],
    "test": pairs[val_end:]
}

for split in splits:
    (IMAGE_DIR / split).mkdir(parents=True, exist_ok=True)
    (LABEL_DIR / split).mkdir(parents=True, exist_ok=True)

for split, items in splits.items():

    print(f"\nCreating {split}: {len(items)} samples")

    for image, label in items:

        shutil.copy2(
            image,
            IMAGE_DIR / split / image.name
        )

        shutil.copy2(
            label,
            LABEL_DIR / split / label.name
        )

print("\n========== DATASET SUMMARY ==========")

for split in splits:

    image_count = len(list((IMAGE_DIR / split).glob("*")))
    label_count = len(list((LABEL_DIR / split).glob("*.txt")))

    print(
        f"{split.upper():5} | "
        f"Images: {image_count:6} | "
        f"Labels: {label_count:6}"
    )

print("\nDataset split completed successfully.")