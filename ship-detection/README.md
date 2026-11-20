# Underwater shipwreck detection experiments

This project explored how a single-class YOLOv5 detector localizes ship remains in underwater photographs. The annotation class is `ship`. The recovered experiment files cover bounding-box loss variants and a SimAM attention layer. The examples inspected include submerged hulls and wreckage. The project report describes image labeling, a switch from CIoU to DIoU, and separate image-enhancement and generation experiments.

This folder preserves the [detector source](detector/), six epoch logs, and the model and dataset configurations. You can inspect the logs in Python without installing a machine learning framework. The photos and pretrained checkpoints remain in the original archive.

## Reproduce the record checks

From this directory, run

```powershell
py -3 review_records.py
```

The script prints final-epoch metrics and the number of rows containing a nonfinite loss for each run. If you have the original archive, add its path to count images and annotations and compare image hashes across the two splits.

```powershell
py -3 review_records.py --archive "C:\path\to\yolov5-master.zip"
```

Both checks use the Python standard library. They read CSV, annotation text, and image bytes. To compare decoded image pixels as well, install Pillow in the same environment and append `--pixels` to the archive command. No checkpoint is loaded.

## Dataset recovered from the archive

| Split | Images | YOLO label files | Annotated boxes |
| --- | ---: | ---: | ---: |
| Training | 55 | 53 | 55 |
| Validation | 28 | 28 | 29 |

Training images `55.png` and `56.png` have no matching text labels. Their intended status is unknown. The validation directory also contains 28 Pascal VOC XML files with 29 objects labeled `ship`. Each split has a separate class-name text file. The dataset YAML leaves the test split empty. The interim report describes a larger collection, and these counts refer specifically to this ZIP.

Four training images are byte-identical to validation images. Comparing decoded RGB pixels finds a fifth pair, training `8.webp` and validation `5.png`. These overlaps limit the use of the recorded validation scores as evidence of generalization to unseen images. The optional pixel comparison checks image dimensions and hashes the decoded RGB bytes.

Two other archives help trace this dataset. All 30 surviving validation label files in the older `yolov5-7.0(1 1.zip` match the same-numbered training label files here, byte for byte. All 55 inputs to the associated DCGAN experiment match these training images. None of its 115 saved generated images is a byte-identical detector input. The files establish a shared image collection, while the exact augmentation mix behind each historical detector run remains unknown.

## Experiment records

Each [CSV](records/) has 100 rows, covering epoch indices 0–99. The table uses the last row throughout. The checkpoint filenames shown were matched by SHA-256 to each run's archived `weights/best.pt`. A name records how a checkpoint was filed. It cannot establish every setting used to train it.

| Run | Matching checkpoint filename | Final mAP@0.50 | Final mAP@0.50:0.95 |
| --- | --- | ---: | ---: |
| exp12 | CIoU_best.pt | 0.73373 | 0.40575 |
| exp13 | EIoU_best.pt | 0.00000 | 0.00000 |
| exp14 | DIoU_best.pt | 0.91816 | 0.54991 |
| exp15 | GIoU_best.pt | 0.89072 | 0.53299 |
| exp21 | SimAM_GIoU_best.pt | 0.89961 | 0.52030 |
| exp22 | SimAMDIoU_best.pt | 0.91344 | 0.50330 |

The exp13 log contains `NaN` for training and validation box and objectness losses in all 100 rows. Its precision, recall, and both mAP columns remain zero. The saved exp21 options point to the SimAM YAML. The exp22 options specify `DIoU_last.pt` with an empty model-configuration field. Its filename alone cannot confirm that the active architecture included SimAM. Several other run directories contain options without a metrics CSV.

## Model and loss details

- The [architecture file](reference/yolov5s-simam.yaml) declares one class and inserts SimAM after the final C3 block on the largest-stride feature map. The detection head consumes layers 17, 20, and 24.
- The [SimAM class](reference/simam.py) calculates a spatial weighting within each channel and multiplies the input tensor by that weight. It was copied from the archive with the two imports needed to inspect it independently. On CPU PyTorch 2.7.1, a synthetic tensor of shape `2 × 4 × 8 × 8` produced a finite output of the same shape. This check exercises the layer alone.
- The archived parser lists SimAM in a general channel-handling branch before its dedicated branch. With this YAML, the constructor receives `(512, 512)` and the resulting layer has `e_lambda=512`, overriding the class default of `1e-4`. This matters when comparing the archived model with other SimAM implementations.
- The current `utils/loss.py` calls `bbox_iou(..., DIoU=True)`. The archived EIoU branch in `utils/metrics.py` raises the width and height differences to powers 241 and 242. The historical logs provide no per-run snapshot of this file. The cause of the exp13 numerical failure remains unverified.

## Run the detector source

The [detector folder](detector/) contains the three Python entry points and the model and loss code they use. Its setup and launch instructions cover local data and weights. The package metadata in the original archive declares YOLOv5 7.0.0 and Python 3.8 or later. Its requirements include `ultralytics>=8.2.34`. The historical environment lock and exact upstream commit are unavailable.

The original training default selected `DIoU_last.pt`, validation selected `SimAMDIoU_best.pt`, and detection selected `yolov5s.pt` with bundled example images. For custom data, use the explicit paths in the detector instructions. For the archived data layout, `data/data.yaml` points to `datasets/train/images` and `datasets/valid/images` beneath the detector root. The older, smaller ZIP lacks all three entry scripts.

**Architecture check.** In both the original archive source and the repository copy, the three entry points printed their help and the model forward pass ran on CPU. One archived validation photograph (1920 × 1440) was decoded and resized with the original letterbox function to a 640 × 640 input. The randomly initialized single-class YOLOv5s and YOLOv5s-SimAM models each returned a finite tensor of shape `1 × 25,200 × 6`, from feature maps of 80 × 80, 40 × 40, and 20 × 20. This check validates the model wiring and preprocessing. Detection accuracy requires trained weights and an independent evaluation set. The check used Python 3.12.14, PyTorch 2.7.1+cpu, torchvision 0.22.1+cpu, Ultralytics 8.2.34, and OpenCV 4.11 on Windows.

**Training check.** The repository copy completed one CPU epoch from random SimAM weights using two generated rectangle images for training and one for validation, at 96 × 96 with batch size 2 and zero data loader workers. The run wrote a finite loss row, saved best and last checkpoints, reloaded its own best checkpoint, and completed final validation. The process used an isolated temporary output directory and loaded only the checkpoints it had just generated. This exercise verifies the training workflow on synthetic data.

## Attribution

The full archive credits Ultralytics for the YOLOv5 framework. Its upstream citation names Glenn Jocher and its project metadata also lists Ayush Chaurasia and Jing Qiu. The [archived license](reference/LICENSE) accompanies the code and configuration excerpts. The [dataset YAML](reference/data.yaml) retains COCO128 template comments, while its active paths and class definition refer to the ship images. The source-image licenses are undocumented in this archive. [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5)
