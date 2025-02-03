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

                        # ******Handle PUSH Command******

                        if message.upper().startswith("PUSH "):
                            try:
                                _, filename = message.split(" ", 1)
                                file_location = os.path.join(SERVER_FILES, filename)
                                user = clients[
                                    r
                                ]  # Get the username of the current client

                                # Read existing metadata
                                existing_metadata = []
                                file_owner = None

                                with open(METADATA_FILE, "r") as meta_file:
                                    for line in meta_file:
                                        metadata_parts = line.strip().split(",")
                                        if (
                                            len(metadata_parts) >= 2
                                            and metadata_parts[1] == filename
                                        ):
                                            file_owner = metadata_parts[
                                                0
                                            ]  # Extract owner of this file
                                        existing_metadata.append(line.strip())

                                # Check if the file exists on the server
                                if os.path.exists(file_location):
                                    if file_owner and file_owner != user:
                                        # If the file exists but is owned by another user, reject the upload
                                        r.sendall(
                                            f"Error: File '{filename}' is owned by {file_owner} and cannot be overwritten.\n".encode(
                                                "utf-8"
                                            )
                                        )
                                    else:
                                        # If the same user is uploading, allow overwrite
                                        print(
                                            f"User '{user}' is overwriting '{filename}'..."
                                        )

                                        # Send READY response to client to indicate that file can be uploaded
                                        r.sendall("READY\n".encode("utf-8"))

                                        # Overwrite the file
                                        with open(file_location, "wb") as file_received:
                                            while True:
                                                data = r.recv(4096)
                                                if not data:
                                                    break  # Stop if client disconnects

                                                # Check if EOF is reached
                                                if data.endswith(b"EOF\n"):
                                                    file_received.write(
                                                        data[:-4]
                                                    )  # remove EOF comment from the binary
                                                    break
                                                else:
                                                    file_received.write(data)

                                        # Calculate file size in bytes
                                        file_size = os.path.getsize(file_location)

                                        # Get timestamp
                                        timestamp = time.strftime(
                                            "%Y-%m-%d %H:%M:%S", time.localtime()
                                        )

                                        # Update the metadata file by replacing the old entry
                                        with open(METADATA_FILE, "w") as meta_file:
                                            for entry in existing_metadata:
                                                # Keep all entries except the old metadata for this user & file
                                                if entry.startswith(
                                                    f"{user},{filename},"
                                                ):
                                                    continue
                                                meta_file.write(entry + "\n")

                                            # Append the new metadata with updated timestamp and file size
                                            meta_file.write(
                                                f"{user},{filename},{file_size},{timestamp}\n"
                                            )

                                        print(
                                            f"File '{filename}' overwritten successfully by {user}."
                                        )
                                        r.sendall(
                                            f"File '{filename}' overwritten successfully.\n".encode(
                                                "utf-8"
                                            )
                                        )

                                else:

                                    # If the file does not exist, allow normal upload
                                    r.sendall("READY\n".encode("utf-8"))

                                    # If the file does not exist, allow normal upload
                                    with open(file_location, "wb") as file_received:
                                        while True:
                                            data = r.recv(4096)
                                            if not data:
                                                break  # Stop if client disconnects

                                            # Check if EOF is reached
                                            if data.endswith(b"EOF\n"):
                                                file_received.write(
                                                    data[:-4]
                                                )  # remove EOF comment from the binary
                                                break
                                            else:
                                                file_received.write(data)

                                    # Calculate file size in bytes
                                    file_size = os.path.getsize(file_location)

                                    # Get timestamp
                                    timestamp = time.strftime(
                                        "%Y-%m-%d %H:%M:%S", time.localtime()
                                    )

                                    # Store metadata in the metadata file
                                    with open(METADATA_FILE, "a") as meta_file:
                                        meta_file.write(
                                            f"{user},{filename},{file_size},{timestamp}\n"
                                        )

                                    print(
                                        f"File '{filename}' uploaded successfully by {user}."
                                    )
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

                        elif message.upper().startswith("GET "):
                            try:
                                _, filename = message.split(" ", 1)
                                file_location = os.path.join(
                                    SERVER_FILES, filename
                                )  # Get the file path where the file is located

                                # If the file exists, send it in chunks through the connection socket
                                if os.path.exists(file_location):
                                    with open(file_location, "rb") as file_sent:
                                        while data := file_sent.read(4096):
                                            r.sendall(
                                                data
                                            )  # Send each chunk of the file to the client

                                    # Notify the client that the file transfer is complete
                                    r.sendall(b"EOF\n")
                                    print(
                                        f"File '{filename}' sent to {clients[r]} successfully."
                                    )

                                # If the file doesn't exist, send an error message
                                else:
                                    error_message = f"ERROR: File '{filename}' is not available on the server\n"
                                    r.sendall(error_message.encode("utf-8"))

                            except Exception as e:
                                print(f"Error sending file: {e}")

                        elif message.upper() == "LIST":
                            try:
                                with open(METADATA_FILE, "r") as meta_file:
                                    lines = meta_file.readlines()[
                                        1:
                                    ]  # Skip header line

                                if not lines:
                                    r.sendall(
                                        "No files found on the server.\n".encode(
                                            "utf-8"
                                        )
                                    )
                                else:
                                    file_list = "\n".join(
                                        f"{filename}, {size_MB} MB, {timestamp}, uploaded by: {username}"
                                        for username, filename, size_MB, timestamp in (
                                            line.strip().split(",") for line in lines
                                        )
                                    )
                                    r.sendall(f"{file_list}\n".encode("utf-8"))

                            except Exception as e:
                                print(f"Error listing files: {e}")
                                r.sendall(f"Error listing files: {e}\n".encode("utf-8"))

                        elif message.upper().startswith("DELETE "):
                            try:
                                _, filename = message.split(
                                    " ", 1
                                )  # Extract the filename to be deleted
                                file_location = os.path.join(
                                    SERVER_FILES, filename
                                )  # Get the full path to the file

                                # Check if the file exists
                                if os.path.exists(file_location):
                                    # Read the metadata file to find the owner of the file
                                    file_owner = None
                                    with open(METADATA_FILE, "r") as meta_file:
                                        for line in meta_file:
                                            metadata_parts = line.strip().split(",")
                                            if (
                                                len(metadata_parts) >= 2
                                                and metadata_parts[1] == filename
                                            ):
                                                file_owner = metadata_parts[
                                                    0
                                                ]  # Extract the file owner
                                                break

                                    # If the owner was found, check if the logged-in user is the owner
                                    if file_owner:
                                        user = clients[
                                            r
                                        ]  # Get the logged-in user (from the clients dictionary)
                                        if user == file_owner:
                                            # Only allow deletion if the user is the owner
                                            os.remove(file_location)  # Delete the file
                                            success_message = f"File '{filename}' deleted successfully\n"
                                            r.sendall(
                                                success_message.encode("utf-8")
                                            )  # Send success message to client
                                            print(
                                                f"File '{filename}' deleted successfully by {user}."
                                            )

                                            # Optionally, remove the file's metadata from the METADATA_FILE
                                            # Update the metadata file to remove the entry for the deleted file
                                            with open(METADATA_FILE, "r") as meta_file:
                                                metadata_lines = meta_file.readlines()

                                            with open(METADATA_FILE, "w") as meta_file:
                                                for line in metadata_lines:
                                                    if not line.startswith(
                                                        f"{file_owner},{filename},"
                                                    ):
                                                        meta_file.write(
                                                            line
                                                        )  # Keep other metadata entries

                                        else:
                                            error_message = f"ERROR: You are not the owner of the file '{filename}'.\n"
                                            r.sendall(
                                                error_message.encode("utf-8")
                                            )  # Send error message if not the owner
                                            print(
                                                f"User '{user}' tried to delete a file they don't own."
                                            )

                                    else:
                                        error_message = f"ERROR: Owner of file '{filename}' not found.\n"
                                        r.sendall(
                                            error_message.encode("utf-8")
                                        )  # Send error message if owner not found

                                else:
                                    error_message = f"ERROR: File '{filename}' not found on the server\n"
                                    r.sendall(
                                        error_message.encode("utf-8")
                                    )  # Send error message if file not found

                            except Exception as e:
                                print(f"Error deleting file: {e}")

                            else:
                                r.sendall(
                                    f"Unknown command: {message}\n".encode("utf-8")
                                )

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
