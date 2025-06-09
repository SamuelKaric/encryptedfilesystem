from __future__ import annotations

from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtQuick import QQuickTextDocument
from PySide6.QtQml import QmlElement, QmlSingleton
from PySide6.QtCore import (Qt, QDir, QAbstractListModel, Slot, QFile, QTextStream,
                            QMimeDatabase, QFileInfo, QStandardPaths, QModelIndex,
                            Signal, Property, QUrl, QObject,QFileInfo, QSortFilterProxyModel)
from accounts import create_account, verify_account, get_all_users
import os
import re
from encrypt.crypto_utils import symmetric_encrypt, symmetric_decrypt

QML_IMPORT_NAME = "View"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class DBUtils(QObject):
    @Slot(str, str, QUrl, result=str)
    def login(self, username: str, password: str, certPath: QUrl) -> str:
        return verify_account(username, password, certPath.toLocalFile())
    
    @Slot(str, str, result=str)
    def register(self, username: str, password: str) -> str:
        if create_account(username, password):
            FileUtils.makeRD(username)
    
    @Slot(result=list)
    def getAllUsers(self) -> list:
        users = get_all_users()
        return users


@QmlElement
class FileUtils(QObject):

    @staticmethod
    def makeRD(name):
        dir = QDir(FileSystemModel.getDefaultRootDir())
        dir.mkdir(name)
        
    @Slot(str, QUrl, QUrl, str, QUrl, result=str)
    def downloadFile(self, user:str, source: QUrl, destination: QUrl, mode: str, certPath: QUrl) -> str:
        destination_path = os.path.join(destination.toLocalFile(), source.fileName())
        temp_path = symmetric_decrypt(user, source.toString(), mode, certPath.toLocalFile())
        if temp_path:
            QFile.copy(symmetric_decrypt(user, source.toString(), mode, certPath.toLocalFile()), destination_path)
            return "Successfully downloaded file"
        else:
            return "Not Authorized to access this file"


    @Slot(str, result=str)
    def makeDir(self, input: str) -> str:
        print(f"Creating new dir at &{input}")
        QDir(input).mkdir("New")

    @Slot(QUrl, str, result=str)
    def renameDir(self, input: QUrl, name: str) -> str:
        print(f"Rename {input} to {name}")
        full_path = input.toString()
        file_info = QFileInfo(full_path)
        dir_name = file_info.fileName()
        parent_dir = file_info.dir().absolutePath()
        QDir(parent_dir).rename(dir_name, name)

    @Slot(str, result=str)
    def deleteDir(self, input: str) -> str:
        print(f"Deleting &{input}")
        QDir(input).removeRecursively()


    @Slot(str,str, QUrl, str, QUrl, result=str)
    def addFile(self, user: str, destination: str, input: QUrl, mode: str, certPath: QUrl) -> str:
        print(f"Moving &{input} to &{destination}")
        symmetric_encrypt(user, input.toLocalFile(), destination+ r"/" + input.fileName(), mode, certPath.toLocalFile())

    @Slot(str, str, QUrl, str, str, QUrl, QUrl, result=str)
    def shareFile(self, user: str, recipiant: str, filePath: QUrl, fileName: str, mode: str, certPath: QUrl, recipiantCertPath) -> str:
        shared_path = FileSystemModel.getSharedDir() + r"/" + fileName
        raw_file = symmetric_decrypt(user, filePath.toString(), mode, certPath.toLocalFile())
        symmetric_encrypt(recipiant, raw_file, shared_path, mode, recipiantCertPath.toLocalFile())

    @Slot(str, result=str)
    def deleteFile(self, input: str) -> str:
        print(f"Deleting &{input}")
        QFile.remove(input)

    @Slot(str, str, result=str)
    def translateUrl(self, fileName: str, username: str) -> str:
        root = self.pathToQUrl(FileSystemModel.getDefaultRootDir()).toString().lower()
        return fileName.lower().replace(root, username)

    @Slot(str, result=QUrl)
    def pathToQUrl(self, path: str) -> QUrl:
        return QUrl.fromLocalFile(path)
    
    @Slot(str, result=str)
    def QMLPicker(self, fileName: str) -> str:
        ext = fileName.lower().split('.')[-1]
        match ext:
            case "pdf":
                return "PDFViewer.qml"
            case "png" | "svg" | "jpg":
                return "ImageViewer.qml"
        return "TextViewer.qml"
    

@QmlElement
@QmlSingleton
class FilteredModel(QSortFilterProxyModel):

    userChanged = Signal()
    decryptedFileReady = Signal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self._user = ""
    
    @Property(QModelIndex, constant=True)
    def rootIndex(self):
        if not self.sourceModel():
            return QModelIndex()
        return self.mapFromSource(self.sourceModel().rootIndex)
    
    @Property(str, notify=userChanged)
    def user(self):
        return self._user
    
    @user.setter
    def user(self, value):
        self._user = value
        self.invalidateFilter()
        self.userChanged.emit()
    
    @Slot(QUrl, str, QUrl, result=str)
    def readFile(self, path, mode, certPath):
        print(f"Reading file at {path} with mode {mode} and certPath {certPath}")
        return self.sourceModel().readFile(self._user, path, mode, certPath)
    
    @Slot(QUrl, str, QUrl, result=str)
    def proxy(self, source, mode, certPath):
        local_path = source.toLocalFile()
        temp = symmetric_decrypt(self._user, local_path, mode, certPath.toLocalFile())
        if temp:
            return QUrl.fromLocalFile(temp).toString()
        return ""

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.sourceModel():
            return False
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid():
            return False
        path = self.sourceModel().filePath(index)

        if self._user in path or "/shared" in path:
            return True

        for i in range(self.sourceModel().rowCount(index)):
            if self.filterAcceptsRow(i, index):
                return True
        return False


@QmlElement
@QmlSingleton
class FileSystemModel(QFileSystemModel):

    rootIndexChanged = Signal()

    @staticmethod
    def getDefaultRootDir():
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    
    @staticmethod
    def getSharedDir():
        return FileSystemModel.getDefaultRootDir()+r"/shared"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mRootIndex = QModelIndex()
        self.mDb = QMimeDatabase()
        self.setFilter(QDir.Filter.AllEntries | QDir.Filter.Hidden | QDir.Filter.NoDotAndDotDot)
        self.setInitialDirectory()

    @Slot(str, QUrl, str, QUrl, result=str)
    def readFile(self, user: str, path: QUrl, mode: str, certPath: QUrl) -> str:
        print(certPath)
        fileName = symmetric_decrypt(user, path.toLocalFile(), mode, certPath.toLocalFile())
        print(f"readFiles filename is {fileName}")
        if fileName == "":
            return ""

        file = QFile(fileName)

        mime = self.mDb.mimeTypeForFile(QFileInfo(file))
        if ('text' in mime.comment().lower()
                or any('text' in s.lower() for s in mime.parentMimeTypes())):
            if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                stream = QTextStream(file).readAll()
                file.close()
                return stream
            else:
                return self.tr("Error opening the file!")
        return self.tr("File type not supported or not accessable!")

    def setInitialDirectory(self, path=None):
        if path is None:
            path = self.getDefaultRootDir()
        url = QUrl.fromLocalFile(path) if isinstance(path, str) else path
        if url.isValid():
            self.setRootPath(url.toLocalFile())
            self.setRootIndex(self.index(url.toLocalFile()))
        else:
            self.setRootPath(self.getDefaultRootDir())
            self.setRootIndex(self.index(self.getDefaultRootDir()))
        dir = QDir(path)
        dir.mkdir("shared")

    def columnCount(self, parent):
        return 1

    @Property(QModelIndex, notify=rootIndexChanged)
    def rootIndex(self):
        return self.mRootIndex

    def setRootIndex(self, index):
        if (index == self.mRootIndex):
            return
        self.mRootIndex = index
        self.rootIndexChanged.emit()


@QmlElement
class LineNumberModel(QAbstractListModel):

    lineCountChanged = Signal()

    def __init__(self, parent=None):
        self.mLineCount = 0
        super().__init__(parent=parent)

    @Property(int, notify=lineCountChanged)
    def lineCount(self):
        return self.mLineCount

    @lineCount.setter
    def lineCount(self, n):
        if n < 0:
            print("lineCount must be greater then zero")
            return
        if self.mLineCount == n:
            return

        if self.mLineCount < n:
            self.beginInsertRows(QModelIndex(), self.mLineCount, n - 1)
            self.mLineCount = n
            self.endInsertRows()
        else:
            self.beginRemoveRows(QModelIndex(), n, self.mLineCount - 1)
            self.mLineCount = n
            self.endRemoveRows()

    def rowCount(self, parent):
        return self.mLineCount

    def data(self, index, role):
        if not self.checkIndex(index) or role != Qt.ItemDataRole.DisplayRole:
            return
        return index.row()
