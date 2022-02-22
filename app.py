from threading import Thread
from PyQt5.QtCore import Qt, QEvent, QEventLoop

# import pyqt5 widgets
from PyQt5.QtWidgets import (
  QApplication,
  QMainWindow,
  QMessageBox,
  QLabel,
  QHBoxLayout,
  QPushButton,
  QLineEdit,
  QScrollArea,
  QVBoxLayout,
  QGridLayout,
  QWidget,
)

from functions import start_app
class ChatUI(QApplication):
  def __init__(self, setState, getState):
    # initialize the application
    super(QApplication, self).__init__([])

    # set title and icon of gui
    self.setApplicationName('Telegram Autoposter by Gifford - giffordcostly@gmail.com')

    # change styles to fusion
    self.setStyle('Fusion')

    # create a window and load it
    self.window = self.Window(setState, getState)

    # start the script
    script = Thread(target=start_app, args=[setState, getState])
    script.start()

  def show_popup(self, message='It\'s working!'):
    """Displays a popup message.
    Args:
        message (str, optional): The message to display. Defaults to 'It\'s working!'.
    
    Example:
        app.show_popup(message='Some Message')
    """
    messageBox = QMessageBox()
    messageBox.setText(message)
    messageBox.exec_()

  def refresh(self):
    """Refreshes the browser by revisiting the current link
    """
    self.window.engine.reload()
  class Window(QMainWindow):
    code = ""

    states = {}

    def __init__(self, setState, getState):
      # create a connection
      super(QMainWindow, self).__init__()
      self.app = ChatUI.instance()


      def on_click():
        if self.button.text() != "Pause":
          setStatus("Restarting the Script...")
          text = "Pause"
          setState("paused", False)
          codebox.setDisabled(True)
        else:
          setStatus("Pausing the Script...")
          setState("paused", True)
          text = "Start"

        self.button.setText(text)

      def setStatus(text):
        setState("messages", getState("messages") + "\n" + text)
      
      def setCode():
        setState("code", True)
        setState("codeText", codebox.text())
        codebox.setDisabled(True)

      container = QGridLayout(spacing=1)
      container.setAlignment(Qt.AlignTop)

      # messages label
      self.message = QLabel("Messages:")
      self.output = ScrollLabel()
      self.output.setText(getState("messages"))

      # control center
      control = QHBoxLayout()
      control.addWidget(QLabel("Delay Seconds:"))
      ctrlbox = QLineEdit()
      ctrlbox.move(20, 20)
      ctrlbox.setText(getState("delay"))
      control.addWidget(ctrlbox)
      controlWidget = QWidget()
      controlWidget.setLayout(control)

      # code send center
      code = QHBoxLayout()
      codeText = QLabel("Enter code for:")
      code.addWidget(codeText)
      codebox = QLineEdit()
      codebox.setDisabled(True)
      codebox.move(20, 20)
      codebox.returnPressed.connect(setCode)
      code.addWidget(codebox)
      codeWidget = QWidget()
      codeWidget.setLayout(code)

      self.button = QPushButton('Pause', self)
      self.button.move(20,80)
      self.button.clicked.connect(on_click)

      # add widgets to container
      container.addWidget(QLabel("MESSAGES"), 0, 0)
      container.addWidget(self.output, 1, 0)
      container.addWidget(QLabel(""), 2, 0)
      container.addWidget(QLabel("CONTROL"), 3, 0)
      container.addWidget(codeWidget, 4, 0, Qt.AlignRight)
      container.addWidget(controlWidget, 4, 0, Qt.AlignLeft)
      container.addWidget(self.button, 4, 2)

      # create the engine to bind
      widget = QWidget()
      widget.setLayout(container)
      self.setCentralWidget(widget)

      def setOutput():
        while True:
          try: self.output.setText(getState("messages"))
          except: pass
      Thread(target=setOutput).start()
      def setCodeText():
        while True:
          try: codebox.setDisabled(getState("code"))
          except: pass
      Thread(target=setCodeText).start()
      def setDelay():
        while True:
          try: setState("delay", ctrlbox.text())
          except: pass
      Thread(target=setDelay).start()
      # display the appropriate screen
      self.show()

class ScrollLabel(QScrollArea):
  # constructor
  def __init__(self, *args, **kwargs):
    QScrollArea.__init__(self, *args, **kwargs)

    # making widget resizable
    self.setWidgetResizable(True)

    self.setFixedWidth(500)
    self.setFixedHeight(200)

    # making qwidget object
    content = QWidget(self)
    self.setWidget(content)

    # vertical box layout
    lay = QVBoxLayout(content)

    # creating label
    self.label = QLabel(content)

    # setting alignment to the text
    self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    # making label multi-line
    self.label.setWordWrap(True)

    # adding label to the layout
    lay.addWidget(self.label)

  # the setText method
  def setText(self, text):
    # setting text to the label
    self.label.setText(text)
