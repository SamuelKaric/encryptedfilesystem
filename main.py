from editormodels import FileUtils, FileSystemModel, FilteredModel
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonInstance
from PySide6.QtCore import qVersion
from accounts import create_table

import sys
import os

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setApplicationName("EFS")

    fs_model = FileSystemModel()
    filtered_model = FilteredModel()
    filtered_model.setSourceModel(fs_model)

    qmlRegisterType(FileUtils, "FileUtilsModule", 1, 0, "FileUtils")
    create_table()


    qmlRegisterSingletonInstance(FileSystemModel, "View", 1, 0, "FileSystemModel", fs_model)
    qmlRegisterSingletonInstance(FilteredModel, "View", 1, 0, "FilteredModel", filtered_model)

    engine = QQmlApplicationEngine()
    engine.addImportPath(sys.path[0])

    engine.loadFromModule("View", "Main")

    if not engine.rootObjects():
        sys.exit(-1)


    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
