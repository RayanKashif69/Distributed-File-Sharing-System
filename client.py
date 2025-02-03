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

                # Receive response from the server about file overwrite policy
                response = client_socket.recv(1024).decode("utf-8").strip()
                if (
                    "Error:" in response
                ):  # Server rejected the upload (e.g., file owned by someone else)
                    print(f"Server response: {response}")
                    continue  # Go back to asking for another command

                # If the file can be overwritten or is new, start sending the file
                if response == "READY":
                    print(f"Sending file '{filename}'...")

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
        if user_command.upper().startswith("GET "):
            try:
                _, filename = user_command.split(" ", 1)  # getting the filename

                # Send GET request to the server
                client_socket.sendall(f"GET {filename}\n".encode("utf-8"))

                # Receive server response for file availability (Error or ready to send file)
                server_response = client_socket.recv(1024).decode("utf-8").strip()

                if server_response.startswith("ERROR: "):
                    print(
                        server_response.strip()
                    )  # Display error message (e.g., file not found)
                    continue  # Reprompt user for another command

                else:
                    # Start receiving file content in binary mode
                    with open(filename, "wb") as file_received:
                        print(f"Receiving file '{filename}'...")

                        while True:
                            data = client_socket.recv(4096)
                            if not data:
                                break  # Stop if no more data (EOF) or disconnected

                            # Handle EOF marker if received
                            if data.endswith(b"EOF\n"):
                                file_received.write(
                                    data[:-4]
                                )  # Remove EOF marker and write to file
                                break
                            else:
                                file_received.write(
                                    data
                                )  # Write the received data to file

                    print(f"File '{filename}' downloaded successfully.")

            except Exception as e:
                print(f"Error downloading file: {e}")

        # ******* Handle LIST command ********
        elif user_command.upper() == "LIST":
            client_socket.sendall(user_command.encode("utf-8"))
            response = client_socket.recv(4096).decode("utf-8")
            print("\nAvailable Files:\n" + response)

        # ******* Handle DELETE command ********
        elif user_command.upper().startswith("DELETE "):
            try:
                _, filename = user_command.split(
                    " ", 1
                )  # Get the filename to be deleted

                # Send DELETE request to the server
                client_socket.sendall(f"DELETE {filename}\n".encode("utf-8"))

                # Receive the server's response
                server_response = client_socket.recv(1024).decode("utf-8").strip()

                print(server_response)  # Print the server's response (success or error)

            except Exception as e:
                print(f"Error deleting file: {e}")

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
