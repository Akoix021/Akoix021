# Ultralytics YOLOv5 🚀, AGPL-3.0 license
# Local review edition, 2026-11-19. Keep the file and TensorBoard callbacks used for local detection training.
"""Logging utils."""

import json
import os
import warnings
from pathlib import Path

import torch

from utils.general import LOGGER, colorstr, cv2
from utils.plots import plot_images, plot_labels, plot_results
from utils.torch_utils import de_parallel

LOGGERS = ("csv", "tb")
RANK = int(os.getenv("RANK", -1))

try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:

    def SummaryWriter(*args):
        """Fall back to SummaryWriter returning None if TensorBoard is not installed."""
        return None  # None = SummaryWriter(str)


def _json_default(value):
    """
    Format `value` for JSON serialization (e.g. unwrap tensors).

    Fall back to strings.
    """
    if isinstance(value, torch.Tensor):
        try:
            value = value.item()
        except ValueError:  # "only one element tensors can be converted to Python scalars"
            pass
    return value if isinstance(value, float) else str(value)


class Loggers:
    """Initializes and manages various logging utilities for tracking YOLOv5 training and validation metrics."""

    def __init__(self, save_dir=None, weights=None, opt=None, hyp=None, logger=None, include=LOGGERS):
        """Initializes loggers for YOLOv5 training and validation metrics, paths, and options."""
        self.save_dir = save_dir
        self.weights = weights
        self.opt = opt
        self.hyp = hyp
        self.plots = not opt.noplots  # plot results
        self.logger = logger  # for printing results to console
        self.include = include
        self.keys = [
            "train/box_loss",
            "train/obj_loss",
            "train/cls_loss",  # train loss
            "metrics/precision",
            "metrics/recall",
            "metrics/mAP_0.5",
            "metrics/mAP_0.5:0.95",  # metrics
            "val/box_loss",
            "val/obj_loss",
            "val/cls_loss",  # val loss
            "x/lr0",
            "x/lr1",
            "x/lr2",
        ]  # params
        self.best_keys = ["best/epoch", "best/precision", "best/recall", "best/mAP_0.5", "best/mAP_0.5:0.95"]
        for k in LOGGERS:
            setattr(self, k, None)  # init empty logger dictionary
        self.csv = True  # always log to csv
        self.ndjson_console = "ndjson_console" in self.include  # log ndjson to console
        self.ndjson_file = "ndjson_file" in self.include  # log ndjson to file

        # TensorBoard
        s = self.save_dir
        if "tb" in self.include and not self.opt.evolve:
            prefix = colorstr("TensorBoard: ")
            self.logger.info(f"{prefix}Start with 'tensorboard --logdir {s.parent}', view at http://localhost:6006/")
            self.tb = SummaryWriter(str(s))


    @property
    def remote_dataset(self):
        return None


    def on_pretrain_routine_end(self, labels, names):
        """Callback that runs at the end of pre-training routine, logging label plots if enabled."""
        if self.plots:
            plot_labels(labels, names, self.save_dir)

    def on_train_batch_end(self, model, ni, imgs, targets, paths, vals):
        """Logs training batch end events, plots images, and updates external loggers with batch-end data."""
        # Callback runs on train batch end
        # ni: number integrated batches (since train start)
        if self.plots:
            if ni < 3:
                f = self.save_dir / f"train_batch{ni}.jpg"  # filename
                plot_images(imgs, targets, paths, f)
                if ni == 0 and self.tb and not self.opt.sync_bn:
                    log_tensorboard_graph(self.tb, model, imgsz=(self.opt.imgsz, self.opt.imgsz))

    def on_fit_epoch_end(self, vals, epoch, best_fitness, fi):
        """Callback that logs metrics and saves them to CSV or NDJSON at the end of each fit (train+val) epoch."""
        x = dict(zip(self.keys, vals))
        if self.csv:
            file = self.save_dir / "results.csv"
            n = len(x) + 1  # number of cols
            s = "" if file.exists() else (("%20s," * n % tuple(["epoch"] + self.keys)).rstrip(",") + "\n")  # add header
            with open(file, "a") as f:
                f.write(s + ("%20.5g," * n % tuple([epoch] + vals)).rstrip(",") + "\n")
        if self.ndjson_console or self.ndjson_file:
            json_data = json.dumps(dict(epoch=epoch, **x), default=_json_default)
        if self.ndjson_console:
            print(json_data)
        if self.ndjson_file:
            file = self.save_dir / "results.ndjson"
            with open(file, "a") as f:
                print(json_data, file=f)

        if self.tb:
            for k, v in x.items():
                self.tb.add_scalar(k, v, epoch)

    def on_train_end(self, last, best, epoch, results):
        """Callback that runs at the end of training to save plots and log results."""
        if self.plots:
            plot_results(file=self.save_dir / "results.csv")  # save results.png
        files = ["results.png", "confusion_matrix.png", *(f"{x}_curve.png" for x in ("F1", "PR", "P", "R"))]
        files = [(self.save_dir / f) for f in files if (self.save_dir / f).exists()]  # filter
        self.logger.info(f"Results saved to {colorstr('bold', self.save_dir)}")

        if self.tb:
            for f in files:
                self.tb.add_image(f.stem, cv2.imread(str(f))[..., ::-1], epoch, dataformats="HWC")

def log_tensorboard_graph(tb, model, imgsz=(640, 640)):
    """Logs the model graph to TensorBoard with specified image size and model."""
    try:
        p = next(model.parameters())  # for device, type
        imgsz = (imgsz, imgsz) if isinstance(imgsz, int) else imgsz  # expand
        im = torch.zeros((1, 3, *imgsz)).to(p.device).type_as(p)  # input image (WARNING: must be zeros, not empty)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # suppress jit trace warning
            tb.add_graph(torch.jit.trace(de_parallel(model), im, strict=False), [])
    except Exception as e:
        LOGGER.warning(f"WARNING ⚠️ TensorBoard graph visualization failure {e}")
