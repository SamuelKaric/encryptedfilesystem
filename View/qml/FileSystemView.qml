import QtQuick
import QtQuick.Effects
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import View

pragma ComponentBehavior: Bound

Rectangle {
    id: root

    signal fileClicked(url filePath)
    property alias rootIndex: fileSystemTreeView.rootIndex

    FileUtils{
        id: fileUtils
    }


    TreeView {
        id: fileSystemTreeView

        property int lastIndex: -1

        anchors.fill: parent
        model: FileSystemModel
        rootIndex: FileSystemModel.rootIndex
        boundsBehavior: Flickable.StopAtBounds
        boundsMovement: Flickable.StopAtBounds
        clip: true

        Component.onCompleted: fileSystemTreeView.toggleExpanded(0)

        delegate: TreeViewDelegate {
            id: treeDelegate
            indentation: 8
            implicitWidth: fileSystemTreeView.width > 0 ? fileSystemTreeView.width : 250
            implicitHeight: 25

            required property int index
            required property url filePath
            required property string fileName

            indicator: Image {
                id: directoryIcon

                x: treeDelegate.leftMargin + (treeDelegate.depth * treeDelegate.indentation)
                anchors.verticalCenter: parent.verticalCenter
                source: treeDelegate.hasChildren ? (treeDelegate.expanded
                            ? "../resources/folder_open.svg" : "../resources/folder_closed.svg")
                        : "../resources/generic_file.svg"
                sourceSize.width: 20
                sourceSize.height: 20
                fillMode: Image.PreserveAspectFit

                smooth: true
                antialiasing: true
                asynchronous: true
            }

            contentItem: TextField {
                id: textField
                text: treeDelegate.fileName
                color: Colors.text
                readOnly: true
                enabled: !readOnly
                background: Rectangle {
                    implicitWidth: parent.width
                    implicitHeight: parent.height
                    color: textField.readOnly ? Colors.surface1 : Colors.active 
                    border.color: textField.readOnly ? "transparent" : Colors.selection
                }
                onAccepted: {
                    textField.readOnly = true
                    fileUtils.renameDir(filePath, text)
                }
            }

            background: Rectangle {
                color: (treeDelegate.index === fileSystemTreeView.lastIndex)
                    ? Colors.selection
                    : (hoverHandler.hovered ? Colors.active : "transparent")
            }

            MultiEffect {
                id: iconOverlay

                anchors.fill: directoryIcon
                source: directoryIcon
                colorization: 1.0
                brightness: 1.0
                colorizationColor: {
                    const isFile = treeDelegate.index === fileSystemTreeView.lastIndex
                                    && !treeDelegate.hasChildren;
                    if (isFile)
                        return Qt.lighter(Colors.folder, 3)

                    const isExpandedFolder = treeDelegate.expanded && treeDelegate.hasChildren;
                    if (isExpandedFolder)
                        return Colors.color2
                    else
                        return Colors.folder
                }
            }

            HoverHandler {
                id: hoverHandler
            }

            TapHandler {
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                onSingleTapped: (eventPoint, button) => {
                    switch (button) {
                        case Qt.LeftButton:
                            fileSystemTreeView.toggleExpanded(treeDelegate.row)
                            fileSystemTreeView.lastIndex = treeDelegate.index
                            if (!treeDelegate.hasChildren){
                                root.fileClicked(treeDelegate.filePath)
                            }
                        break;
                        case Qt.RightButton:
                            if (treeDelegate.hasChildren){
                                contextFolderMenu.popup();
                            }
                            else 
                                contextFileMenu.popup();
                        break;
                    }
                }
            }

            FileDialog{
                id: importDialog
                nameFilters: ["Text files (*.txt *.html *.htm *.sql *key)", "PDF files(*.pdf)", "Image files(*.svg *.png *.jpg)"]
                onAccepted: {
                    fileUtils.addFile(filePath, selectedFile)
                }
            }
            FolderDialog{
                id: downloadDialog
                onAccepted: {
                    fileUtils.downloadFile(filePath, currentFolder)
                }
            }

            MyMenu {
                id: contextFolderMenu
                Action {
                    text: qsTr("Add to folder")
                    onTriggered: {
                        importDialog.open()

                    }
                }
                Action {
                    text: qsTr("Create Directory")
                    onTriggered: { 
                        fileUtils.makeDir(filePath)
                    }
                }
                Action {
                    text: qsTr("Rename")
                    onTriggered: { 
                        textField.readOnly = false
                    }
                }
                Action {
                    text: qsTr("Delete")
                    onTriggered: { 
                        fileUtils.deleteDir(filePath)
                    }
                }
            }
            MyMenu {
                id: contextFileMenu
                Action {
                    text: qsTr("Download file")
                    onTriggered: {
                        downloadDialog.open()
                    }
                }
                Action {
                    text: qsTr("Delete")
                    onTriggered: { 
                        fileUtils.deleteFile(filePath)
                    }
                }
            }
        }

        ScrollIndicator.vertical: ScrollIndicator {
            active: true
            implicitWidth: 15

            contentItem: Rectangle {
                implicitWidth: 6
                implicitHeight: 6

                color: Colors.color1
                opacity: fileSystemTreeView.movingVertically ? 0.5 : 0.0

                Behavior on opacity {
                    OpacityAnimator {
                        duration: 500
                    }
                }
            }
        }
    }
}
