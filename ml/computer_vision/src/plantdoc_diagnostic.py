from pathlib import Path
from collections import Counter

from PIL import Image
from ultralytics import YOLO

MODEL_PATH = Path(
    r"C:\Users\HP\agrisentry-core\runs\plantvillage_yolov8n\weights\best.pt"
)

PLANTDOC_TEST = Path(
    r"C:\PlantDoc\PlantDoc-Dataset-windows-compatible-master\test"
)

IMG_SIZE = 256
CONF_THRESHOLD = 0.25
DEVICE = 0

CLASS_MAPPING = {
    "Apple Scab Leaf": "Apple___Apple_scab",
    "Apple leaf": "Apple___healthy",
    "Apple rust leaf": "Apple___Cedar_apple_rust",

    "Bell_pepper leaf": "Pepper,_bell___healthy",
    "Bell_pepper leaf spot": "Pepper,_bell___Bacterial_spot",

    "Blueberry leaf": "Blueberry___healthy",
    "Cherry leaf": "Cherry___healthy",

    "Corn Gray leaf spot": (
        "Corn___Cercospora_leaf_spot Gray_leaf_spot"
    ),
    "Corn rust leaf": "Corn___Common_rust",

    "Peach leaf": "Peach___healthy",
    "Potato leaf early blight": "Potato___Early_blight",
    "Potato leaf late blight": "Potato___Late_blight",

    "Raspberry leaf": "Raspberry___healthy",
    "Soyabean leaf": "Soybean___healthy",

    "Squash Powdery mildew leaf": "Squash___Powdery_mildew",

    "Tomato Early blight leaf": "Tomato___Early_blight",
    "Tomato leaf": "Tomato___healthy",
    "Tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "Tomato leaf late blight": "Tomato___Late_blight",
    "Tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "Tomato leaf yellow virus": (
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus"
    ),
    "Tomato mold leaf": "Tomato___Leaf_Mold",
    "Tomato Septoria leaf spot": "Tomato___Septoria_leaf_spot",

    "grape leaf": "Grape___healthy",
    "grape leaf black rot": "Grape___Black_rot",
}


def get_images(folder):
    """Return supported image files from a folder."""
    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".JPG", ".JPEG", ".PNG"}

    return [
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix in extensions
    ]


def predict_image(model, image_path):
    """Run YOLO prediction and return highest-confidence class."""
    results = model.predict(
        source=str(image_path),
        imgsz=IMG_SIZE,
        conf=CONF_THRESHOLD,
        device=DEVICE,
        verbose=False,
    )

    result = results[0]

    if result.boxes is None or len(result.boxes) == 0:
        return None, 0.0

    confidences = result.boxes.conf.cpu().tolist()
    class_ids = result.boxes.cls.cpu().tolist()

    best_index = max(
        range(len(confidences)),
        key=lambda i: confidences[i]
    )

    best_conf = confidences[best_index]
    best_class_id = int(class_ids[best_index])

    predicted_class = model.names[best_class_id]

    return predicted_class, best_conf

def main():

    print("=" * 70)
    print("PlantDoc Image-Level Diagnostic")
    print("=" * 70)

    print(f"Model : {MODEL_PATH}")
    print(f"Dataset: {PLANTDOC_TEST}")
    print()

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    if not PLANTDOC_TEST.exists():
        raise FileNotFoundError(
            f"PlantDoc test folder not found: {PLANTDOC_TEST}"
        )

    print("Loading YOLO model...")
    model = YOLO(str(MODEL_PATH))
    print("Model loaded.")
    print()

    total_images = 0
    correct = 0
    no_prediction = 0

    class_results = Counter()
    class_correct = Counter()

    for folder_name, expected_class in CLASS_MAPPING.items():

        class_folder = PLANTDOC_TEST / folder_name

        if not class_folder.exists():
            print(f"[SKIP] Missing folder: {folder_name}")
            continue

        images = get_images(class_folder)

        if not images:
            print(f"[SKIP] No images: {folder_name}")
            continue

        print(
            f"[TEST] {folder_name} "
            f"-> {expected_class} "
            f"({len(images)} images)"
        )

        for image_path in images:

            try:
                # Verify image is readable
                with Image.open(image_path) as img:
                    img.verify()

                predicted_class, confidence = predict_image(
                    model,
                    image_path
                )

            except Exception as e:
                print(
                    f"  [ERROR] {image_path.name}: {e}"
                )
                continue

            total_images += 1
            class_results[expected_class] += 1

            if predicted_class is None:
                no_prediction += 1
                continue

            if predicted_class == expected_class:
                correct += 1
                class_correct[expected_class] += 1

    evaluated = total_images - no_prediction

    print()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(f"Total images       : {total_images}")
    print(f"Images evaluated   : {evaluated}")
    print(f"No prediction     : {no_prediction}")
    print(f"Correct            : {correct}")

    if total_images > 0:
        overall_accuracy = correct / total_images * 100
        print(
            f"Image-level accuracy: "
            f"{overall_accuracy:.2f}%"
        )
    else:
        print("Image-level accuracy: N/A")

    if evaluated > 0:
        conditional_accuracy = correct / evaluated * 100
        print(
            f"Accuracy when predicted: "
            f"{conditional_accuracy:.2f}%"
        )

    print()
    print("=" * 70)
    print("PER-CLASS ACCURACY")
    print("=" * 70)

    for expected_class in sorted(class_results):

        total = class_results[expected_class]
        class_ok = class_correct[expected_class]

        accuracy = (
            class_ok / total * 100
            if total > 0
            else 0
        )

        print(
            f"{expected_class:<55} "
            f"{class_ok:>4}/{total:<4} "
            f"{accuracy:>6.2f}%"
        )

    print()
    print("=" * 70)
    print("IMPORTANT")
    print("=" * 70)
    print(
        "This is an IMAGE-LEVEL diagnostic, NOT object-detection mAP."
    )
    print(
        "PlantDoc Cropped dataset does not contain bounding-box annotations."
    )
    print(
        "No model weights, dataset files, or training configuration were modified."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()