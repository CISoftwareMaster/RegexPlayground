import io
import sys
import re
from random import randint
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# our example document
example = """A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9

All Aardvarks must beam their bacon (what?!)
I just want to include that word in a sentence,
and of course, it ended up not making sense.
"""


class RPRegexpHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.pattern = None
        self.matchFormat = QTextCharFormat()

    @pyqtSlot(str)
    def changeRegexpPattern(self, pattern):
        try:
            self.pattern = re.compile(pattern)
        except:
            self.pattern = None

        # update highlighting
        self.rehighlight()

    def highlightBlock(self, string):
        if self.pattern is not None:
            for match in self.pattern.finditer(string):
                # randomise background colour for each match
                self.matchFormat.setBackground(QColor(randint(200, 255), randint(200, 255), randint(150, 255)))
                # highlight our matches
                self.setFormat(match.start(), abs(match.end()-match.start()), self.matchFormat)


class RPHighlightedTextArea(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        # initialise our highlighter
        self.highlighter = RPRegexpHighlighter(self.document())
        # update font size
        font = self.font()
        font.setPointSize(18)
        self.setFont(font)


class RPMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # initialise our inputs
        regexpInput = QLineEdit()
        self.textarea = RPHighlightedTextArea()

        # unified toolbar / titlebar look for macOS
        self.setUnifiedTitleAndToolBarOnMac(True)

        # add some text to our text area just so we can begin working with something
        self.textarea.setPlainText(example)

        # initialise our super simple toolbar
        toolBar = QToolBar()
        toolBar.setMovable(False)
        self.addToolBar(toolBar)

        # open action
        open = toolBar.addAction("Open Text File")
        open.setIcon(QIcon.fromTheme("open"))
        open.setShortcut("ctrl+o")

        # open dialog
        openD = QFileDialog(self)
        openD.setAcceptMode(QFileDialog.AcceptOpen)
        openD.setFileMode(QFileDialog.ExistingFile)
        open.triggered.connect(openD.exec)
        openD.fileSelected.connect(self.openFile)

        # reset action
        reset = toolBar.addAction("Reset Text")
        reset.setIcon(QIcon.fromTheme("new"))
        reset.setShortcut("ctrl+n")
        reset.triggered.connect(self.resetDocument)

        # force highlight update
        uhighlight = toolBar.addAction("Change highlight colours")
        uhighlight.setShortcut("ctrl+u")
        uhighlight.triggered.connect(self.updateHighlight)

        # initialise our layout
        view = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(regexpInput)
        layout.addWidget(self.textarea)
        view.setLayout(layout)

        # connect our regexp input to our text editor
        regexpInput.textChanged.connect(self.textarea.highlighter.changeRegexpPattern)

        # our starting regular expression
        regexpInput.setPlaceholderText("Enter your regular expression here...")
        regexpInput.setText("\w+")

        # finalise
        self.setWindowTitle("Regular Expressions Playgrounds")
        self.setMinimumSize(640, 480)
        self.setCentralWidget(view)

    @pyqtSlot(str)
    def openFile(self, o):
        try:
            with io.open(o, "r", encoding="utf-8") as file:
                self.textarea.setPlainText(file.read())
                file.close()
        except FileNotFoundError:
            print(f"Sorry, but the file '{o}' can't be found!")
        except IOError:
            print(f"Sorry, but we can't open '{o}'")

    @pyqtSlot()
    def resetDocument(self):
        self.textarea.setPlainText(example)

    @pyqtSlot()
    def updateHighlight(self):
        self.textarea.highlighter.rehighlight()

if __name__ == "__main__":
    # initialise our app
    app = QApplication(sys.argv)
    window = RPMainWindow()
    window.show()
    sys.exit(app.exec_())
