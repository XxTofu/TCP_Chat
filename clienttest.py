import socket
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os

HOST = ""
PORT = 0
nickname = ""
client = None
LOG_FILE = ""

BG        = "#0d0d0d"
BG2       = "#1a1a2e"
ACCENT    = "#00d4ff"
TEXT      = "#f0f0f0"
DIM       = "#555555"
YELLOW    = "#f0c040"
MY_BG     = "#003344"
OTHER_BG  = "#1a1a2e"
SYSTEM_BG = "#1e1e1e"

def timestamp():
    return datetime.now().strftime('%H:%M')

def get_log_path(filename):
    appdata = os.getenv('APPDATA')
    folder = os.path.join(appdata, "TCPChat")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, filename)


def log(message):
    if LOG_FILE:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp()}] {message}\n")
        except Exception as e:
            print(f"Log write failed: {e}")


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Chat")
        self.root.configure(bg=BG)
        self.root.geometry("400x700")
        self.root.resizable(True, True)
        self.build_login()

    #  Login Screen 
    def build_login(self):
        self.login_frame = tk.Frame(self.root, bg=BG)
        self.login_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=60)

        tk.Label(self.login_frame, text="⚡ Test Chat", font=("Courier", 22, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(0, 30))

        self.host_var = tk.StringVar()
        self.port_var = tk.StringVar()
        self.nick_var = tk.StringVar()

        for label, var in [("Server IP", self.host_var),
                            ("Port", self.port_var),
                            ("Nickname", self.nick_var)]:
            tk.Label(self.login_frame, text=label, font=("Courier", 10),
                     bg=BG, fg=DIM, anchor="w").pack(fill=tk.X, pady=(8, 2))
            tk.Entry(self.login_frame, textvariable=var,
                     bg=BG2, fg=TEXT, insertbackground=ACCENT,
                     relief=tk.FLAT, font=("Courier", 13), bd=8).pack(fill=tk.X, ipady=6)

        tk.Button(self.login_frame, text="Connect", font=("Courier", 13, "bold"),
                  bg=ACCENT, fg="#000", relief=tk.FLAT, cursor="hand2",
                  command=self.connect).pack(fill=tk.X, pady=(30, 0), ipady=10)

    #  Chat Screen 
    def build_chat(self):
        self.login_frame.destroy()

        header = tk.Frame(self.root, bg=BG2, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="⚡ Test Chat", font=("Courier", 14, "bold"),
                 bg=BG2, fg=ACCENT).pack()
        self.status_label = tk.Label(header, text=f"Connected as {nickname}",
                                      font=("Courier", 9), bg=BG2, fg=DIM)
        self.status_label.pack()

        self.msg_frame = tk.Frame(self.root, bg=BG)
        self.msg_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(self.msg_frame, bg=BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.msg_frame, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        input_frame = tk.Frame(self.root, bg="#111", pady=8, padx=8)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.msg_input = tk.Entry(input_frame, bg=BG2, fg=TEXT,
                                   insertbackground=ACCENT, relief=tk.FLAT,
                                   font=("Courier", 13), bd=8)
        self.msg_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.msg_input.bind("<Return>", lambda e: self.send())
        self.msg_input.focus()

        tk.Button(input_frame, text="Send", font=("Courier", 11, "bold"),
                  bg=ACCENT, fg="#000", relief=tk.FLAT, cursor="hand2",
                  command=self.send).pack(side=tk.RIGHT, padx=(8, 0), ipady=8, ipadx=10)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    #  Load History 
    def load_history(self):
        if not LOG_FILE or not os.path.exists(LOG_FILE):
            return

        self.add_message("── Previous messages ──", "system")

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            if "===" in line or "Session" in line or "Server:" in line:
                continue
            if line.startswith("[") and "]" in line:
                message = line.split("] ", 1)[-1].strip()
                if not message:
                    continue
                is_me     = message.startswith(f"{nickname}: ")
                is_system = ": " not in message
                kind      = "mine" if is_me else "system" if is_system else "other"
                self.add_message_silent(message, kind)

        self.add_message("── Live ──", "system")

    def add_message_silent(self, text, kind="other"):
        frame = tk.Frame(self.inner, bg=BG, pady=3)
        frame.pack(fill=tk.X, padx=6)

        if kind == "system":
            tk.Label(frame, text=f"⚡ {text}",
                     bg=SYSTEM_BG, fg=YELLOW, font=("Courier", 9),
                     padx=10, pady=5, wraplength=340).pack()
        else:
            is_me = kind == "mine"
            bubble_bg = MY_BG if is_me else OTHER_BG
            anchor = "e" if is_me else "w"

            if ": " in text:
                nick, msg = text.split(": ", 1)
            else:
                nick, msg = "", text

            bubble = tk.Frame(frame, bg=bubble_bg, padx=10, pady=6)
            bubble.pack(anchor=anchor)

            if not is_me:
                tk.Label(bubble, text=nick, bg=bubble_bg, fg=ACCENT,
                         font=("Courier", 9, "bold")).pack(anchor="w")

            tk.Label(bubble, text=msg, bg=bubble_bg, fg=TEXT,
                     font=("Courier", 11), wraplength=260,
                     justify=tk.LEFT).pack(anchor="w")

            tk.Label(bubble, text=timestamp(), bg=bubble_bg, fg=DIM,
                     font=("Courier", 8)).pack(anchor="e")

        self.root.after(50, self.scroll_bottom)

    #  Add Message (live, logs to file) 
    def add_message(self, text, kind="other"):
        frame = tk.Frame(self.inner, bg=BG, pady=3)
        frame.pack(fill=tk.X, padx=6)

        if kind == "system":
            tk.Label(frame, text=f"⚡ {text}  {timestamp()}",
                     bg=SYSTEM_BG, fg=YELLOW, font=("Courier", 9),
                     padx=10, pady=5, wraplength=340).pack()
        else:
            is_me = kind == "mine"
            bubble_bg = MY_BG if is_me else OTHER_BG
            anchor = "e" if is_me else "w"

            if ": " in text:
                nick, msg = text.split(": ", 1)
            else:
                nick, msg = "", text

            bubble = tk.Frame(frame, bg=bubble_bg, padx=10, pady=6)
            bubble.pack(anchor=anchor)

            if not is_me:
                tk.Label(bubble, text=nick, bg=bubble_bg, fg=ACCENT,
                         font=("Courier", 9, "bold")).pack(anchor="w")

            tk.Label(bubble, text=msg, bg=bubble_bg, fg=TEXT,
                     font=("Courier", 11), wraplength=260,
                     justify=tk.LEFT).pack(anchor="w")

            tk.Label(bubble, text=timestamp(), bg=bubble_bg, fg=DIM,
                     font=("Courier", 8)).pack(anchor="e")

        self.root.after(50, self.scroll_bottom)
        log(text)

    def scroll_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    #  Connect 
    def connect(self):
        global HOST, PORT, nickname, client, LOG_FILE

        HOST     = self.host_var.get().strip()
        PORT     = self.port_var.get().strip()
        nickname = self.nick_var.get().strip()

        if not HOST or not PORT or not nickname:
            messagebox.showerror("Error", "Fill in all fields.")
            return

        try:
            PORT = int(PORT)
        except:
            messagebox.showerror("Error", "Port must be a number.")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect:\n{e}")
            return

        LOG_FILE = get_log_path(f"chat_{nickname}.txt")
        log(f"{'='*40}")
        log(f"Session started as {nickname}")
        log(f"Server: {HOST}:{PORT}")
        log(f"{'='*40}")

        self.build_chat()
        self.load_history()

        thread = threading.Thread(target=self.receive, daemon=True)
        thread.start()

    #  Receive 
    def receive(self):
        while True:
            try:
                message = client.recv(1024).decode()
                if not message:
                    break

                if message == "NICK":
                    client.send(nickname.encode())
                    continue

                is_me     = message.startswith(f"{nickname}: ")
                is_system = ": " not in message
                kind      = "mine" if is_me else "system" if is_system else "other"
                self.root.after(0, lambda m=message, k=kind: self.add_message(m, k))

            except Exception as e:
                self.root.after(0, lambda: self.add_message("Disconnected from server.", "system"))
                self.root.after(0, lambda: self.status_label.config(text="Disconnected", fg="red"))
                log(f"{'='*40}")
                log("Session ended")
                log(f"{'='*40}")
                break

    #  Send 
    def send(self):
        message = self.msg_input.get().strip()
        if not message:
            return
        full = f"{nickname}: {message}"
        try:
            client.send(full.encode())
            self.msg_input.delete(0, tk.END)
        except:
            self.add_message("Failed to send message.", "system")


root = tk.Tk()
app = ChatApp(root)
root.mainloop()