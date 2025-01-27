import socket
import sys
import select

try:
    hostname = '' # Hostname (can be '' or 'localhost' for local machine)
    port = int(sys.argv[1])  # Port number
except:
    print("Usage: python filename.py hostname port")
    sys.exit(1)

# Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to the provided hostname and port
try:
    server_socket.bind((hostname, port))
    print(f"Server is listening on {hostname}:{port}")
except socket.error as e:
    print(f"Error binding to port {port}: {e}")
    sys.exit(1)

server_socket.listen()

while True:
    conn, ip = server_socket.accept()

    print(f"client connected : {ip}")

    



