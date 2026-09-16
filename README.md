⚡ TCP Chat

A lightweight desktop chat application built with Python, TCP sockets, Tkinter, and multithreading.

The application provides a simple dark-themed graphical interface where users can connect to a TCP chat server, choose a nickname, exchange messages in real time, and automatically save chat history locally.

✨ Features

💬 Real-time TCP chat

🖥️ Desktop GUI built with Tkinter

🔌 TCP/IP socket communication

🧵 Background thread for receiving messages

👤 Custom nicknames

🕐 Message timestamps

💾 Persistent local chat history

📜 Automatic loading of previous messages

🌙 Dark-themed interface

⚡ Lightweight with no external Python dependencies

❌ Connection/disconnection status handling

⌨️ Press Enter to send messages

🛠️ Technologies

Python 3

Tkinter — graphical user interface

Socket — TCP network communication

Threading — asynchronous message receiving

Datetime — message timestamps

OS — local log file management

📁 Project Structure
TCPChat/
│
├── client.py          # Tkinter chat client
├── server.py          # TCP chat server
├── README.md          # Project documentation
└── ...


The provided code is the client-side application. A compatible TCP server is required for clients to communicate.

🚀 Getting Started
Prerequisites

Make sure you have Python 3.x installed.

Check your Python version:

python --version


Tkinter is normally included with standard Python installations.

1. Clone the Repository
git clone https://github.com/your-username/TCPChat.git
cd TCPChat

2. Start the Server

Start your TCP chat server first:

python server.py


Make sure the server is listening on the IP address and port you intend to use.

3. Start the Client

In another terminal:

python client.py


The application will open a graphical login screen.

4. Connect

Enter:

Field	Description
Server IP	IP address of the TCP server
Port	TCP port used by the server
Nickname	Your display name

Click Connect to join the chat.

💬 Using the Chat

Once connected:

Type a message into the input field.

Press Enter or click Send.

Messages from other users will appear automatically.

Your messages are displayed on the right side.

Messages from other users appear on the left.

System notifications are displayed separately.



💾 Chat History

The client automatically stores chat logs locally.

On Windows, logs are saved under:

%APPDATA%\TCPChat\


Each nickname gets its own log file:

chat_<nickname>.txt


For example:

%APPDATA%\TCPChat\chat_Alice.txt


When the user reconnects with the same nickname, previous messages are loaded into the chat window.

🌐 Network Architecture

The application uses a traditional client-server TCP architecture:

                    TCP Connection
              ┌──────────────────────┐
              │                      │
              ▼                      ▼
        ┌───────────┐          ┌───────────┐
        │  Client 1 │          │  Client 2 │
        │  Tkinter  │          │  Tkinter  │
        └─────┬─────┘          └─────┬─────┘
              │                      │
              │        TCP           │
              └──────────┬───────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ TCP Server  │
                  │             │
                  │  Broadcast  │
                  │  Messages   │
                  └─────────────┘


The client:

Creates a TCP socket.

Connects to the configured server.

Sends the nickname when requested.

Sends messages to the server.

Continuously receives messages in a background thread.

Updates the Tkinter interface safely using root.after().

🧵 Multithreading

Receiving network messages continuously could block the graphical interface.

To prevent the GUI from freezing, the application creates a daemon thread:

thread = threading.Thread(
    target=self.receive,
    daemon=True
)

thread.start()


The receiving thread waits for incoming TCP messages while the Tkinter main thread continues handling the interface.

GUI updates are scheduled with:

self.root.after(0, ...)


This keeps Tkinter operations on the main GUI thread.

🎨 Interface

The application uses a dark color scheme with cyan accents.

Element	Color
Background	#0d0d0d
Secondary background	#1a1a2e
Accent	#00d4ff
Text	#f0f0f0
User messages	#003344
Other messages	#1a1a2e
System messages	#1e1e1e
🔐 Security Considerations

This project is intended primarily for learning and local/network experimentation.

The current implementation does not provide:

End-to-end encryption

TLS/SSL

User authentication

Password protection

Message integrity verification

Access control

Input/message size limits

Secure server-side persistence

Avoid using the application to transmit sensitive information over untrusted networks.

⚠️ Error Handling

The client handles several common problems:

Missing connection information

Invalid port numbers

Failed server connections

Server disconnections

Failed message transmission

Log-file write errors

For example, an invalid port produces a GUI error instead of attempting a connection.

🔧 Possible Improvements

Future versions could add:

🔐 TLS encryption

🔑 User authentication

🟢 Online/offline user indicators

📎 File transfers

😀 Emoji support

🖼️ Image sharing

🔔 Desktop notifications

🗃️ SQLite-based message storage

🔍 Searchable chat history

🧹 Clear-history functionality

⚙️ Configurable server settings

🧑‍🤝‍🧑 Private messaging

🛡️ Better server-side validation

📦 Standalone executable builds with PyInstaller

🐛 Known Limitations

A compatible TCP server must be running before connecting.

Messages are transmitted without encryption.

The client uses a simple text-based protocol.

Chat history is stored as plain text.

The application currently targets desktop environments supported by Tkinter.

Message timestamps shown for loaded history represent the time they are displayed rather than necessarily the original message time.

🤝 Contributing

Contributions are welcome!
