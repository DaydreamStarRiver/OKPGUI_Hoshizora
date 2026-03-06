#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程输出控制台模块

该模块提供了一个用于显示外部进程输出的控制台窗口，主要用于显示 OKP.Core.exe 的运行结果。
"""

import sys

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QProcess
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout, QPushButton
import locale


class ProcessOutputReader(QProcess):
    """进程输出读取器类"""
    
    # 定义信号，用于发送进程输出的文本
    produce_output = pyqtSignal(str)

    def __init__(self, parent=None):
        """初始化进程输出读取器
        
        Args:
            parent (QObject): 父对象
        """
        super().__init__(parent=parent)

        # 将 stderr 通道合并到 stdout 通道
        self.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        # 连接 readyReadStandardOutput 信号到槽函数
        self.readyReadStandardOutput.connect(self._ready_read_standard_output)

    @pyqtSlot()
    def _ready_read_standard_output(self):
        """读取标准输出并发送信号"""
        # 读取所有标准输出
        raw_bytes = self.readAllStandardOutput()
        # 解码为文本
        text = raw_bytes.data().decode(locale.getencoding())
        # 发送输出文本信号
        self.produce_output.emit(text)


class MyConsoleWidget(QPlainTextEdit):
    """控制台文本显示组件类"""

    def __init__(self, parent=None):
        """初始化控制台文本显示组件
        
        Args:
            parent (QWidget): 父窗口
        """
        super().__init__(parent=parent)

        # 设置为只读模式
        self.setReadOnly(True)
        # 限制最大行数为 10000
        self.setMaximumBlockCount(10000)
        
        # 获取文本光标
        self._cursor_output = self.textCursor()

    @pyqtSlot(str)
    def append_output(self, text):
        """追加输出文本
        
        Args:
            text (str): 要追加的文本
        """
        # 插入文本
        self._cursor_output.insertText(text)
        # 滚动到最后一行
        self.scroll_to_last_line()

    def scroll_to_last_line(self):
        """滚动到最后一行"""
        cursor = self.textCursor()
        # 移动到文本末尾
        cursor.movePosition(QTextCursor.MoveOperation.End)
        # 如果在块开始位置，向上移动一行，否则移动到行首
        cursor.movePosition(QTextCursor.MoveOperation.Up if cursor.atBlockStart() else
                            QTextCursor.MoveOperation.StartOfLine)
        # 设置光标位置
        self.setTextCursor(cursor)

class MyConsole(QWidget):
    """控制台窗口类"""
    
    def __init__(self, parentWindow, *args, **kwargs):
        """初始化控制台窗口
        
        Args:
            parentWindow (QWidget): 父窗口
        """
        super(QWidget, self).__init__(*args, **kwargs)
        # 设置窗口大小
        self.resize(800, 600)
        # 创建垂直布局
        self.vbox = QVBoxLayout(self)

        # 创建发布按钮
        self.publishButton = QPushButton(self)
        self.publishButton.setText("确定")
        font = QFont()
        font.setPointSize(20)
        self.publishButton.setFont(font)

        # 连接按钮点击信号
        self.publishButton.clicked.connect(self.onPublishButton)
        # 创建进程输出读取器
        self.reader = ProcessOutputReader()
        # 创建控制台文本显示组件
        self.consoleWidget = MyConsoleWidget()

        # 连接进程输出信号到控制台组件
        self.reader.produce_output.connect(self.consoleWidget.append_output)

        # 添加组件到布局
        self.vbox.addWidget(self.consoleWidget)
        self.vbox.addWidget(self.publishButton)

        # 设置窗口标题
        self.setWindowTitle("OKP 运行中…")

    def onPublishButton(self):
        """发布按钮点击事件处理"""
        # 追加换行
        self.consoleWidget.append_output("\n")
        # 向进程写入换行符
        self.reader.write(b"\n")

    def start(self, *args, **kargs):
        """启动进程
        
        Args:
            *args: 传递给 QProcess.start() 的参数
            **kargs: 传递给 QProcess.start() 的关键字参数
        """
        self.reader.start(*args, **kargs)

    def onFinished(self, func):
        """设置进程完成回调函数
        
        Args:
            func (callable): 进程完成时调用的函数
        """
        self.reader.finished.connect(func)

    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event (QCloseEvent): 关闭事件
        """
        # 终止进程
        self.reader.terminate()


if __name__ == "__main__":
    # 创建应用程序实例
    app = QApplication(sys.argv)
    # 创建控制台并连接进程输出读取器
    console = MyConsole(None)
    # 启动测试进程
    console.start('python', ['test.py'])
    
    # 显示控制台
    console.show()
    # 启动应用程序事件循环
    app.exec()