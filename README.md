# Robotics and computer vision projects

This collection covers camera-based charging-port alignment, scripted robot motion in MuJoCo, and a shipwreck imaging study. A separate database course project includes two examples of client-side API integration.

| Project | What to inspect | Where to start |
| --- | --- | --- |
| Charging-port alignment | OpenCV detects three socket holes, measures their offset from the camera center and formats a serial adjustment. Generated frames and an in-memory serial connection make the decision logic easy to reproduce. | [Run the offline example](charging-vision-public/README.md) |
| Factory handling simulation | A recorded sequence coordinates a six-joint arm, an articulated hand and a battery fixture. The included six-actuator fixture demonstrates part of the motion without external meshes. | [Replay the fixture in MuJoCo](simulation/README.md) |
| Shipwreck detection | The YOLOv5 source includes training, validation and inference for a single `ship` class. Six historical runs are available for inspection. Five validation images also appear in the training set after image decoding, which limits what can be inferred from the logged scores. | [Inspect the detector and training records](ship-detection/README.md) |
| Image generation experiments | A DCGAN training script and its generator and discriminator accompany image-generation experiments. The shipwreck subset uses the same 55 input images as the recovered YOLOv5 training split. | [Read the DCGAN experiment notes](dcgan-experiments/README.md) |
| Campus partner matching | Two Vue components show how a student can search by interest and check an application. Each calls a separate KES Plus API. | [Inspect the two request flows](campus-matching/README.md) |

The shipwreck detection and image generation folders cover two parts of the same research project. The charging system and the factory-handling simulation have separate hardware assumptions and entry points. Each folder documents the available source, dependencies and checks performed during preparation.
