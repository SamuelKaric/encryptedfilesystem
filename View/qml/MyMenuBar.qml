import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import View

MenuBar {
    id: root

    required property ApplicationWindow dragWindow
    property alias infoText: windowInfo.text
    property bool logginState: true

    delegate: MenuBarItem {
        id: menuBarItem
        enabled: !logginState
        contentItem: Text {
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            text: menuBarItem.text
            font: menuBarItem.font
            elide: Text.ElideRight
            color: menuBarItem.highlighted ? Colors.textFile : Colors.text
            opacity: enabled ? 1.0 : 0.3
        }

        background: Rectangle {
            id: background

            color: menuBarItem.highlighted ? Colors.selection : "transparent"
            Rectangle {
                id: indicator

                width: 0; height: 3
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom

                color: Colors.color1
                states: State {
                    name: "active"
                    when: menuBarItem.highlighted
                    PropertyChanges {
                        indicator.width: background.width - 2
                    }
                }
                transitions: Transition {
                    NumberAnimation {
                        properties: "width"
                        duration: 175
                    }
                }
            }
        }
    }

    contentItem: RowLayout {
        id: windowBar

        Layout.fillWidth: true
        Layout.fillHeight: true

        spacing: root.spacing
        Repeater {
            id: menuBarItems

            Layout.alignment: Qt.AlignLeft
            model: root.contentModel
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Text {
                id: windowInfo

                width: parent.width; height: parent.height
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                leftPadding: windowActions.width
                color: Colors.text
                clip: true
            }
        }

        RowLayout {
            id: windowActions

            Layout.alignment: Qt.AlignRight
            Layout.fillHeight: true

            spacing: 0

            component InteractionButton: Rectangle {
                id: interactionButton

                signal action()
                property alias hovered: hoverHandler.hovered

                Layout.fillHeight: true
                Layout.preferredWidth: height

                color: hovered ? Colors.background : "transparent"
                HoverHandler {
                    id: hoverHandler
                }
                TapHandler {
                    id: tapHandler
                    onTapped: interactionButton.action()
                }
            }

            InteractionButton {
                id: minimize

                onAction: root.dragWindow.showMinimized()
                Rectangle {
                    anchors.centerIn: parent
                    color: parent.hovered ? Colors.iconIndicator : Colors.icon
                    height: 2
                    width: parent.height - 14
                }
            }

            InteractionButton {
                id: maximize

                onAction: root.dragWindow.showMaximized()
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 7
                    border.color: parent.hovered ? Colors.iconIndicator : Colors.icon
                    border.width: 2
                    color: "transparent"
                }
            }

            InteractionButton {
                id: close

                color: hovered ? "#ec4143" : "transparent"
                onAction: root.dragWindow.close()
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.height - 8; height: 2

                    rotation: 45
                    antialiasing: true
                    transformOrigin: Item.Center
                    color: parent.hovered ? Colors.iconIndicator : Colors.icon

                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.height
                        height: parent.width

                        antialiasing: true
                        color: parent.color
                    }
                }
            }
        }
    }

    background: Rectangle {
        color: Colors.surface2
        DragHandler{
            target: null
            onActiveChanged: {
                if (active) root.dragWindow.startSystemMove()
            }
        }
    }
}
