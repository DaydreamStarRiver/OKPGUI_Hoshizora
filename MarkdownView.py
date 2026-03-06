#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 预览窗口模块

该模块提供了一个用于预览 Markdown 渲染效果的窗口，使用 QWebEngineView 来显示 HTML 内容。
"""

import sys

from PyQt6.QtCore import QUrl, QByteArray, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QToolBar, QMainWindow, QDialog, QWidget, QVBoxLayout
from PyQt6.QtNetwork import QNetworkCookie, QNetworkCookieJar
from PyQt6.QtGui import QAction
from urllib import parse

class MarkdownViewWindow(QWidget):
    """Markdown 预览窗口类"""
    
    def __init__(self, html, parentWindow, *args, **kwargs):
        """初始化 Markdown 预览窗口
        
        Args:
            html (str): 要显示的 HTML 内容
            parentWindow (QWidget): 父窗口
        """
        super(QWidget, self).__init__(*args, **kwargs)

        # 设置窗口大小
        self.resize(1200, 1080)
        # 保存父窗口引用
        self.parentWindow = parentWindow
        # 设置窗口标题
        self.setWindowTitle("Preview")

        # 创建 Web 引擎视图用于显示 HTML
        self.browser = QWebEngineView()
        # 设置 HTML 内容
        self.browser.setHtml(html)

        # 创建垂直布局
        vbox = QVBoxLayout(self)
        # 添加 Web 引擎视图到布局
        vbox.addWidget(self.browser)
        # 设置窗口布局
        self.setLayout(vbox)
