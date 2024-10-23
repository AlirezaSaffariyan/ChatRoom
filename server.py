import socket
import threading
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLabel,
    QInputDialog,
)
from PyQt5.QtGui import QFont


class Logger:
    def log_message(self, log_display, message):
        log_display.append(message)


class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.clients = {}
        self.initUI()
        self.start_server()

    def initUI(self):
        self.setWindowTitle("Chat Server")
        self.setGeometry(300, 300, 600, 400)

        self.layout = QVBoxLayout()

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Arial", 14))

        self.layout.addWidget(QLabel("Server Logs:"))
        self.layout.addWidget(self.log_display)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def start_server(self, host="localhost", port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.logger.log_message(
            self.log_display, "Server started, waiting for connections..."
        )

        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            conn, addr = self.server_socket.accept()
            self.logger.log_message(
                self.log_display, f"Connection established with {addr}"
            )
            threading.Thread(
                target=self.handle_client, args=(conn, addr), daemon=True
            ).start()

    def handle_client(self, conn, addr):
        username = self.request_username(conn)
        self.clients[conn] = username

        while True:
            try:
                data = conn.recv(1024).decode("utf-8")
                if not data:
                    break
                self.logger.log_message(
                    self.log_display, f"Received from {username}: {data}"
                )
                self.broadcast_message(f"{username}: {data}", conn)
            except Exception as e:
                self.logger.log_message(self.log_display, f"An error occurred: {e}")
                break

        self.logger.log_message(self.log_display, f"Connection closed by {addr}")
        del self.clients[conn]
        conn.close()

    def request_username(self, conn):
        conn.sendall("Enter your username:".encode("utf-8"))
        username = conn.recv(1024).decode("utf-8")
        return username

    def broadcast_message(self, message, sender_conn):
        for client in self.clients.keys():
            if client != sender_conn:
                try:
                    client.sendall(message.encode("utf-8"))
                except Exception as e:
                    self.logger.log_message(
                        self.log_display, f"Could not send message: {e}"
                    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = ServerApp()
    server.show()
    sys.exit(app.exec_())
