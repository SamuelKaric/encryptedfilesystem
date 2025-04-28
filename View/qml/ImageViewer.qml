import QtQuick
import QtQuick.Layouts

Rectangle{
    id: root
    anchors.fill: parent
    color: Colors.background
    property url source: "../resources/test.svg"

    Flickable {
        id: flickable
        anchors.fill: parent
        clip: true

        contentWidth: image.paintedWidth
        contentHeight: image.paintedHeight

        Image {
            id: image
            source: root.source
            fillMode: Image.PreserveAspectFit
        }
    }

}