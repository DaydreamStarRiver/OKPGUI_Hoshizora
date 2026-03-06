#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页辅助模块

该模块提供了网页浏览和 Cookie 获取功能，用于登录 BT 资源站并获取登录状态。
"""

import sys

from PyQt6.QtCore import QUrl, QByteArray, QSize, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QToolBar, QMainWindow, QDialog, QWidget, QVBoxLayout
from PyQt6.QtNetwork import QNetworkCookie, QNetworkProxy
from PyQt6.QtGui import QAction
from urllib import parse
import traceback
import datetime


def bytestostr(data):
    """将字节数据转换为字符串
    
    Args:
        data: 要转换的数据
        
    Returns:
        str: 转换后的字符串
    """
    if isinstance(data, str):
        return data
    if isinstance(data, QByteArray):
        data = data.data()
    if isinstance(data, bytes):
        data = data.decode(errors='ignore')
    else:
        data = str(data)
    return data

def cookiesToStr(cookie: QNetworkCookie):
    """将 QNetworkCookie 对象转换为字符串
    
    Args:
        cookie (QNetworkCookie): Cookie 对象
        
    Returns:
        str: 转换后的 Cookie 字符串
    """
    domain = cookie.domain()
    path = cookie.path()
    name = bytestostr(cookie.name().data())
    value = bytestostr(cookie.value().data())

    flags = []
    flags.append(f"{name}={value}")
    flags.append(f"domain={domain}")
    flags.append(f"path={path}")

    if cookie.isSecure(): flags.append("Secure")
    if cookie.isHttpOnly(): flags.append("HttpOnly")
    match cookie.sameSitePolicy():
        case QNetworkCookie.SameSite.Default:
            pass
        case QNetworkCookie.SameSite.Lax:
            flags.append("SameSite=Lax")
        case QNetworkCookie.SameSite.Strict:
            flags.append("SameSite=Strict")
        case QNetworkCookie.SameSite.None_:
            flags.append("SameSite=None")

    if not cookie.isSessionCookie():
        time = cookie.expirationDate().toString(Qt.DateFormat.ISODate)
        time = datetime.datetime.fromisoformat(time).strftime("%a, %d %b %Y %H:%M:%S GMT") 
        flags.append(f"expires={time}")

    flags = "; ".join(flags)
    
    return f"https://{domain}\t{flags}"

def filterCookies(cookie: QNetworkCookie) -> bool:
    """过滤需要的 Cookie
    
    Args:
        cookie (QNetworkCookie): Cookie 对象
        
    Returns:
        bool: 是否保留该 Cookie
    """
    if cookie.domain() == "share.dmhy.org":
        if bytestostr(cookie.name().data()) in {"pass", "rsspass", "tid", "uname", "uid"}:
            return True
    if cookie.domain() == "nyaa.si":
        if bytestostr(cookie.name().data()) == "session":
            return True
    if cookie.domain() == "acg.rip":
        if bytestostr(cookie.name().data()) == "_kanako_session":
            return True
    if cookie.domain() == "bangumi.moe":
        if bytestostr(cookie.name().data()) in {"locale", "koa:sess", "koa:sess.sig"}:
            return True
    return False


class WebEngineView(QWidget):
    """网页引擎视图类"""

    def __init__(self, url, parentWindow, *args, **kwargs):
        """初始化网页引擎视图
        
        Args:
            url (QUrl): 要加载的 URL
            parentWindow (QWidget): 父窗口
        """
        super(QWidget, self).__init__(*args, **kwargs)
        # 连接 Cookie 添加信号
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        # 设置窗口大小
        self.resize(1920, 600)
        # 保存父窗口引用
        self.parentWindow = parentWindow
        # 创建 Web 引擎视图
        self.browser = QWebEngineView()
        # 连接加载完成信号
        self.browser.loadFinished.connect(self.onLoadFinished)
        
        # 创建垂直布局
        vbox = QVBoxLayout(self)

        # 创建工具栏
        toolbar = QToolBar('toolbar')
        self.saveButton = QAction("保存 cookies", parent=self)
        backButton = QAction("后退", parent=self)
        refreshButton = QAction("刷新", parent=self)

        # 连接按钮信号
        backButton.triggered.connect(self.browser.back)
        refreshButton.triggered.connect(self.browser.reload)
        self.saveButton.triggered.connect(self.saveCookies)

        # 添加按钮到工具栏
        toolbar.addAction(backButton)
        toolbar.addAction(refreshButton)
        toolbar.addAction(self.saveButton)

        # 存储获取到的 Cookie
        self.cookies = []
        # 添加组件到布局
        vbox.addWidget(toolbar)
        vbox.addWidget(self.browser)
        # 设置窗口布局
        self.setLayout(vbox)

        # 设置代理
        if hasattr(parentWindow, 'menuProxyType') and parentWindow.menuProxyType.currentText() == "HTTP":
            parsed = parse.urlparse(self.parentWindow.profile['proxy'])
            self.proxy = QNetworkProxy(QNetworkProxy.ProxyType.HttpProxy, hostName=parsed.hostname, port=parsed.port)
            QNetworkProxy.setApplicationProxy(self.proxy)

        # 加载 URL
        self.browser.load(url)

    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event (QCloseEvent): 关闭事件
        """
        # 添加获取到的 Cookie 到父窗口
        self.parentWindow.addCookies("\n".join(self.cookies))
        # 设置用户代理
        self.parentWindow.setUserAgent(self.browser.page().profile().httpUserAgent())
        # 保存配置
        self.parentWindow.saveProfile()
        # 调用父类关闭事件
        super(WebEngineView, self).closeEvent(event)

    def onLoadFinished(self):
        """页面加载完成事件处理"""
        pass

    def onCookieAdd(self, cookie:QNetworkCookie):
        """Cookie 添加事件处理
        
        Args:
            cookie (QNetworkCookie): 新添加的 Cookie
        """
        if filterCookies(cookie):
            self.cookies.append(cookiesToStr(cookie))
        
    def saveCookies(self):
        """保存 Cookie 并关闭窗口"""
        self.close()


    
