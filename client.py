import socket
import threading
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QInputDialog,
)
from PyQt5.QtGui import QFont


class MessageHandler:
    def __init__(self, message_display):
        self.message_display = message_display

    def display_message(self, message):
        self.message_display.append(message)


class ClientApp(QMainWindow):
    def __init__(self, host="localhost", port=12345):
        super().__init__()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        self.username = self.request_username()
        self.client_socket.sendall(self.username.encode("utf-8"))

        self.initUI()  # Initialize UI first
        self.message_handler = MessageHandler(
            self.message_display
        )  # Now self.message_display is initialized

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def request_username(self):
        username, ok = QInputDialog.getText(self, "Username", "Enter your username:")
        if ok and username:
            return username
        return "Anonymous"  # Fallback username

    def initUI(self):
        self.setWindowTitle("Chat Client")
        self.setGeometry(300, 300, 600, 400)

        self.layout = QVBoxLayout()

        self.message_display = QTextEdit(self)
        self.message_display.setReadOnly(True)
        self.message_display.setFont(QFont("Arial", 14))

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter your message...")
        self.input_field.setFont(QFont("Arial", 14))

        self.send_button = QPushButton("Send", self)
        self.send_button.setFont(QFont("Arial", 14))
        self.send_button.clicked.connect(self.send_message)

        self.layout.addWidget(QLabel("Messages:"))
        self.layout.addWidget(self.message_display)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.send_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def send_message(self):
        message = self.input_field.text()
        if message.strip():
            self.client_socket.sendall(message.encode("utf-8"))
            self.message_handler.display_message(f"You: {message}")
            self.input_field.clear()

    def receive_messages(self):
        while True:
            try:
                response = self.client_socket.recv(1024).decode("utf-8")
                if response:
                    self.message_handler.display_message(response)
            except Exception as e:
                print(f"An error occurred while receiving: {e}")
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ClientApp()
    client.show()
    sys.exit(app.exec_())
