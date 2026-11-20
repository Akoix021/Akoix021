"""Summarize historical YOLOv5 logs and optionally inspect the original dataset ZIP."""

import argparse
import csv
import hashlib
import io
import math
from collections import defaultdict
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


def summarize_logs():
    folder = Path(__file__).resolve().parent / "records"
    print("Run     Epochs  Final precision  Final recall  Final mAP50  Final mAP50-95  Nonfinite loss rows")
    for path in sorted(folder.glob("exp*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, skipinitialspace=True))
        last = rows[-1]
        loss_columns = [field for field in last if field.strip().endswith("_loss")]
        bad = sum(any(not math.isfinite(float(row[key])) for key in loss_columns) for row in rows)
        print(
            f"{path.stem:6} {len(rows):7}  {float(last['metrics/precision']):15.5f}"
            f"  {float(last['metrics/recall']):12.5f}  {float(last['metrics/mAP_0.5']):11.5f}"
            f"  {float(last['metrics/mAP_0.5:0.95']):14.5f}  {bad:19}"
        )


def print_matches(title, groups):
    print(title)
    for group in sorted(groups.values()):
        if len({split for split, _ in group}) > 1:
            print("  " + " = ".join(f"{split}/{filename}" for split, filename in group))


def inspect_dataset(path, compare_pixels):
    digest_groups = defaultdict(list)
    pixels = defaultdict(list)
    if compare_pixels:
        try:
            from PIL import Image
        except ImportError:
            raise SystemExit("Pixel comparison requires Pillow. Install it with 'python -m pip install Pillow'.")
    with ZipFile(path) as archive:
        members = [PurePosixPath(info.filename) for info in archive.infolist() if not info.is_dir()]
        for split in ("train", "valid"):
            root = PurePosixPath("yolov5-master", "datasets", split)
            images = [p for p in members if p.parent == root / "images"]
            if not images:
                raise SystemExit(f"No images under {root / 'images'} in {path}.")
            labels = [
                p for p in members
                if p.parent == root / "labels" and p.suffix == ".txt" and p.name != "classes.txt"
            ]
            boxes = 0
            for label in labels:
                for line in archive.read(str(label)).decode("utf-8-sig").splitlines():
                    if line.strip():
                        cls, *coords = line.split()
                        if cls != "0" or len(coords) != 4 or not all(0 <= float(x) <= 1 for x in coords):
                            raise ValueError(f"Unexpected YOLO annotation in {label}")
                        boxes += 1
            print(f"{split}: {len(images)} images, {len(labels)} label files, {boxes} boxes")
            labeled = {p.stem for p in labels}
            for image in sorted(images):
                if image.stem not in labeled:
                    print(f"  No matching label: {image.name}")
                contents = archive.read(str(image))
                digest_groups[hashlib.sha256(contents).digest()].append((split, image.name))
                if compare_pixels:
                    with Image.open(io.BytesIO(contents)) as source:
                        rgb = source.convert("RGB")
                        key = (rgb.size, hashlib.sha256(rgb.tobytes()).digest())
                    pixels[key].append((split, image.name))
    print_matches("Byte-identical train/validation images:", digest_groups)
    if compare_pixels:
        print_matches("Pixel-identical train/validation images:", pixels)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Optional path to the original yolov5-master.zip.")
    parser.add_argument("--pixels", action="store_true", help="Also compare decoded RGB pixels (requires Pillow).")
    args = parser.parse_args()
    if args.pixels and not args.archive:
        parser.error("--pixels requires --archive")
    summarize_logs()
    if args.archive:
        inspect_dataset(args.archive, args.pixels)
