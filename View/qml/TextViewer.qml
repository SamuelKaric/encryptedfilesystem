import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import View


pragma ComponentBehavior: Bound

Rectangle {
    id: root

    property url source
    property bool showLineNumbers: true
    property alias text: textArea
    property int currentLineNumber: -1
    property int rowHeight: Math.ceil(fontMetrics.lineSpacing)

    color: Colors.background

    RowLayout {
        anchors.fill: parent

        Flickable {
            id: lineNumbers

            Layout.preferredWidth: fontMetrics.averageCharacterWidth
                * (Math.floor(Math.log10(textArea.lineCount)) + 1) + 10
            Layout.fillHeight: true

            interactive: false
            contentY: editorFlickable.contentY
            visible: textArea.text !== "" && root.showLineNumbers

            Column {
                anchors.fill: parent
                Repeater {
                    id: repeatedLineNumbers

                    model: LineNumberModel {
                        lineCount: textArea.text !== "" ? textArea.lineCount : 0
                    }

                    delegate: Item {
                        required property int index

                        width: parent.width
                        height: root.rowHeight
                        Label {
                            id: numbers

                            text: parent.index + 1

                            width: parent.width
                            height: parent.height
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter

                            color: Colors.text
                            font: textArea.font
                        }
                    }
                }
            }
        }

        Flickable {
            id: editorFlickable

            property alias textArea: textArea

            Layout.fillHeight: true
            Layout.fillWidth: true

            boundsBehavior: Flickable.StopAtBounds

            TextArea.flickable: TextArea {
                id: textArea
                anchors.fill: parent

                focus: false
                topPadding: 0
                leftPadding: 10

                text: FileSystemModel.readFile(root.source)
                tabStopDistance: fontMetrics.averageCharacterWidth * 4

                color: Colors.textFile
                selectedTextColor: Colors.textFile
                selectionColor: Colors.selection

                textFormat: TextEdit.PlainText
                renderType: Text.QtRendering
                selectByMouse: true
                background: null
            }

            FontMetrics {
                id: fontMetrics
                font: textArea.font
            }
        }
    }
}
