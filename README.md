# HueMask v1.0 — Region-wise HSV Mask Annotation Tool

**[中文文档 → README_CN.md](README_CN.md)**

**Region-wise HSV-assisted labeling: draw a rough box, tune color thresholds with live preview, and get pixel-accurate masks — block by block.**

**HueMask** is a lightweight PyQt5 + OpenCV desktop tool for creating and correcting semantic-segmentation masks. Built for refining masks produced by models such as SAM2, and equally usable for labeling from scratch.

## ✨ Highlights

- **Region-wise HSV labeling (the core feature).** Global color thresholding breaks down when lighting varies across an image. Here you outline a rough region first, then tune the H/S/V range **with a live preview of exactly which pixels will change** — only pixels inside your region are affected. Move to the next block, use a *different* HSV range, repeat. You get pixel-accurate boundaries from color, while only ever drawing rough polygons.
- **Preview before commit.** In HSV mode nothing touches the mask until you press Enter; matched pixels light up in the target-class color so you see the exact result beforehand. Esc cancels.
- **Surgical relabeling with the source-class filter.** Restrict any edit to pixels that currently belong to one class — e.g. "inside this box, turn only *leaf* pixels into *spike*" — so fixing one class never damages its neighbors.
- **Three complementary modes.** HSV filter fill for the heavy lifting, polygon fill for clean regions, brush for touch-ups.
- **Non-destructive workflow.** Original masks are never modified; corrected masks are written to a separate folder and automatically take precedence on the next load. Undo up to 20 steps (Ctrl+Z).
- **Pixel-accurate viewing.** Full-resolution rendering with nearest-neighbor magnification — zoom in and see real pixel boundaries, not blur. Wheel zoom, Ctrl/middle-drag pan, high-DPI aware.
- **Frictionless data handling.** No popups at startup: data folders next to the tool are picked up automatically, otherwise use "Open data folder…" to point at any dataset — including a plain folder of images. Missing masks start blank, so labeling from scratch just works.
- **Bilingual UI (English default, 中文 switchable), configurable classes, Unicode/CJK paths.**

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Try it in 2 minutes with the example data

The repo ships three synthetic samples with deliberately flawed masks (see [examples/README.md](examples/README.md)).

1. Run `python main.py`, click **"Open data folder…"** (top right) and select the `examples` folder.
2. The red "spike" has its bottom part mislabeled as leaf. Fix it with **region-wise HSV**:
   - Mode: **HSV filter fill** (default). Target class: `1: spike`. Source class: `Any`.
   - Left-click a few points around the spike, right-click to close the region.
   - Drag the **H** sliders toward red (e.g. ≈ 150–179) and raise the **S** minimum until only the red grains glow in the spike color — that's the live preview.
   - Press **Enter**. Done — pixel-accurate, no pixel painting.
3. The whole mask is also shifted a few pixels. Pick a leaf, box it, tune H toward green, Enter. Each region gets its own thresholds — that's the point.
4. To see the source-class filter: set Target = `2: leaf`, Source = `1: spike`, and box an area — only spike pixels inside it change.
5. **Ctrl+S** saves to `examples/masks_corrected/`; toggle "Show raw image" or drag the opacity slider to inspect.

## Using your own data

Put data folders next to the tool (auto-detected at startup), or open any folder with the button:

| Folder | Content |
|---|---|
| `images/` (or `1_图像/`) | source images (jpg/png) |
| `masks/` (or `2_掩膜/`) | initial masks — optional; single-channel PNG, pixel value = class ID, same base filename as the image |
| `masks_corrected/` (or `3_修正掩膜/`) | corrected output (created automatically, loaded in preference next time) |

Picking the images folder itself, or any loose folder of images, also works — mask folders are located or created automatically.

## Shortcuts

| Key | Action |
|---|---|
| Left click | add polygon vertex / paint with brush |
| Right click | close polygon |
| Enter | apply HSV filter to the selected region |
| Esc | cancel current selection |
| Ctrl+Z | undo (up to 20 steps) |
| Ctrl+S | save current mask |
| Mouse wheel | zoom |
| Ctrl+left drag / middle drag | pan |

## Class configuration

`class_config.json` is generated on first run and freely editable:

```json
{
  "0": { "name": "background", "color": [0, 0, 0] },
  "1": { "name": "spike",      "color": [220, 20, 60] },
  "...": {}
}
```

`color` is RGB (display only). Mask PNGs store class IDs (0–255), not colors.

## Tests

```bash
pip install pytest
python -m pytest tests
```

## Citation

If HueMask is useful in your research, please cite it (GitHub's "Cite this repository" button uses [CITATION.cff](CITATION.cff)):

```bibtex
@software{huemask2026,
  author  = {anthpot},
  title   = {HueMask: Region-wise HSV Mask Annotation Tool},
  year    = {2026},
  version = {1.0},
  url     = {https://github.com/anthpot/huemask}
}
```

## License

Licensed under [CC BY-NC-SA 4.0](LICENSE) (Attribution-NonCommercial-ShareAlike):

- **Attribution** — keep the copyright notice and credit the source.
- **NonCommercial** — commercial use is **not** permitted without a separate license from the author.
- **ShareAlike** — modified or derivative versions **must** be open-sourced under the same license.
