import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Dialogs

Rectangle{
    id: root
    anchors.fill: parent
    color: Colors.background
    anchors.centerIn: parent

    property string username
    property string password
    property string message
    property string certPath

    signal login(string username, string password)
    signal register(string username, string password)

    ColumnLayout{
        spacing: 20
        anchors.verticalCenter: root.verticalCenter
        anchors.horizontalCenter: root.horizontalCenter

        MyTextInput{
            id: usernameInput
            propText: "Username"
            text: username
            onTextChanged: root.username = text
        }

        MyTextInput{
            id: passwordInput
            hide: true
            propText: "Password"
            text: password
            onTextChanged: root.password = text
        }

        FileDialog{
            id: certDialog
            nameFilters: ["PEM files (*.pem)"]
            onAccepted: {
                root.message = "Selected cert: " + certDialog.file
                certPath = certDialog.file
            }
        }

        Button{
            id: certButton
            text: "Choose Cert"

            contentItem: Text {
                text: certButton.text
                opacity: enabled ? 1.0: 0.3
                color: certButton.down ? Colors.disabledText: Colors.text
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle{
                implicitWidth: 200
                implicitHeight: 40
                opacity: enabled? 1.0 : 0.3
                border.color: Colors.selection
                color: Colors.surface2
            }

            onClicked: certDialog.open()
        }
        RowLayout{
            Button{
                id: logButton
                text: "Log In"

                contentItem: Text {
                    text: logButton.text
                    opacity: enabled ? 1.0: 0.3
                    color: logButton.down ? Colors.disabledText: Colors.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle{
                    implicitWidth: 100
                    implicitHeight: 40
                    opacity: enabled? 1.0 : 0.3
                    border.color: Colors.selection
                    color: Colors.surface2
                }

                onClicked: root.login(username, password)
            }

            Button{
                id: regButton
                text: "Register"

                contentItem: Text {
                    text: regButton.text
                    opacity: enabled ? 1.0: 0.3
                    color: regButton.down ? Colors.disabledText: Colors.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle{
                    implicitWidth: 100
                    implicitHeight: 40
                    opacity: enabled? 1.0 : 0.3
                    border.color: Colors.selection
                    color: Colors.surface2
                }

                onClicked: root.register(username, password)
            }
        }

    }

}