import QtQuick
import QtQuick.Layouts
import View

Rectangle{
    id: root
    anchors.fill: parent
    color: Colors.background
    property url source: "../resources/test.svg"
    property string mode: "AES"
    property url certPath: ""

    Flickable {
        id: flickable
        anchors.fill: parent
        clip: true

        contentWidth: image.paintedWidth
        contentHeight: image.paintedHeight

        Image {
            id: image
            source: FilteredModel.proxy(root.source, mode, certPath)
            fillMode: Image.PreserveAspectFit
        }
    }

}