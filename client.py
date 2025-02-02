import socket
import sys
import os


# get the login credentials from the command line arguments
try:
    username = sys.argv[1]
    hostname = sys.argv[2]
    port = int(sys.argv[3])

except:
    print("Usage: python filename.py username hostname port")
    sys.exit(1)

# Create a client socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
try:
    client_socket.connect((hostname, port))
    print(f"Connected to the {hostname} at port {port}")
except socket.error as e:
    print(f"Error connecting to server: {e}")
    sys.exit(1)

# login authentication
# Send the LOGIN command to the server
client_socket.sendall(f"LOGIN {username}\n".encode("utf-8"))

# Receive the server's response
response = client_socket.recv(1024).decode("utf-8").strip()
print("Server response:", response)

if response.strip() == "LOGIN SUCCESSFUL":
    print("You are now authenticated.")

    # After successful login, you can keep the connection open and interact with the server
    while True:

        # Example: Requesting a list of files or any other command
        user_command = input("Enter command options (e.g., PUSH, LIST, GET, or EXIT): ")

        # ******* Handle push command, parse and send the file and its content ********
        if user_command.upper().startswith("PUSH "):
            try:
                _, filename = user_command.split(" ", 1)  # getting the filename

                # Check if file exists locally
                if not os.path.exists(filename):
                    print(f"File {filename} not found.")
                    continue

                # send the push command
                client_socket.sendall(f"PUSH {filename}\n".encode("utf-8"))

                total_sent = 0  # size of data sent

                # open the file read binary and send the command to the server
                with open(filename, "rb") as file_sent:
                    while data := file_sent.read(4096):
                        client_socket.sendall(data)

                # message for server to know that the whole is transferred
                client_socket.sendall(b"EOF\n")

                print(f"{filename} sent successfully.")

                response = (
                    client_socket.recv(1024).decode("utf-8").strip()
                )  # Get server response
                print(f"Server response: {response}")

            except FileNotFoundError:
                print("file {filename} not found.")
                continue

            except Exception:
                print("Error Try Again.")
                continue

        # ******* Handle GET command ********
        # ******* Handle LIST command ********
        # ******* Handle DELETE command ********

        elif user_command == "EXIT":

            client_socket.sendall("EXIT\n".encode("utf-8"))  # Send exit command

            response = (
                client_socket.recv(1024).decode("utf-8").strip()
            )  # Get server response
            print(f"🔹 Server response: {response}")

            print(" Closing connection...")
            break  # Exit the loop

# Close connection after exiting the loop
client_socket.close()
print(" Connection closed.")
