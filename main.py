"""HueMask v1.0 entry point — Region-wise HSV Mask Annotation Tool
HueMask v1.0 入口 — 分块HSV掩膜标注工具"""
import sys
from PyQt5 import QtCore, QtWidgets

# 高 DPI 支持（4K 屏下控件/字体不再过小）——必须在 QApplication 创建前设置
# High-DPI support (widgets/fonts stay readable on 4K screens) — must be set before QApplication
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

from mask_tool.app import MaskEditor

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # 适当放大全局字体，进一步改善小字问题
    # Slightly enlarge the global font to improve readability
    f = app.font()
    f.setPointSize(max(f.pointSize(), 11))
    app.setFont(f)

    win = MaskEditor()
    if win.valid_startup:
        win.show()
        sys.exit(app.exec_())
    else:
        sys.exit(1)
