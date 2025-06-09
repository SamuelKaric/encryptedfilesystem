import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import View
import FileUtilsModule

pragma ComponentBehavior: Bound

ApplicationWindow {
    id: root

    property bool expandPath: false
    property bool showLineNumbers: true
    property url currentFilePath
    property bool logginState: true
    property string username
    property string password
    property string mode: "AES"
    property url certPath

    width: 1000
    height: 600
    minimumWidth: 200
    minimumHeight: 100
    visible: true
    color: Colors.background
    flags: Qt.Window | Qt.FramelessWindowHint
    title: qsTr("Encrypted File System")

    function getInfoText() : string {
        let out = root.currentFilePath.toString()
        if (!out)
            return qsTr("Encrypted File System")
        return root.expandPath ? fileUtils.translateUrl(out, "") : out.substring(out.lastIndexOf("/") + 1, out.length)
    }

        
    FileUtils{
        id: fileUtils
    }

    DBUtils{
        id: dbUtils
    }

    LoginWindow{
        id: login
        visible: logginState
        
        onLogin: (username, password) => {
            login.message = dbUtils.login(username, password, certPath)
            console.log(login.message)
            if ("Password validated." === login.message){
                logginState = false
                root.username = username
                root.certPath = certPath
            }
            console.log(root.username)
        }
        onRegister: (username, password) => {
            login.message = dbUtils.register(username, password)
            console.log(login.message)
        }

    }

    menuBar: MyMenuBar {
        dragWindow: root
        logginState: root.logginState
        infoText: root.getInfoText()
        MyMenu {
            title: qsTr("File")
            Action {
                text: root.expandPath ? qsTr("Toggle Short Path")
                                      : qsTr("Toggle Expand Path")
                enabled: root.currentFilePath
                onTriggered: root.expandPath = !root.expandPath
            }
            Action {
                text: qsTr("Logout")
                onTriggered: () => {
                    logginState = true;
                    username = "";
                }
            }
            Action {
                text: qsTr("Exit")
                onTriggered: Qt.exit(0)
                shortcut: StandardKey.Quit
            }
        }
        MyMenu{
            title: qsTr("Encryption")
                Action {
                    text: qsTr("AES")
                    onTriggered: {
                        root.mode = "AES"
                    }
                }
                Action {
                    text: qsTr("ChaCha20")
                    onTriggered: {
                        root.mode = "ChaCha20"
                    }
                }
                Action {
                    text: qsTr("ARC4")
                    onTriggered: { 
                        root.mode = "ARC4"
                    }
                }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0


        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !logginState

            handle: Rectangle {
                implicitWidth: 10
                color: SplitHandle.pressed ? Colors.color2 : Colors.background
                border.color: SplitHandle.hovered ? Colors.color2 : Colors.background
                opacity: SplitHandle.hovered || navigationView.width < 15 ? 1.0 : 0.0

                Behavior on opacity {
                    OpacityAnimator {
                        duration: 1400
                    }
                }
            }

            Rectangle {
                id: navigationView
                color: Colors.surface1
                SplitView.preferredWidth: 250
                SplitView.fillHeight: true
                FileSystemView {
                    id: fileSystemView
                    color: Colors.surface1
                    anchors.fill: parent
                    user: username
                    mode: root.mode
                    certPath: root.certPath
                    onFileClicked: path => {
                        root.currentFilePath = fileUtils.pathToQUrl(path)
                    }
                }
            }

            Viewer {
                id: viewer
                showLineNumbers: root.showLineNumbers
                currentFilePath: root.currentFilePath
                mode: root.mode
                certPath: root.certPath
                SplitView.fillWidth: true
                SplitView.fillHeight: true
            }
        }
    }

    Button {
        icon.width: 20; icon.height: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        rightPadding: 3
        bottomPadding: 3

        icon.source: "./resources/resize.svg"
        icon.color: hovered ? Colors.iconIndicator : Colors.icon

        background: null
        checkable: false
        display: AbstractButton.IconOnly
        onPressed: root.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
    }
}
