import socket
import sys
import select
import os
import time

# files on the server side
SERVER_FILES = "server_files"
METADATA_FILE = os.path.join(
    SERVER_FILES, "metadata.txt"
)  # text file to store metadata

try:
    hostname = ""  # Hostname (can be '' or 'localhost' for local machine)
    port = int(sys.argv[1])  # Port number
except:
    print("Usage: python filename.py port")
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

# maintaining a socket list and clients
sockets_list = [server_socket]
clients = {}  # Dictionary to map sockets to usernames

# Ensure server_files directory exists
if not os.path.exists(SERVER_FILES):
    os.makedirs(SERVER_FILES)
    print(f"Created directory: {SERVER_FILES}")

# Ensure metadata.txt exists or create it with a header if not
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as meta_file:
        meta_file.write("username,filename,size_MB,timestamp\n")
    print(f"Created metadata file: {METADATA_FILE}")

try:
    # main loop with the select statement
    while True:

        # select the socket from the readable sockets using a select statement, handles multiple clients
        readable_sockets, writable_sockets, exceptional_sockets = select.select(
            sockets_list, [], []
        )

        # for each socket in the readable_sockets list check the following conditions
        for r in readable_sockets:

            if r == server_socket:  # if r is a server socket establish a new connection
                connection_socket, client_address = server_socket.accept()
                print(f"New Client Connected: {client_address}")
                # add new client to the sockets_list
                sockets_list.append(connection_socket)

            else:  # handle client messages
                try:
                    message = r.recv(1024).decode("utf-8").strip()

                    # empty message
                    if not message:  # Client disconnected
                        print(f"Client {r.getpeername()} disconnected")
                        sockets_list.remove(r)
                        r.close()
                        continue  # Skip further processing for this socket

                    # handle client authentication
                    if r not in clients:

                        # If login command received
                        if message.startswith("LOGIN "):
                            username = message.split(" ", 1)[1]
                            clients[r] = username
                            response = "LOGIN SUCCESSFUL\n"
                            # Send response to client
                            r.sendall(response.encode("utf-8"))

                        else:  # Invalid user since there is no login command sent from client
                            r.sendall("INVALID USER\n".encode("utf-8"))
                            sockets_list.remove(r)
                            r.close()

                    else:  # If user is already authenticated, now im handling further commands
                        username = clients[r]

                        print(f"Command from {username}: {message}")

                        # ******Handle PUSH Command**********
                        if message.upper().startswith("PUSH "):
                            try:
                                _, filename = message.split(" ", 1)
                                file_location = os.path.join(SERVER_FILES, filename)

                                with open(file_location, "wb") as file_received:
                                    while True:
                                        data = r.recv(4096)
                                        if not data:
                                            break  # Stop if client disconnects

                                        # Check if EOF is reached
                                        if data.endswith(b"EOF\n"):
                                            file_received.write(
                                                data[:-4]
                                            )  # Remove EOF marker
                                            break
                                        else:
                                            file_received.write(data)

                                #
                                file_received.close()

                                #  Calculate file size in bytes
                                file_size = os.path.getsize(file_location)

                                print(f"{file_size}")

                                #  Get timestamp
                                timestamp = time.strftime(
                                    "%Y-%m-%d %H:%M:%S", time.localtime()
                                )
                                print(f"{timestamp}")

                                #  Store metadata in the metadata file
                                with open(METADATA_FILE, "a") as meta_file:
                                    meta_file.write(
                                        f"{clients[r]},{filename},{file_size},{timestamp}\n"
                                    )
                                    meta_file.close()

                                print(f"File '{filename}' uploaded successfully.")
                                r.sendall(
                                    f"File '{filename}' uploaded successfully.\n".encode(
                                        "utf-8"
                                    )
                                )

                            except Exception as e:
                                print(f"Error receiving file: {e}")
                                r.sendall(
                                    f"Error receiving file: {e}\n".encode("utf-8")
                                )

                        else:
                            r.sendall(f"Unknown command: {message}\n".encode("utf-8"))

                except Exception as e:
                    print(f"Error with client: {e}")
                    if r in clients:
                        del clients[r]
                    sockets_list.remove(r)
                    r.close()

except KeyboardInterrupt:
    print("\nServer Sutting")
    for sock in sockets_list:
        sock.close()
        server_socket.close()
        sys.exit(0)
