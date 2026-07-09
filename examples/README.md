# Example data / 示例数据

Three synthetic images with deliberately imperfect masks, for trying out the tool:

- the whole mask is shifted by a few pixels (practice fixing borders with the brush or HSV filter);
- the bottom part of each red "spike" is mislabeled as "leaf" (practice the source-class filter: set Target class = spike, Source class = leaf, then select the area).

三张合成图片，掩膜带有故意留下的瑕疵，用于快速体验工具：

- 整个掩膜偏移了几个像素（可用画笔或 HSV 过滤练习修边）；
- 每个红色"穗"的下半部分被误标成"叶"（可练习源类别限定：目标类别选 spike、源类别选 leaf，再框选该区域）。

## How to use / 使用方法

Option 1: start the tool from the repo root and pick this `examples` folder in the dialog that appears.
方式一：在仓库根目录启动工具，在弹出的对话框中选择本 `examples` 文件夹。

```bash
python main.py
```

Option 2: run the tool with `examples` as the working directory.
方式二：以 `examples` 为工作目录启动。

```bash
cd examples
python ../main.py
```

Corrected masks are written to `examples/masks_corrected/` (not tracked by git).
修正后的掩膜会保存到 `examples/masks_corrected/`（不入库）。
