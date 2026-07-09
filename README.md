# Mask Annotation Tool v1.0 / 掩膜标注工具 v1.0

[English](#english) | [中文](#中文)

---

## English

A PyQt5 + OpenCV desktop tool for annotating and correcting semantic-segmentation masks. Designed for manually refining masks produced by models such as SAM2, and equally usable for labeling from scratch.

The UI is bilingual: **English by default**, switchable to 中文 from the dropdown in the top-right control panel (the choice is saved to `settings.json`).

### Features

- **Three editing modes**
  - **Polygon fill**: left-click to add vertices, right-click to close; pixels inside are set to the target class
  - **Brush**: paint with the left button, adjustable radius
  - **HSV filter fill** (default): draw a region, then drag the H/S/V sliders with a **live preview** of matching pixels; press Enter to apply — great for separating targets by color (e.g. spikes vs. leaves)
- **Source-class restriction**: optionally change only pixels that currently belong to one class (e.g. relabel only "leaf" pixels back to "spike"); choose "Any" to change everything inside the region
- **Undo**: up to 20 steps (Ctrl+Z)
- **Full-resolution rendering**: wheel zoom, Ctrl+left / middle-button pan; zoomed-in view shows true pixel boundaries for precise edge work
- **Unicode/CJK path support** and high-DPI display support
- **Configurable classes**: `class_config.json` is generated on first run; edit class names and colors freely
- **Data folder picker**: if no data folder is found next to the tool, a dialog asks for one at startup; the "Open data folder…" button switches folders at any time

### Installation

```bash
pip install -r requirements.txt
```

### Usage

1. Prepare data folders in the project root:

   | Folder | Content |
   |---|---|
   | `images/` (or `1_图像/`) | source images (jpg/png) |
   | `masks/` (or `2_掩膜/`) | initial masks (optional; single-channel PNG, pixel value = class ID, same base filename as the image) |
   | `masks_corrected/` (or `3_修正掩膜/`) | output folder for corrected masks (created automatically) |

   Legacy Chinese folder names are used if present, otherwise the English names. If neither is found, a folder-picker dialog opens at startup — you can also pick the images folder itself, or any folder that directly contains images. When no mask is found a blank one is created, so the tool also works for labeling from scratch.

2. Run:

   ```bash
   python main.py
   ```

   To try the bundled sample data, pick the `examples/` folder in the dialog (see [examples/README.md](examples/README.md)).

3. Pick an image in the file list on the right → choose "(1) Target class" and "(2) Source class" → draw/paint on the image → Ctrl+S to save. Saved corrected masks are loaded in preference to the originals next time. Use "Open data folder…" above the file list to switch datasets.

### Shortcuts

| Key | Action |
|---|---|
| Left click | add polygon vertex / paint with brush |
| Right click | close polygon |
| Enter | apply HSV filter to the selected region |
| Esc | cancel current selection |
| Ctrl+Z | undo |
| Ctrl+S | save current mask |
| Mouse wheel | zoom |
| Ctrl+left drag / middle drag | pan |

### Class configuration

`class_config.json` (auto-generated on first run, editable):

```json
{
  "0": { "name": "background", "color": [0, 0, 0] },
  "1": { "name": "spike",      "color": [220, 20, 60] },
  "...": {}
}
```

`color` is RGB. Mask PNGs store class IDs (0–255), not colors.

### Running tests

```bash
pip install pytest
python -m pytest tests
```

---

## 中文

一个基于 PyQt5 + OpenCV 的语义分割掩膜标注/修正桌面工具。适合对模型（如 SAM2）生成的分割掩膜做人工精修，也可以从零开始标注。

界面为双语：**默认英语**，可在右侧控制面板顶部的下拉框切换为中文（选择保存在 `settings.json`，下次启动生效）。

### 功能特性

- **三种编辑模式**
  - **多边形填充**：左键加点、右键闭合，多边形内像素改为目标类别
  - **画笔涂抹**：按住左键涂抹，画笔大小可调
  - **HSV 过滤填充**（默认）：先框选区域，再拖动 H/S/V 滑块**实时预览**命中像素，回车应用——适合按颜色快速分离目标（如穗、叶）
- **源类别限定**：可以只修改「原来是某一类」的像素（例如只把误标成"叶"的像素改回"穗"），选「任意」则区域内全部修改
- **撤销**：最多 20 步（Ctrl+Z）
- **全分辨率渲染**：滚轮缩放、Ctrl+左键/中键拖动平移，放大时按真实像素显示，方便精修边缘
- **中文/Unicode 路径兼容**、高 DPI 屏幕适配
- **类别可配置**：首次运行自动生成 `class_config.json`，可自行修改类别名与颜色
- **数据文件夹选择**：启动时若当前目录没有数据文件夹会弹出选择对话框；「打开数据文件夹…」按钮可随时切换数据集

### 安装

```bash
pip install -r requirements.txt
```

### 使用

1. 在项目根目录准备数据文件夹：

   | 文件夹 | 内容 |
   |---|---|
   | `images/`（或 `1_图像/`） | 原图（jpg/png） |
   | `masks/`（或 `2_掩膜/`） | 原始掩膜（可选，单通道 PNG，像素值=类别 ID，文件名与原图相同） |
   | `masks_corrected/`（或 `3_修正掩膜/`） | 修正后的掩膜输出目录（自动创建） |

   若存在中文旧目录（`1_图像` 等）则优先使用，否则使用英文目录名。两者都没有时启动会弹出文件夹选择对话框——也可以直接选图像文件夹本身或任何存放图片的文件夹。找不到掩膜时会新建空白掩膜，因此也可用于从零标注。

2. 启动：

   ```bash
   python main.py
   ```

   想体验自带示例数据，在弹出的对话框中选择 `examples/` 文件夹即可（见 [examples/README.md](examples/README.md)）。

3. 在右侧文件列表选图 → 选好「① 目标类别」和「② 源类别」→ 在图上框选/涂抹 → Ctrl+S 保存。已保存的修正掩膜下次会优先加载。文件列表上方的「打开数据文件夹…」按钮可随时切换数据集。

### 快捷键

| 按键 | 功能 |
|---|---|
| 左键 | 多边形加点 / 画笔涂抹 |
| 右键 | 闭合多边形 |
| 回车 | 应用 HSV 过滤到框选区 |
| Esc | 取消当前框选 |
| Ctrl+Z | 撤销 |
| Ctrl+S | 保存当前掩膜 |
| 滚轮 | 缩放 |
| Ctrl+左键 / 中键拖动 | 平移画布 |

### 类别配置

`class_config.json`（首次运行自动生成，可修改）：

```json
{
  "0": { "name": "background", "color": [0, 0, 0] },
  "1": { "name": "spike",      "color": [220, 20, 60] },
  "...": {}
}
```

`color` 为 RGB。掩膜 PNG 中保存的是类别 ID（0–255），不是颜色。

### 运行测试

```bash
pip install pytest
python -m pytest tests
```

---

## License / 许可证

MIT
