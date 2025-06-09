import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Pdf

Rectangle {
    id: root
    anchors.fill:parent
    color: Colors.background
    visible: true
    property url source: "../resources/test.pdf"
    property url sourcee: "../resources/test.pdf"

    ToolBar {
        id: toolbar
        height: 42
        width: parent.width
        RowLayout {
            height: parent.height
            width: parent.width
            visible: true
            anchors.rightMargin: 6
            SpinBox {
                id: currentPageSB
                from: 1
                to: document.pageCount
                editable: true
                value: view.currentPage + 1
                onValueModified: view.goToPage(value - 1)
                Shortcut {
                    sequence: StandardKey.MoveToPreviousPage
                    onActivated: view.goToPage(currentPageSB.value - 2)
                }
                Shortcut {
                    sequence: StandardKey.MoveToNextPage
                    onActivated: view.goToPage(currentPageSB.value)
                }
            }
        }
    }

    PdfScrollablePageView {
        id: view
        anchors.top: toolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        document: PdfDocument {
            id: document
            source: Qt.resolvedUrl(Qt.url(root.sourcee))
            onPasswordRequired: passwordDialog.open()
        }
    }
}
