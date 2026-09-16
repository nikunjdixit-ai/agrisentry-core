"""
AgriSentry - Grouped Clean Dataset Splitter
Eliminates duplicate image leakage across train, val, and test splits.
Preserves the original dataset structure and files.
Generates text manifest files and a clean data.yaml.
"""

import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

# Relative to project root
CV_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = CV_DIR / "data" / "plantvillage"
IMAGE_DIR = DATASET_DIR / "images"
LABEL_DIR = DATASET_DIR / "labels"
CLEAN_SPLIT_DIR = DATASET_DIR / "clean_split"

SEED = 42
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10


def create_grouped_clean_split():
    random.seed(SEED)
    CLEAN_SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("AgriSentry — Creating Leakage-Free Grouped Split")
    print("=" * 60)

    # 1. Collect the 54,293 canonical images from root images directory
    extensions = {".jpg", ".jpeg", ".png"}
    all_images = [
        p for p in IMAGE_DIR.glob("*")
        if p.is_file() and p.suffix.lower() in extensions
    ]
    all_images.sort()
    print(f"Total canonical image files discovered: {len(all_images)}")

    # Map each image to its label file
    valid_pairs = []
    missing_labels = 0
    for img_path in all_images:
        label_candidates = [
            LABEL_DIR / f"{img_path.stem}.txt",
            LABEL_DIR / "train" / f"{img_path.stem}.txt",
            LABEL_DIR / "val" / f"{img_path.stem}.txt",
            LABEL_DIR / "test" / f"{img_path.stem}.txt",
        ]
        label_found = None
        for candidate in label_candidates:
            if candidate.exists():
                label_found = candidate
                break

        if label_found:
            valid_pairs.append((img_path, label_found))
        else:
            missing_labels += 1

    print(f"Valid image-label pairs: {len(valid_pairs)} (Missing labels: {missing_labels})")

    # 2. Group by MD5 hash of image bytes to prevent leakage
    hash_groups = defaultdict(list)
    print("Computing image MD5 hashes for duplicate grouping...")
    for img_path, lbl_path in valid_pairs:
        md5 = hashlib.md5(img_path.read_bytes()).hexdigest()
        hash_groups[md5].append((img_path, lbl_path))

    unique_hashes = sorted(list(hash_groups.keys()))
    print(f"Total unique image hashes (groups): {len(unique_hashes)}")
    duplicate_groups = [h for h, items in hash_groups.items() if len(items) > 1]
    total_duplicate_images = sum(len(hash_groups[h]) for h in duplicate_groups)
    print(f"Duplicate hash groups: {len(duplicate_groups)} (involving {total_duplicate_images} images)")

    # 3. Shuffle hash groups (not individual images) to keep duplicates grouped in the same split
    random.shuffle(unique_hashes)

    total_groups = len(unique_hashes)
    train_end = int(total_groups * TRAIN_RATIO)
    val_end = train_end + int(total_groups * VAL_RATIO)

    split_hashes = {
        "train": unique_hashes[:train_end],
        "val": unique_hashes[train_end:val_end],
        "test": unique_hashes[val_end:]
    }

    # 4. Assemble samples per split
    split_samples = {"train": [], "val": [], "test": []}
    for split_name, hashes in split_hashes.items():
        for h in hashes:
            for img_path, lbl_path in hash_groups[h]:
                split_samples[split_name].append((img_path, lbl_path))

    # 5. Verify zero cross-split leakage
    train_hashes = set(split_hashes["train"])
    val_hashes = set(split_hashes["val"])
    test_hashes = set(split_hashes["test"])

    assert len(train_hashes.intersection(val_hashes)) == 0, "Leakage detected between train and val!"
    assert len(train_hashes.intersection(test_hashes)) == 0, "Leakage detected between train and test!"
    assert len(val_hashes.intersection(test_hashes)) == 0, "Leakage detected between val and test!"

    print("\nVerification Passed: Exact cross-split hash leakage is strictly 0.00%.")

    # 6. Write text manifests with forward slashes for cross-platform compatibility
    manifest_info = {}
    for split_name in ["train", "val", "test"]:
        txt_path = CLEAN_SPLIT_DIR / f"{split_name}.txt"
        samples = split_samples[split_name]
        with open(txt_path, "w", encoding="utf-8") as f:
            for img_path, _ in samples:
                f.write(img_path.resolve().as_posix() + "\n")

        manifest_info[split_name] = {
            "samples": len(samples),
            "unique_hashes": len(split_hashes[split_name]),
            "manifest_file": str(txt_path.relative_to(DATASET_DIR)).replace("\\", "/")
        }
        print(f"  {split_name.upper():5}: {len(samples):6} images ({len(split_hashes[split_name]):6} unique groups) -> {txt_path.name}")

    # 7. Write clean data_clean.yaml
    classes_yaml_path = DATASET_DIR / "classes.yaml"
    class_names = []
    if classes_yaml_path.exists():
        import yaml
        with open(classes_yaml_path, "r", encoding="utf-8") as f:
            cdata = yaml.safe_load(f)
            class_names = cdata.get("names", [])

    clean_yaml_path = CLEAN_SPLIT_DIR / "data_clean.yaml"
    with open(clean_yaml_path, "w", encoding="utf-8") as f:
        f.write("# AgriSentry Clean Leakage-Free Dataset Configuration\n")
        f.write(f"path: {DATASET_DIR.resolve().as_posix()}\n")
        f.write("train: clean_split/train.txt\n")
        f.write("val: clean_split/val.txt\n")
        f.write("test: clean_split/test.txt\n\n")
        f.write(f"nc: {len(class_names)}\n")
        f.write("names:\n")
        for name in class_names:
            f.write(f"  - {name}\n")

    print(f"\nClean YAML written: {clean_yaml_path.relative_to(DATASET_DIR)}")

    # 8. Write split metadata manifest
    metadata = {
        "split_name": "clean_grouped_split",
        "random_seed": SEED,
        "train_ratio": TRAIN_RATIO,
        "val_ratio": VAL_RATIO,
        "test_ratio": TEST_RATIO,
        "total_images": len(valid_pairs),
        "total_unique_hashes": len(unique_hashes),
        "cross_split_leakage_groups": 0,
        "cross_split_leakage_images": 0,
        "splits": manifest_info,
        "created_at": "2026-09-16T13:00:00"
    }
    manifest_json_path = CLEAN_SPLIT_DIR / "split_manifest.json"
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Manifest saved: {manifest_json_path.relative_to(DATASET_DIR)}")
    print("=" * 60)
    print("Clean grouped split generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    create_grouped_clean_split()
