#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKPGUI 应用程序入口文件

该文件是 OKPGUI 应用程序的主入口点，负责创建应用程序实例并显示主窗口。
"""

import sys

from PyQt6.QtWidgets import QApplication
from OKPLogic import OKPMainWIndow
import platform


if __name__ == '__main__':
    # 创建 QApplication 实例
    app = QApplication(sys.argv)
    
    # 非 Windows 系统使用 Fusion 样式
    if platform.system() != "Windows":
        app.setStyle('Fusion')

    # 创建主窗口实例
    window = OKPMainWIndow()
    # 显示主窗口
    window.show()
    # 启动应用程序事件循环
    sys.exit(app.exec())
