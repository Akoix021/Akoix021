# Train and run the ship detector

This directory contains the detection code recovered from `yolov5-master.zip`. The three entry points share the model parser, image loader and bounding-box utilities. Start with [the SimAM model configuration](models/yolov5s-simam.yaml) and [the training loss](utils/loss.py) to inspect the experiment. The archived loss selects DIoU in its box regression calculation. The [standard YOLOv5s configuration](models/yolov5s.yaml) is also available. Training takes its class count from the dataset YAML.

## Install

Run these PowerShell commands **from this directory**. The example uses a dedicated Python 3.12 environment. The requirements select PyTorch 2.5.1, torchvision 0.20.1 and Ultralytics 8.2.34 for this local edition. The archived package specified minimum dependency versions and supplied no environment lock.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Train on your own images

The supplied [ship dataset definition](data/data.yaml) maps class zero to `ship`. Place your own labeled images in the layout below. Each label row uses `class_id x_center y_center width height` with normalized coordinates. To use a different location, copy the YAML and set `path` to your dataset's absolute path. Pass that YAML to every command.

```text
datasets/
  train/
    images/
    labels/
  valid/
    images/
    labels/
```

This starts the SimAM model from random weights, trains for one epoch on CPU and writes checkpoints under `runs/train/ship-local/weights/`. Use the standard model YAML to train the baseline. Choose a fresh run name when repeating the commands.

```powershell
.\.venv\Scripts\python train.py --data data/data.yaml --cfg models/yolov5s-simam.yaml --weights= --hyp data/hyps/hyp.scratch-low.yaml --epochs 1 --batch-size 2 --imgsz 640 --workers 0 --device cpu --name ship-local
```

`--weights=` supplies an empty path explicitly. Without that option, the historical training default looks for `DIoU_last.pt`. The images and archived weights are held separately from this source directory.

## Validate and predict

Use the checkpoint produced by your own training run. The detector saves annotated output to `runs/detect/`.

```powershell
.\.venv\Scripts\python val.py --data data/data.yaml --weights runs/train/ship-local/weights/best.pt --device cpu --workers 0
.\.venv\Scripts\python detect.py --data data/data.yaml --weights runs/train/ship-local/weights/best.pt --source datasets/valid/images --device cpu
```

## What was verified

Both model configurations produced finite output of shape `(1, 25200, 6)` from a 640-pixel input in the single-class configuration. The code in this directory also completed one CPU training epoch from random initialization using two synthetic training images and one synthetic validation image. The trainer wrote `best.pt` and `last.pt` and reloaded its own output for final validation.

That training check ran under PyTorch 2.7.1, whose default weights-only loader differs from the archive's whole-model format. The temporary training process set `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1` only for checkpoints generated within that isolated check. The installation above selects PyTorch 2.5.1, which reads the trainer's own whole-model files by default. In separate PyTorch 2.5.1 CPU processes, `val.py` evaluated the fresh checkpoint on one synthetic image and `detect.py` wrote an output image. The detector returned zero boxes at its default prediction threshold. These checks exercised the code paths. Ship-detection performance and the archived checkpoints were not evaluated in these runs.

## Source and modifications

The archive credits Ultralytics and supplies the [AGPL-3.0 license](LICENSE) and a [software citation](CITATION.cff). The project-specific model, parser, DIoU loss and metrics are included in their original locations. This edition keeps local logging, file-based data checks and the model-format table used during inference. Packaging edits remove automatic package installation on import, remote Git update checks, dataset-provided download commands and notebook setup. The dependency bounds above describe this edition. Modified source files carry a dated notice.
