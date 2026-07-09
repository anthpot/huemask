# Mask Annotation Tool v1.0 / 掩膜标注工具 v1.0

**Region-wise HSV-assisted labeling: draw a rough box, tune color thresholds with live preview, and get pixel-accurate masks — block by block.**
**分块 HSV 辅助标注：粗略框一个区域，拖滑块实时预览颜色命中，回车即得像素级掩膜——一块一块来。**

[English](#english) | [中文](#中文)

---

## English

A lightweight PyQt5 + OpenCV desktop tool for creating and correcting semantic-segmentation masks. Built for refining masks produced by models such as SAM2, and equally usable for labeling from scratch.

### ✨ Highlights

- **Region-wise HSV labeling (the core feature).** Global color thresholding breaks down when lighting varies across an image. Here you outline a rough region first, then tune the H/S/V range **with a live preview of exactly which pixels will change** — only pixels inside your region are affected. Move to the next block, use a *different* HSV range, repeat. You get pixel-accurate boundaries from color, while only ever drawing rough polygons.
- **Preview before commit.** In HSV mode nothing touches the mask until you press Enter; matched pixels light up in the target-class color so you see the exact result beforehand. Esc cancels.
- **Surgical relabeling with the source-class filter.** Restrict any edit to pixels that currently belong to one class — e.g. "inside this box, turn only *leaf* pixels into *spike*" — so fixing one class never damages its neighbors.
- **Three complementary modes.** HSV filter fill for the heavy lifting, polygon fill for clean regions, brush for touch-ups.
- **Non-destructive workflow.** Original masks are never modified; corrected masks are written to a separate folder and automatically take precedence on the next load. Undo up to 20 steps (Ctrl+Z).
- **Pixel-accurate viewing.** Full-resolution rendering with nearest-neighbor magnification — zoom in and see real pixel boundaries, not blur. Wheel zoom, Ctrl/middle-drag pan, high-DPI aware.
- **Frictionless data handling.** No popups at startup: data folders next to the tool are picked up automatically, otherwise use "Open data folder…" to point at any dataset — including a plain folder of images. Missing masks start blank, so labeling from scratch just works.
- **Bilingual UI (English default, 中文 switchable), configurable classes, Unicode/CJK paths.**

### Installation

```bash
pip install -r requirements.txt
python main.py
```

### Try it in 2 minutes with the example data

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

### Using your own data

Put data folders next to the tool (auto-detected at startup), or open any folder with the button:

| Folder | Content |
|---|---|
| `images/` (or `1_图像/`) | source images (jpg/png) |
| `masks/` (or `2_掩膜/`) | initial masks — optional; single-channel PNG, pixel value = class ID, same base filename as the image |
| `masks_corrected/` (or `3_修正掩膜/`) | corrected output (created automatically, loaded in preference next time) |

Picking the images folder itself, or any loose folder of images, also works — mask folders are located or created automatically.

### Shortcuts

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

### Class configuration

`class_config.json` is generated on first run and freely editable:

```json
{
  "0": { "name": "background", "color": [0, 0, 0] },
  "1": { "name": "spike",      "color": [220, 20, 60] },
  "...": {}
}
```

`color` is RGB (display only). Mask PNGs store class IDs (0–255), not colors.

### Tests

```bash
pip install pytest
python -m pytest tests
```

---

## 中文

一个轻量的 PyQt5 + OpenCV 桌面工具，用于制作和修正语义分割掩膜。适合对模型（如 SAM2）生成的掩膜做人工精修，也可以从零开始标注。

### ✨ 亮点

- **分块 HSV 标注（核心功能）。** 全图统一的颜色阈值在光照不均时必然失效。这个工具的做法是：先粗略框出一块区域，再拖 H/S/V 滑块——**哪些像素会被改，实时高亮给你看**，且只影响框内。这一块做完，换下一块，用*另一组*阈值。粗框由你画，像素级的精细边界交给颜色来算。
- **先预览、后落笔。** HSV 模式下按回车之前掩膜完全不动：命中像素以目标类别的颜色点亮，效果所见即所得；Esc 随时取消。
- **源类别限定，指哪打哪。** 任何编辑都可以限定"只改原来属于某一类的像素"——例如"这个框里，只把*叶*改成*穗*"——修一个类别绝不误伤旁边的。
- **三种模式互补。** HSV 过滤填充干重活，多边形填充处理规整区域，画笔做零星修补。
- **无损工作流。** 原始掩膜永不改动，修正结果写入独立文件夹，下次打开自动优先加载；支持 20 步撤销（Ctrl+Z）。
- **像素级查看。** 全分辨率渲染 + 放大时最近邻显示，看到的是真实像素边界而不是模糊插值；滚轮缩放、Ctrl/中键拖动平移，适配高 DPI 屏。
- **数据加载零阻碍。** 启动不弹窗：工具旁边有数据文件夹就自动读取，没有就点「打开数据文件夹…」指向任意数据集——哪怕只是一个装图片的普通文件夹。缺掩膜自动建空白，从零标注开箱即用。
- **双语界面（默认英文，可切中文）、类别可配置、兼容中文/Unicode 路径。**

### 安装

```bash
pip install -r requirements.txt
python main.py
```

### 用示例数据 2 分钟上手

仓库自带三张合成样例，掩膜故意留了瑕疵（详见 [examples/README.md](examples/README.md)）。

1. 运行 `python main.py`，点右上角**「打开数据文件夹…」**，选择 `examples` 文件夹。
2. 红色"穗"的下半段被误标成了叶。用**分块 HSV** 修复：
   - 模式选 **HSV过滤填充**（默认），目标类别选 `1: spike`，源类别选 `任意`。
   - 左键在穗周围点几个点，右键闭合框选。
   - 把 **H** 滑块拖向红色区间（约 150–179），拉高 **S** 下限，直到只有红色籽粒亮起目标色——这就是实时预览。
   - 按**回车**。搞定——像素级精度，一个像素都不用手涂。
3. 整个掩膜还整体偏移了几个像素。框住一片叶子，把 H 调到绿色区间，回车。每一块用自己的阈值——这正是"分块"的意义。
4. 体验源类别限定：目标选 `2: leaf`、源类别选 `1: spike`，随便框一块——框内只有穗的像素会变。
5. **Ctrl+S** 保存到 `examples/masks_corrected/`；勾选「显示原图」或拖透明度滑块随时对照检查。

### 使用自己的数据

把数据文件夹放在工具旁边（启动自动识别），或用按钮打开任意文件夹：

| 文件夹 | 内容 |
|---|---|
| `images/`（或 `1_图像/`） | 原图（jpg/png） |
| `masks/`（或 `2_掩膜/`） | 原始掩膜——可选；单通道 PNG，像素值=类别 ID，文件名与原图相同 |
| `masks_corrected/`（或 `3_修正掩膜/`） | 修正输出（自动创建，下次优先加载） |

直接选中图像文件夹本身、或任何散装图片文件夹也可以——掩膜目录会自动定位或创建。

### 快捷键

| 按键 | 功能 |
|---|---|
| 左键 | 多边形加点 / 画笔涂抹 |
| 右键 | 闭合多边形 |
| 回车 | 应用 HSV 过滤到框选区 |
| Esc | 取消当前框选 |
| Ctrl+Z | 撤销（最多 20 步） |
| Ctrl+S | 保存当前掩膜 |
| 滚轮 | 缩放 |
| Ctrl+左键 / 中键拖动 | 平移画布 |

### 类别配置

`class_config.json` 首次运行自动生成，可自由修改：

```json
{
  "0": { "name": "background", "color": [0, 0, 0] },
  "1": { "name": "spike",      "color": [220, 20, 60] },
  "...": {}
}
```

`color` 为 RGB（仅用于显示）。掩膜 PNG 中保存的是类别 ID（0–255），不是颜色。

### 测试

```bash
pip install pytest
python -m pytest tests
```

---

## License / 许可证

MIT
