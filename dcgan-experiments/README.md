# DCGAN image generation experiments

These PyTorch scripts train a deep convolutional generative adversarial network. The generator turns a 100-dimensional noise vector into a 128 × 128 RGB image. The discriminator assigns one real-or-generated score to each image. The archive contains three sets of inputs and saved outputs, including one with underwater shipwreck photographs. The network produces images. It has no object labels, bounding-box predictions or detection metrics.

The underwater project's midterm report describes why the team tried this approach. After narrowing its scope to underwater image restoration and shipwreck detection, the team studied a face-generation example and tried generating more shipwreck imagery. The report describes poor sample quality after roughly 100 rounds. It separately records a pretrained DeblurGAN-v2 restoration trial. The corresponding restoration code and weights have yet to be identified. There is no documented improvement in detector performance attributable to the generated images.

## Evidence in the original archive

| Folder | Subject seen in sample inputs | Input files | Saved training grids | Individual output images |
| --- | --- | ---: | ---: | ---: |
| `project1` | Color-coded human-pose silhouettes | 108 | 95 | 100 |
| `project2` | Underwater scenes including shipwrecks | 55 | 110 | 5 |
| `project3` | Red apples | 14 | 1,000 | 5 |

The counts refer to files. Selected inputs and outputs were opened to identify the subject in each row. The training script points to `project3/data`. Two serialized networks sit outside all three folders in the archive. No run manifest identifies the training set for those weights. The photos, saved outputs and checkpoints remain in the original archive.

Two embedded figures in the shipwreck project's midterm report can be traced to `project2/out0_0.png` and `project2/out99_199.png`. After aligning the 616 × 616 plotted regions, more than 99% of RGB channel values matched exactly in each comparison. This ties the underwater generation outputs to the report, including the early noise grid and the later blue-green image grid.

All 55 `project2/data/pose` source images match the 55 training images in `yolov5-master.zip` by filename and SHA-256. Four files also match validation images byte for byte. A fifth image, `train/8.webp`, has the same decoded RGB pixels as `valid/5.png`. None of the 115 saved `project2` output PNGs is byte-identical to an image in either detector split. The two experiments share source photographs. Use of transformed or re-encoded GAN outputs in another training run remains unknown.

## Source and entry points

| File | Role |
| --- | --- |
| [netG.py](netG.py) | Builds the generator from transposed convolutions, batch normalization, ReLU and a final tanh. |
| [netD.py](netD.py) | Builds the discriminator from convolutions, leaky ReLU, batch normalization and a final sigmoid. |
| [DCGAN学习.py](DCGAN学习.py) | Loads images with `torchvision.datasets.ImageFolder`, alternates discriminator and generator updates using binary cross-entropy and Adam, saves sample grids and serializes both networks. |
| [生成图片.py](生成图片.py) | Historical sampling entry point. It expects the local whole-model file `netg1000.pt`, uses a hard-coded output prefix and requests five samples. |

All four files preserve the original source bytes and the header credit `lhy`.

## Run the model shape check

From this directory, these commands create a local Python environment and exercise both networks on CPU with random weights. The PowerShell example uses Python 3.12. The check requires only PyTorch.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install torch==2.7.1
.\.venv\Scripts\python -c "import torch; from netG import Generator; from netD import Discriminator; x=Generator().eval()(torch.randn(2,100,1,1)); print(tuple(x.shape), tuple(Discriminator().eval()(x).shape))"
```

Expected output is `(2, 3, 128, 128) (2, 1, 1, 1)`.

## Run a short training check

1. Work on a local copy of the four Python files. Install the training dependencies in the same environment.

   ```powershell
   .\.venv\Scripts\python -m pip install torchvision==0.22.1 numpy==2.3.5 matplotlib==3.10.3
   ```

2. Create `sample-data/shapes/` and place two RGB images inside it. The subfolder is required by `ImageFolder`. In the local copy of `DCGAN学习.py`, set `dataroot = "sample-data"`, `num_epoch = 1`, and the `root` inside the training loop to `"out"`. That variable is a filename prefix. The first grid will be written as `out0_0.png` in the working directory.
3. Run the script from the directory containing the four files. This example selects a noninteractive plot backend.

   ```powershell
   $env:MPLBACKEND = "Agg"
   .\.venv\Scripts\python ".\DCGAN学习.py"
   ```

A CPU check on two synthetic shape images completed one epoch and wrote the sample grid, `netg1.pt` and `netd1.pt`. The path and epoch settings were changed only in the test copy. The original setting is 1,000 epochs, batch size 32 and learning rate 0.0003. The test used Python 3.12, PyTorch 2.7.1, torchvision 0.22.1, NumPy 2.3.5 and matplotlib 3.10.3. These versions describe the check. The historical dependency versions and image quality on the three source datasets remain unverified.

The sampler uses legacy whole-model loading. Its archived checkpoint was left unopened, and the original sampling entry point was not validated.
