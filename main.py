from editormodels import FileUtils
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtCore import qVersion
from accounts import create_table

import sys
import os

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setApplicationName("EFS")

    qmlRegisterType(FileUtils, "FileUtilsModule", 1, 0, "FileUtils")

    create_table()

    engine = QQmlApplicationEngine()
    engine.addImportPath(sys.path[0])

    engine.loadFromModule("View", "Main")

    if not engine.rootObjects():
        sys.exit(-1)


    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
