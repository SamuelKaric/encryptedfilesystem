import QtQuick
import View
import FileUtilsModule

pragma ComponentBehavior: Bound


Rectangle {
    id: root

    property url currentFilePath
    property int currentLineNumber: -1
    color: Colors.background
    required property bool showLineNumbers
    visible: true

    property bool isPDF: currentFilePath.toString().endsWith(".pdf")
    property bool isImage: currentFilePath.toString().endsWith(".png")
    property bool validFilePath: (currentFilePath && currentFilePath.toString() !=="")

    Loader {
        id: loader
        anchors.fill: parent
        source: (currentFilePath && currentFilePath.toString() !=="") ? (fileUtils.QMLPicker(currentFilePath.toString())): ""

        onLoaded: {
            if(item){
                item.source = currentFilePath;
                if(item.source === "TextViewer.qml"){
                    console.log(currentFilePath, "text")
                    item.showLineNumbers = showLineNumbers;
                }   
            }
        }

        onSourceChanged: {
            if (item) {
                item.source = currentFilePath;
            }
        }
    }

    onCurrentFilePathChanged: {
        loader.source = "";
        loader.source = (currentFilePath && currentFilePath.toString() !=="") ? (fileUtils.QMLPicker(currentFilePath.toString())): ""
    }

}
