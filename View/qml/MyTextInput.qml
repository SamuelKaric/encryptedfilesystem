import QtQuick
import QtQuick.Controls


Rectangle {
    id: root
    width: 200
    height: 40
    color: Colors.surface1
    border.color: Colors.surface2
    radius: 4

    property string propText: ""
    property alias text: input.text
    property bool hide: false

    TextInput {
        id: input
        anchors.fill: parent
        anchors.margins: 8
        focus: true
        color: Colors.text
        echoMode: hide? TextInput.Password : TextInput.Normal
    }

    Text {
        text: root.propText
        color: Colors.disabledText
        anchors.verticalCenter: parent.verticalCenter
        anchors.margins: 8
        visible: input.text.length === 0
    }
}