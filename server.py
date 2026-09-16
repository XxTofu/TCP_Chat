import socket
import threading
import atexit
import os
from pyngrok import ngrok
from dotenv import load_dotenv

load_dotenv()

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # fix port already in use
server.bind((HOST, PORT))
server.listen()

clients = {}
lock = threading.Lock()

atexit.register(server.close)
atexit.register(ngrok.kill)


def broadcast(message):
    with lock:
        for client in list(clients):
            try:
                client.send(message)
            except Exception as e:
                print(f"Send error: {e}")
                clients.pop(client, None)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise Exception("Disconnected")
            broadcast(message)
        except Exception as e:
            print(f"Client error: {e}")
            with lock:
                nickname = clients.pop(client, None)
            if nickname:
                broadcast(f"{nickname} left the chat.".encode())
            client.close()
            break


def receive():
    ngrok.set_auth_token(os.getenv("token")) #ngrok auth token do not change this line or share it with anyone

    try:
        tunnel = ngrok.connect(PORT, "tcp")
        try:
            public_url = tunnel.public_url
        except AttributeError:
            public_url = tunnel.url()
    except Exception as e:
        print(f"ngrok error: {e}")
        public_url = f"tcp://{HOST}:{PORT} (ngrok failed)"

    parts = public_url.replace('tcp://', '').split(':')
    public_host = parts[0]
    public_port = parts[1]

    print(f"Server running on {HOST}:{PORT}")
    print(f"Public URL: {public_url}")
    print(f"Share with clients -> host: {public_host}  port: {public_port}")

    while True:
        client, address = server.accept()
        print(f"Connected with {address}")

        try:
            client.send("NICK".encode())
            nickname = client.recv(1024).decode().strip()

            if not nickname:
                client.close()
                continue

            with lock:
                clients[client] = nickname

            print(f"Nickname: {nickname}")
            client.send("Connected to the server.".encode())  # confirm to client first
            broadcast(f"{nickname} joined the chat!".encode())  # then tell everyone

            thread = threading.Thread(target=handle, args=(client,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"Handshake error: {e}")
            client.close()

receive()