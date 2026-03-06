#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKPGUI 主逻辑模块

该模块是 OKPGUI 的核心逻辑文件，包含了主窗口类 OKPMainWIndow 的实现，
负责处理用户界面交互、模板管理、身份管理、发布功能等核心业务逻辑。
"""

from PyQt6.QtCore import (
    QUrl, 
    QProcess, 
    Qt, 
    QFileInfo,
)
from PyQt6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QFileDialog, 
    QDialog,
    QTreeWidgetItem, 
    QFileIconProvider, 
    QStyle,
)
import sys
from OKPUI import Ui_MainWindow
from WarningDialog import Ui_Dialog
import yaml
from pathlib import Path
from WebHelper import WebEngineView
import re
import markdown
from MarkdownView import MarkdownViewWindow
import toml
from html2phpbbcode.parser import HTML2PHPBBCode
from collections import defaultdict
import torrent_parser as tp
from ProcessWindow import MyConsole
import platform

# 版本号
VERSION = "v0.1.7 Beta"

# 资源分类映射表，定义了不同类型资源支持的子分类
CATEGORY = {
    'Anime': ['Default', 'MV', 'TV', 'Movie', 'Collection', 'Raw', 'English'],
    'Music': ['Default', 'Lossless', 'Lossy', 'ACG', 'Doujin', 'Pop'],
    'Comic': ['Default', 'HongKong', 'Taiwan', 'Japanese', 'English'],
    'Novel': ['Default', 'HongKong', 'Taiwan', 'Japanese', 'English'],
    'Action': ['Default', 'Idol', 'TV', 'Movie', 'Tokusatsu', 'Show', 'Raw', 'English'],
    'Picture': ['Default', 'Graphics', 'Photo'],
    'Software': ['Default', 'App', 'Game']
}

# 模板配置文件路径
TEMPLATE_CONFIG = Path("okpgui_config.yml")
# 身份配置文件路径
PROFILE_CONFIG = Path("okpgui_profile.yml")

class OKPerror(Exception):
    """OKP 错误异常类"""
    pass

class OKPMainWIndow(QMainWindow, Ui_MainWindow):
    """OKP 主窗口类
    
    该类是应用程序的主窗口，集成了 UI 界面和业务逻辑，
    负责处理种子文件选择、模板管理、身份管理、发布操作等功能。
    """
    
    def __init__(self, *args, **kwargs):
        """初始化主窗口
        
        Args:
            *args: 传递给父类的参数
            **kwargs: 传递给父类的关键字参数
        """
        QMainWindow.__init__(self, *args, **kwargs)
        # 设置 UI
        self.setupUi(self)
        # 设置额外的 UI 初始化
        self.setupUi2()
        # 检查 OKP.Core.exe 是否存在
        if not Path("OKP.Core.exe").exists():
            self.warning("找不到 OKP.Core.exe，请将本程序复制到 OKP.Core.exe 同目录下。")
            sys.exit(1)
    
    def setupUi2(self):
        """设置额外的 UI 初始化
        
        该方法负责初始化 UI 组件的信号连接、加载数据等操作。
        """
        # 设置窗口标题
        self.setWindowTitle("OKPGUI by AmusementClub " + VERSION)

        self.textAboutProgram.setText(f"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li {{ white-space: pre-wrap; }}
</style></head><body style=" font-family:'Microsoft YaHei UI'; font-size:12pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">此软件为 <a href="https://github.com/AmusementClub/OKP"><span style=" text-decoration: underline; color:#0000ff;">OKP</span></a> 的 GUI，由<a href="https://github.com/AmusementClub"><span style=" text-decoration: underline; color:#0000ff;">娱乐部</span></a>制作，用于快速在多个 BT 资源站发布种子。</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">使用方法参见 GitHub 上的 <a href="https://github.com/AmusementClub/OKPGUI"><span style=" text-decoration: underline; color:#0000ff;">README</span></a>。</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Version: {VERSION}</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">作者：<a href="https://github.com/tastysugar"><span style=" text-decoration: underline; color:#0000ff;">tastySugar</span></a></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>
                                      """)

        # 连接浏览按钮点击信号到选择种子文件方法
        self.buttonBrowse.clicked.connect(self.selectTorrentFile)
        
        # 设置主页标签页接受拖放
        self.HomeTab.setAcceptDrops(True)
        # 连接标签页切换信号
        self.tab.currentChanged.connect(self.changeTabHandler)
        # 设置拖放事件处理
        self.HomeTab.dragEnterEvent = self.onDragEnterEvent
        self.HomeTab.dropEvent = self.onDropEvent
        self.HomeTab.dragLeaveEvent = self.onDragLeaveEvent
        # 连接种子文件路径文本变化信号
        self.textTorrentPath.textChanged.connect(self.loadTorrent)


        # 重新加载身份配置
        self.reloadProfile()

        # 重新加载模板配置
        self.reloadTemplate()
        # 更新模板显示
        self.updateTemplate()
        # 处理身份选择变化
        self.selectCookiesChangeHandler(self.menuSelectCookies.currentText())

        # 加载代理设置
        self.loadProxy()

        # 连接保存/删除模板按钮点击信号
        self.buttonSaveTemplate.clicked.connect(self.saveTemplate)
        self.buttonDeleteTemplate.clicked.connect(self.deleteTemplate)


        # 连接预览 Markdown 按钮点击信号
        self.buttonPreviewMarkdown.clicked.connect(self.previewMarkdown)

        # 连接集数匹配和标题匹配文本编辑信号
        self.textEpPattern.textEdited.connect(self.setTitleText)
        self.textTitlePattern.textEdited.connect(self.setTitleText)

        # 连接身份选择变化信号
        self.menuSelectCookies.currentTextChanged.connect(self.selectCookiesChangeHandler)

        # 设置文件树列宽
        self.fileTree.setColumnWidth(0,450)

        # 标签页 2：登录网站按钮连接
        self.buttonDmhyLogin.clicked.connect(self.loginWebsite("https://share.dmhy.org/user/login"))
        self.buttonNyaaLogin.clicked.connect(self.loginWebsite("https://nyaa.si/login"))
        self.buttonAcgripLogin.clicked.connect(self.loginWebsite("https://acg.rip/users/sign_in"))
        self.buttonBangumiLogin.clicked.connect(self.loginWebsite("https://bangumi.moe/"))

        # 禁用 Nyaa 名称输入框
        self.textNyaaName.setDisabled(True)


        # 连接保存/删除身份按钮点击信号
        self.buttonSaveProfile.clicked.connect(self.saveProfile)
        self.buttonDeleteProfile.clicked.connect(self.deleteProfile)

        # 连接代理类型选择变化信号
        self.menuProxyType.currentTextChanged.connect(self.onProxySelection)
        self.onProxySelection()

        # 连接保存代理按钮点击信号
        self.buttonSaveProxy.clicked.connect(self.saveProxy)

        # 连接 Acgnx API Token 文本编辑信号
        self.textAcgnxasiaToken.textEdited.connect(self.applyAcgnxasiaAPIToken)
        self.textAcgnxglobalToken.textEdited.connect(self.applyAcgnxglobalAPIToken)
        # 连接 Cookies 文本变化信号
        self.textCookies.textChanged.connect(self.onCookiesChange)

        # 连接发布按钮点击信号
        self.buttonOKP.clicked.connect(self.publishRun)

    def changeTabHandler(self, event):
        """标签页切换事件处理
        
        Args:
            event (int): 标签页索引
        """
        if event == 1:
            # 切换到身份管理器标签页时重新加载身份配置
            self.reloadProfile()
        if event == 2:
            # 切换到杂项标签页时加载代理设置
            self.loadProxy()

    def onDragEnterEvent(self, event):
        """拖放进入事件处理
        
        Args:
            event (QDragEnterEvent): 拖放进入事件
        """
        if event.mimeData().hasUrls():
            # 接受拖放
            event.accept()
            # 设置提示文本
            self.textTorrentPath.setPlaceholderText("请在此释放鼠标")
        else:
            # 忽略拖放
            event.ignore()

    def onDropEvent(self, event):
        """拖放释放事件处理
        
        Args:
            event (QDropEvent): 拖放释放事件
        """
        # 恢复提示文本
        self.textTorrentPath.setPlaceholderText("可直接 .torrent 文件拖放到此处")
        # 获取拖放的文件列表
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        # 设置种子文件路径
        self.textTorrentPath.setText(files[0])

    def onDragLeaveEvent(self, evet):
        """拖放离开事件处理
        
        Args:
            evet (QDragLeaveEvent): 拖放离开事件
        """
        # 恢复提示文本
        self.textTorrentPath.setPlaceholderText("可直接 .torrent 文件拖放到此处")

    def loadTorrent(self):
        """加载种子文件
        
        该方法解析种子文件并在文件树中显示其内容结构。
        """

        def sizeof_fmt(num, suffix="B"):
            """格式化文件大小
            
            Args:
                num (int): 文件大小（字节）
                suffix (str): 大小单位后缀
                
            Returns:
                str: 格式化后的文件大小字符串
            """
            if num == -1:
                return ""
            
            for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
                if abs(num) < 1024.0:
                    return f"{num:3.1f} {unit}{suffix}"
                num /= 1024.0
            return f"{num:.1f} Yi{suffix}"
        
        # 清空文件树
        self.fileTree.clear()
        # 设置标题文本
        self.setTitleText()

        # 获取种子文件路径
        torrentPath = Path(self.textTorrentPath.text())
        try:
            # 解析种子文件
            data = tp.parse_torrent_file(torrentPath)
        except:
            return
        

        if 'files' not in data['info']:
            # 单文件种子
            root = QTreeWidgetItem(self.fileTree)
            root.setText(0, Path(data['info']['name']).stem)
            root.setText(1, sizeof_fmt(data['info']['length']))
            # 设置文件图标
            file_info = QFileInfo(str(data['info']['name']))
            file_icon_provider = QFileIconProvider()
            root.setIcon(0, file_icon_provider.icon(file_info))

        else:
            # 多文件种子
            data = data['info']['files']
            folder_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)

            # 创建根节点
            root = QTreeWidgetItem(self.fileTree)
            root.setText(0, torrentPath.stem)
            root.setIcon(0, folder_icon)
            root.setExpanded(True)
            self.fileTree.insertTopLevelItem(0, root)

            # 创建文件路径到长度的映射
            d = {str(x['path']):x['length'] for x in data}
            d["[]"] = root

            # 找到最长路径
            longetstPath = 0
            for file in data:
                if len(file['path']) > longetstPath:
                    longetstPath = len(file['path'])

            # 创建节点字典，-1 表示目录
            nodes = dict()

            for x in range(longetstPath + 1):
                for path, length in d.items():
                    path = eval(path)
                    if len(path) > x:
                        nodes[str(path[:x])] = -1
                    else:
                        nodes[str(path)] = length


            sorted_nodes = sorted(nodes, key=lambda x: len(eval(x)))

            for n in sorted_nodes:
                if n == "[]":
                    continue
                # 创建树节点
                item = QTreeWidgetItem(nodes[f'{eval(n)[:-1]}'])
                item.setText(0, eval(n)[-1])
                item.setText(1, sizeof_fmt(nodes[n]))
                if nodes[n] == -1:
                    # 目录图标
                    item.setIcon(0, folder_icon)
                else:
                    # 文件图标
                    file_info = QFileInfo(eval(n)[-1])
                    file_icon_provider = QFileIconProvider()
                    item.setIcon(0, file_icon_provider.icon(file_info))
                nodes[n] = item

            # 按大小排序列
            self.fileTree.sortByColumn(1, Qt.SortOrder.AscendingOrder)
            # 设置交替行颜色
            self.fileTree.setAlternatingRowColors(True)





    def selectTorrentFile(self):
        """选择种子文件
        
        打开文件对话框让用户选择种子文件。
        """
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Torrent file v1 (*.torrent)")[0]
        self.textTorrentPath.setText(fname)





    def loadConfig(self):
        """加载配置文件
        
        如果配置文件不存在，则创建默认配置文件。
        """
        path = Path(TEMPLATE_CONFIG)
        if not path.exists():
            # 创建默认配置文件
            with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as f:
                f.write('''
lastUsed: 新模板
proxy: http://127.0.0.1:7890
proxyType: 不使用代理
template:
  新模板:
    about: 
    checkAcgnxasia: false
    checkAcgnxglobal: false
    checkAcgrip: false
    checkDmhy: false
    checkNyaa: false
    description: ""
    epPattern: ""
    poster: ""
    profile: ""
    tags: "Anime"
    titlePattern: ""
    title: ""
                ''')

        with open(path, "r", encoding="utf-8") as f:
            self.conf = yaml.safe_load(f)
    
    def loadProxy(self):
        """加载代理设置"""
        conf = defaultdict(str, self.conf)
        self.menuProxyType.setCurrentText(conf['proxyType'])
        self.textProxyHost.setText(conf['proxy'])

    def saveProxy(self):
        """保存代理设置"""
        self.conf['proxyType'] = self.menuProxyType.currentText()
        self.conf['proxy'] = self.textProxyHost.text()
        with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as file:
            yaml.safe_dump(self.conf, file, encoding='utf-8',allow_unicode=True)


    def loginWebsite(self, url):
        """登录网站
        
        Args:
            url (str): 登录页面 URL
            
        Returns:
            callable: 登录函数
        """
        def login():
            # 创建网页视图并显示
            self.webview = WebEngineView(url=QUrl(url),parentWindow=self)
            self.webview.show()

        return login
    
    def getCookies(self):
        """获取 Cookies 文本
        
        Returns:
            str: Cookies 文本
        """
        return self.textCookies.toPlainText()

    def setCookies(self, cookies:str):
        """设置 Cookies 文本
        
        Args:
            cookies (str): Cookies 文本
        """
        self.textCookies.setText(cookies)

    def addCookies(self, cookies:str):
        """添加 Cookies 文本
        
        Args:
            cookies (str): 要添加的 Cookies 文本
        """
        c = self.textCookies.toPlainText()
        # 修复 URL 格式
        cookies = re.sub(r"https://\.", "https://", cookies)
        if c == "":
            # 如果当前为空，直接设置
            if len(cookies) > 0 and cookies[-1] != "\n":
                cookies += "\n"
            self.textCookies.setText(cookies)
        else:
            # 追加到现有内容
            c += cookies
            c = re.sub(r"\n\n", "", c)
            if c[-1] != "\n":
                c += "\n"
            self.textCookies.setText(c)

    def setUserAgent(self, ua:str):
        """设置用户代理
        
        Args:
            ua (str): 用户代理字符串
        """
        if not re.search(r"^user-agent:", self.textCookies.toPlainText()):
            # 如果没有 user-agent 行，添加到开头
            self.textCookies.setText(f"user-agent:\t{ua}\n" + self.textCookies.toPlainText())
        else:
            # 替换现有的 user-agent 行
            self.textCookies.setText(
                re.sub(r"^user-agent:.*\n", f"user-agent:\t{ua}\n", self.textCookies.toPlainText())
            )
            
    def updateTemplate(self):
        """更新模板显示
        
        根据选择的模板更新界面上的各个字段。
        """
        selected = self.menuTemplateSelection.currentText()
        if selected == "创建新模板":
            # 清空所有字段
            self.textTemplateName.setText("新模板")
            self.textEpPattern.clear()
            self.textTitlePattern.clear()
            self.textTitle.clear()
            self.textPoster.clear()
            self.textAbout.clear()
            self.textTags.setText("Anime")
            self.textDescription.clear()
            self.menuSelectCookies.setCurrentIndex(0)


        elif selected not in self.conf['template']:
            return
        else:
            # 加载模板配置
            conf = defaultdict(str, self.conf['template'][selected])
            self.textTemplateName.setText(selected)
            self.textEpPattern.setText(conf['epPattern'])
            self.textTitlePattern.setText(conf['titlePattern'])
            self.setTitleText()
            self.textPoster.setText(conf['poster'])
            self.textAbout.setText(conf['about'])
            self.textDescription.setText(conf['description'])
            self.reloadMenuSelectCookies()
            self.textTags.setText(conf['tags'])
            self.textTitle.setText(conf['title'])
            self.setTitleText()
            self.conf['template'][selected] = dict(conf)

            # 加载发布站点选择
            conf = defaultdict(bool, self.conf['template'][selected])
            self.checkboxDmhyPublish.setChecked(conf['checkDmhy'])
            self.checkboxNyaaPublish.setChecked(conf['checkNyaa'])
            self.checkboxBangumiPublish.setChecked(conf['checkBangumi'])
            self.checkboxAcgripPublish.setChecked(conf['checkAcgrip'])
            self.checkboxAcgnxasiaPublish.setChecked(conf['checkAcgnxasia'])
            self.checkboxAcgnxglobalPublish.setChecked(conf['checkAcgnxglobal'])
            self.conf['template'][selected] = dict(conf)

    def setTitleText(self):
        """设置标题文本
        
        根据集数匹配和标题匹配模式，从种子文件名中提取信息并生成标题。
        """
        # 获取种子文件名
        filename = Path(self.textTorrentPath.text()).name
        epPattern = self.textEpPattern.text()
        titlePattern = self.textTitlePattern.text()

        if epPattern == "" or titlePattern == "":
            return
        
        # 找到所有需要替换的标签
        replaces = re.findall(r"<\w+>", epPattern)
        # 转义正则表达式特殊字符
        epPattern = re.escape(epPattern)
        # 将标签转换为命名捕获组
        epPattern = re.sub(r"<", r"(?P<", epPattern)
        epPattern = re.sub(r">", r">.+)", epPattern)

        try:
            # 在文件名中搜索匹配
            m = re.search(epPattern, filename)
        except re.error:
            return 

        if not m:
            return

        # 替换标题中的标签
        title = titlePattern
        for i in replaces:
            title = re.sub(i, m[f'{re.sub("<|>", "", i)}'], title)
        
        self.textTitle.setText(title)

    def selectCookiesChangeHandler(self, event):
        """身份选择变化处理
        
        根据选择的身份，启用或禁用对应的发布站点复选框。
        
        Args:
            event (str): 选择的身份名称
        """
        if event == "":
            return

        cookies = self.profile['profiles'][event]['cookies']


        # 检查 dmhy Cookies
        if cookies is None or not re.search(r"https:\/\/share\.dmhy\.org", cookies):
            self.checkboxDmhyPublish.setChecked(False)
            self.checkboxDmhyPublish.setCheckable(False)
        else:
            self.checkboxDmhyPublish.setCheckable(True)

        # 检查 nyaa Cookies
        if cookies is None or not re.search(r"https:\/\/nyaa\.si", cookies):
            self.checkboxNyaaPublish.setChecked(False)
            self.checkboxNyaaPublish.setCheckable(False)
        else:
            self.checkboxNyaaPublish.setCheckable(True)

        # 检查 acg.rip Cookies
        if cookies is None or not re.search(r"https:\/\/acg\.rip", cookies):
            self.checkboxAcgripPublish.setChecked(False)
            self.checkboxAcgripPublish.setCheckable(False)
        else:
            self.checkboxAcgripPublish.setCheckable(True)

        # 检查 bangumi.moe Cookies
        if cookies is None or not re.search(r"https:\/\/bangumi\.moe", cookies):
            self.checkboxBangumiPublish.setChecked(False)
            self.checkboxBangumiPublish.setCheckable(False)
        else:
            self.checkboxBangumiPublish.setCheckable(True)

        # 检查 acgnx_asia Cookies
        if cookies is None or not re.search(r"https:\/\/share\.acgnx\.se", cookies):
            self.checkboxAcgnxasiaPublish.setChecked(False)
            self.checkboxAcgnxasiaPublish.setCheckable(False)
        else:
            self.checkboxAcgnxasiaPublish.setCheckable(True)

        # 检查 acgnx_global Cookies
        if cookies is None or not re.search(r"https:\/\/www\.acgnx\.se", cookies):
            self.checkboxAcgnxglobalPublish.setChecked(False)
            self.checkboxAcgnxglobalPublish.setCheckable(False)
        else:
            self.checkboxAcgnxglobalPublish.setCheckable(True)


    def reloadTemplate(self):
        """重新加载模板列表
        
        从配置文件加载模板列表并更新下拉菜单。
        """
        self.loadConfig()
        templateList = list(self.conf['template'].keys())
        self.menuTemplateSelection.clear()
        self.menuTemplateSelection.addItems(templateList)
        self.menuTemplateSelection.addItem("创建新模板")
        self.menuTemplateSelection.currentTextChanged.connect(self.updateTemplate)
        try:
            # 设置上次使用的模板
            self.menuTemplateSelection.setCurrentText(self.conf['lastUsed'])
            self.updateTemplate()
        except: 
            pass

        
    def saveTemplate(self):
        """保存模板
        
        将当前界面上的模板配置保存到配置文件。
        """
        templateName = self.textTemplateName.text()

        if templateName in ["", "创建新模板"]:
            self.warning(f"非法模板名\"{templateName}\"，请换个名字。")
            return
        
        if templateName in self.conf['template']:
            if not self.warning(f"即将覆盖模板\"{templateName}\"，是否确认？"):
                return
        
        # 保存模板配置
        self.conf['lastUsed'] = templateName
        self.conf['template'][templateName] = {
            'epPattern': self.textEpPattern.text(),
            'titlePattern': self.textTitlePattern.text(),
            'poster': self.textPoster.text(),
            'about': self.textAbout.text(),
            'tags': self.textTags.text(),
            'description': self.textDescription.toPlainText(),
            'profile': self.menuSelectCookies.currentText(),
            'checkDmhy': self.checkboxDmhyPublish.isChecked(),
            'checkNyaa': self.checkboxNyaaPublish.isChecked(),
            'checkBangumi': self.checkboxBangumiPublish.isChecked(),
            'checkAcgrip': self.checkboxAcgripPublish.isChecked(),
            'checkAcgnxasia': self.checkboxAcgnxasiaPublish.isChecked(),
            'checkAcgnxglobal': self.checkboxAcgnxglobalPublish.isChecked(),
            'title': self.textTitle.text()
        }

        # 写入配置文件
        with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as file:
            yaml.safe_dump(self.conf, file, encoding='utf-8',allow_unicode=True)
        
        self.reloadTemplate()
            

    def deleteTemplate(self):
        """删除模板
        
        删除当前选择的模板。
        """
        if self.warning(f'正在删除"{self.menuTemplateSelection.currentText()}"模板，删除后将无法恢复，是否继续？'):
            self.conf['template'].pop(self.menuTemplateSelection.currentText())
            with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as file:
                yaml.safe_dump(self.conf, file, encoding='utf-8',allow_unicode=True)
        
            self.reloadTemplate()

    def loadProfile(self):
        """加载身份配置
        
        如果配置文件不存在，则创建默认配置文件。
        """
        path = Path(PROFILE_CONFIG)
        if not path.exists():
            # 创建默认配置文件
            with open(path, "w", encoding="utf-8") as f:
                f.write(
'''
lastUsed: 新身份
profiles:
  新身份:
    cookies: 
    dmhyName: 
    nyaaName: 
    acgripName: 
    bangumiName: 
    acgnxasiaName: 
    acgnxglobalName: 
'''
                )
        with open(path, "r", encoding="utf-8") as f:
            self.profile = yaml.safe_load(f)

    def reloadProfile(self):
        """重新加载身份列表
        
        从配置文件加载身份列表并更新下拉菜单。
        """
        self.loadProfile()
        profileList = list(self.profile["profiles"].keys())
        self.menuProfileSelection.clear()
        self.menuProfileSelection.addItems(profileList)
        self.menuProfileSelection.addItem("创建新身份")
        self.updateProfile()
        self.menuProfileSelection.currentTextChanged.connect(self.updateProfile)
        try:
            # 设置上次使用的身份
            self.menuProfileSelection.setCurrentText(self.profile["lastUsed"])
            self.updateProfile()
        except:
            pass
        
    def updateProfile(self):
        """更新身份显示
        
        根据选择的身份更新界面上的各个字段。
        """
        
        selected = self.menuProfileSelection.currentText()
        
        if selected == "创建新身份":
            # 清空所有字段
            self.textProfileName.setText("新身份")
            self.textDmhyName.clear()
            self.textNyaaName.clear()
            self.textAcgripName.clear()
            self.textBangumiName.clear()
            self.textAcgnxasiaName.clear()
            self.textAcgnxasiaToken.clear()
            self.textAcgnxglobalName.clear()
            self.textAcgnxglobalToken.clear()
            self.textCookies.clear()

        elif selected not in self.profile["profiles"]:
            return
        else:
            # 加载身份配置
            prof = defaultdict(str, self.profile["profiles"][selected])
            
            self.textProfileName.setText(selected)
            self.textDmhyName.setText(prof['dmhyName'])
            self.textNyaaName.setText(prof['nyaaName'])
            self.textAcgripName.setText(prof['acgripName'])
            self.textBangumiName.setText(prof['bangumiName'])
            self.textAcgnxasiaName.setText(prof['acgnxasiaName'])
            self.textAcgnxglobalName.setText(prof['acgnxglobalName'])
            self.textCookies.setText(prof['cookies'])
            

            # 提取 acgnx_asia API Token
            res = re.search(r'https:\/\/share.acgnx.se\ttoken=(?P<token>.*)(\n|$)', str(prof['cookies']))
            if res:
                self.textAcgnxasiaToken.setText(res['token'])
            else:
                self.textAcgnxasiaToken.clear()
            # 提取 acgnx_global API Token
            res = re.search(r'https:\/\/www.acgnx.se\ttoken=(?P<token>.*)(\n|$)', str(prof['cookies']))
            if res:
                self.textAcgnxglobalToken.setText(res['token'])
            else:
                self.textAcgnxglobalToken.clear()

            self.profile["profiles"][selected] = dict(prof)


    def saveProfile(self):
        """保存身份
        
        将当前界面上的身份配置保存到配置文件。
        """
        profileName = self.textProfileName.text()
        
        if profileName in ["", "创建新身份"]:
            self.warning(f"非法身份名\"{profileName}\"，请换个名字。")
            return
        
        if profileName in self.profile["profiles"]:
            if not self.warning(f"即将覆盖身份\"{profileName}\", 是否确认？"):
                return
            
        # 保存身份配置
        self.profile["lastUsed"] = self.textProfileName.text()
        self.profile["profiles"][self.textProfileName.text()] = {
            'cookies': self.textCookies.toPlainText(),
            'dmhyName': self.textDmhyName.text(),
            'nyaaName': self.textNyaaName.text(),
            'acgripName': self.textAcgripName.text(),
            'bangumiName': self.textBangumiName.text(),
            'acgnxasiaName': self.textAcgnxasiaName.text(),
            'acgnxglobalName': self.textAcgnxglobalName.text(),
        }

        # 写入配置文件
        with open(PROFILE_CONFIG, "w", encoding='utf-8') as file:
            yaml.safe_dump(self.profile, file, encoding='utf-8',allow_unicode=True)
        
        self.reloadProfile()
        self.reloadMenuSelectCookies()


    def deleteProfile(self):
        """删除身份
        
        删除当前选择的身份。
        """
        if self.warning(f'正在删除"{self.menuProfileSelection.currentText()}"身份，删除后将无法恢复，是否继续？'):
            self.profile['profiles'].pop(self.menuProfileSelection.currentText())
            with open(PROFILE_CONFIG, "w", encoding='utf-8') as file:
                yaml.safe_dump(self.profile, file, encoding='utf-8',allow_unicode=True)
            
            self.reloadMenuSelectCookies()
            self.reloadProfile()


    def previewMarkdown(self):
        """预览 Markdown 内容
        
        将 Markdown 文本转换为 HTML 并在新窗口中预览。
        """
        md = markdown.markdown(self.textDescription.toPlainText())
        self.markdownWindow = MarkdownViewWindow(html=md,parentWindow=self)
        self.markdownWindow.show()

    def warning(self, message):
        """显示警告对话框
        
        Args:
            message (str): 警告消息
            
        Returns:
            bool: 用户是否点击确定
        """
        warning = WarningDialog()
        warning.label.setText(message)
        warning.show()
        return warning.exec()

    def reloadMenuSelectCookies(self):
        """重新加载身份选择菜单"""
        self.menuSelectCookies.clear()
        self.menuSelectCookies.addItems(self.profile['profiles'].keys())
        try: self.menuSelectCookies.setCurrentText(self.conf['template'][self.menuTemplateSelection.currentText()]['profile'])
        except: pass

    def onProxySelection(self):
        """代理类型选择变化处理"""
        selected = self.menuProxyType.currentText()
        if selected == "不使用代理":
            self.textProxyHost.setDisabled(True)
            return
        if selected == "HTTP":
            self.textProxyHost.setEnabled(True)
            return
        
    def applyAcgnxasiaAPIToken(self):
        """应用 Acgnx Asia API Token
        
        将输入的 API Token 添加到 Cookies 文本中。
        """
        cookies = self.textCookies.toPlainText()
        new_string, n = re.subn(
            r"https:\/\/share.acgnx.se\ttoken=.*(\n|$)", 
            f"https://share.acgnx.se\ttoken={self.textAcgnxasiaToken.text()}\n", 
            cookies)
        if n != 0:
            # 替换现有的 Token
            self.textCookies.setText(new_string)
        else:
            # 添加新的 Token
            if cookies and cookies[-1] != "\n": cookies += "\n"
            self.textCookies.setText(
                cookies + f"https://share.acgnx.se\ttoken={self.textAcgnxasiaToken.text()}\n"
            )

    def applyAcgnxglobalAPIToken(self):
        """应用 Acgnx Global API Token
        
        将输入的 API Token 添加到 Cookies 文本中。
        """
        cookies = self.textCookies.toPlainText()
        new_string, n = re.subn(
            r"https:\/\/www.acgnx.se\ttoken=.*(\n|$)", 
            f"https://www.acgnx.se\ttoken={self.textAcgnxglobalToken.text()}\n", 
            cookies)
        if n != 0:
            # 替换现有的 Token
            self.textCookies.setText(new_string)
        else:
            # 添加新的 Token
            if cookies and cookies[-1] != "\n": cookies += "\n"
            self.textCookies.setText(
                cookies + f"https://www.acgnx.se\ttoken={self.textAcgnxglobalToken.text()}\n"
            )

    def onCookiesChange(self):
        """Cookies 文本变化处理
        
        从 Cookies 文本中提取 API Token 并更新到对应的输入框。
        """
        cookies = self.textCookies.toPlainText()
        # 提取 acgnx_asia Token
        m = re.search(r"https:\/\/share.acgnx.se\ttoken=(?P<token>.*)(\n|$)", cookies)
        if m:
            self.textAcgnxasiaToken.setText(m['token'])

        # 提取 acgnx_global Token
        m = re.search(r"https:\/\/www.acgnx.se\ttoken=(?P<token>.*)(\n|$)", cookies)
        if m:
            self.textAcgnxglobalToken.setText(m['token'])



    def publishRun(self):
        """执行发布操作
        
        该方法生成 template.toml 和 cookies.txt 文件，
        然后启动 OKP.Core.exe 进行发布。
        """
        # 合法性检查
        path = self.textTorrentPath.text()
        if path == "":
            self.warning("种子文件不能为空。")
            return
        
        if not Path(path).exists():
            self.warning(f"无法找到种子文件'{path}'。")
            return
        
        if Path(path).suffix != ".torrent":
            self.warning(f"'{path}' 不是一个 .torrent 文件")
            return
        
        if self.textTitle.text() == "":
            self.warning("标题不能为空。")
            return
        
        if self.textDescription.toPlainText() == "":
            self.warning("内容不能为空。")

        # 生成 template.toml
        tags = map(lambda x: x.strip() , self.textTags.text().split(","))
        intro_templates = []

        # 转换 Markdown 到 HTML 和 BBCode
        md = self.textDescription.toPlainText()
        html = markdown.markdown(md)
        parser = HTML2PHPBBCode()
        bbcode = parser.feed(html)
        proxy = self.conf["proxy"]

        cookies = self.profile['profiles'][self.menuSelectCookies.currentText()]['cookies']
        profile = self.profile['profiles'][self.menuSelectCookies.currentText()]

        # 添加 dmhy 发布配置
        if self.checkboxDmhyPublish.isChecked() and self.checkboxDmhyPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'dmhy',
                'name': profile['dmhyName'],
                'content': html,
                }
            )
        
        # 添加 nyaa 发布配置
        if self.checkboxNyaaPublish.isChecked() and self.checkboxNyaaPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'nyaa',
                'name': profile['nyaaName'],
                'content': md,
                }
            )

        # 添加 acgrip 发布配置
        if self.checkboxAcgripPublish.isChecked() and self.checkboxAcgripPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'acgrip',
                'name': profile['acgripName'],
                'content': bbcode,
                }
            )

        # 添加 bangumi 发布配置
        if self.checkboxBangumiPublish.isChecked() and self.checkboxBangumiPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'bangumi',
                'name': profile['bangumiName'],
                'content': html,
                }
            )

        # 添加 acgnx_asia 发布配置
        if self.checkboxAcgnxasiaPublish.isChecked() and self.checkboxAcgnxasiaPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'acgnx_asia',
                'name': profile['acgnxasiaName'],
                'content': html,
                }
            )

        # 添加 acgnx_global 发布配置
        if self.checkboxAcgnxglobalPublish.isChecked() and self.checkboxAcgnxglobalPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'acgnx_global',
                'name': profile['acgnxglobalName'],
                'content': html,
                }
            )

        # 如果使用代理，添加代理配置
        if self.conf['proxyType'] == "HTTP":
            for d in intro_templates:
                d['proxy'] = proxy

        # 构建 template.toml 配置
        template_conf = {
            'display_name': self.textTitle.text(),
            'poster': self.textPoster.text(),
            'about': self.textAbout.text(),
            'filename_regex': '',
            'resolution_regex': '',
            'tags': list(tags),
            'intro_template': intro_templates
        }

        # 写入 template.toml 文件
        with open("template.toml", "w", encoding='utf-8') as f:
            toml.dump(template_conf, f)
        
        # 生成 cookies.txt 文件
        with open("cookies.txt", "w", encoding='utf-8') as f:
            f.write(self.profile['profiles'][self.menuSelectCookies.currentText()]['cookies'])
        
        # 创建控制台窗口并启动 OKP.Core.exe
        self.console = MyConsole(self)
        self.console.onFinished(self.updateCookies)
        self.console.start("OKP.Core.exe", [
            self.textTorrentPath.text(),
            "-s", str(Path.cwd().joinpath("template.toml")),
            '--cookies', str(Path.cwd().joinpath("cookies.txt"))
        ])
        self.console.show()


        
        
    def updateCookies(self, int, exitStatus):
        """更新 Cookies
        
        发布完成后，从 cookies.txt 文件中读取更新后的 Cookies 并保存。
        
        Args:
            int (int): 退出码
            exitStatus (QProcess.ExitStatus): 退出状态
        """
        if exitStatus == QProcess.ExitStatus.NormalExit:
            try:
                # 读取更新后的 Cookies
                with open("cookies.txt", "r", encoding="utf-8") as f:
                    newCookies = f.read()

                # 更新身份配置中的 Cookies
                self.profile["profiles"][self.menuSelectCookies.currentText()]["cookies"] = newCookies

                # 保存配置文件
                with open(PROFILE_CONFIG, "w", encoding="utf-8") as file:
                    yaml.safe_dump(self.profile, file, encoding='utf-8',allow_unicode=True)

                self.reloadProfile()

            except:
                return
            


class WarningDialog(QDialog, Ui_Dialog):
    """警告对话框类
    
    该类继承自 QDialog 和 Ui_Dialog，用于显示警告信息。
    """
    
    def __init__(self, *args, **kwargs):
        """初始化警告对话框
        
        Args:
            *args: 传递给父类的参数
            **kwargs: 传递给父类的关键字参数
        """
        QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)


if __name__ == '__main__':
    # 创建应用程序实例
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