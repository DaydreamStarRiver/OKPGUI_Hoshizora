#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
警告对话框模块

该模块提供了一个用于显示警告信息的对话框，由 PyQt6 UI 代码生成器生成。

注意：此文件由 pyuic6 从 WarningDialog.ui 文件生成，手动修改会在下次生成时丢失。
"""

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    """警告对话框 UI 类"""
    
    def setupUi(self, Dialog):
        """设置对话框 UI
        
        Args:
            Dialog (QDialog): 对话框实例
        """
        Dialog.setObjectName("Dialog")
        Dialog.resize(300, 106)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        
        # 创建垂直布局
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        # 创建标签用于显示警告信息
        self.label = QtWidgets.QLabel(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        
        # 创建按钮框，包含确定和取消按钮
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        # 翻译 UI
        self.retranslateUi(Dialog)
        # 连接按钮信号
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        # 连接信号槽
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        """翻译 UI 文本
        
        Args:
            Dialog (QDialog): 对话框实例
        """
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "TextLabel"))


if __name__ == "__main__":
    import sys
    # 创建应用程序实例
    app = QtWidgets.QApplication(sys.argv)
    # 创建对话框实例
    Dialog = QtWidgets.QDialog()
    # 创建 UI 实例并设置
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    # 显示对话框
    Dialog.show()
    # 启动应用程序事件循环
    sys.exit(app.exec())
