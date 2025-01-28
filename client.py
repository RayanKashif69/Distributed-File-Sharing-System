import socket
import sys
import select

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
    client_socket.connect((hostname,port))
    print(f"Connected to the {hostname} at port {port}")
except socket.error as e:
    print(f"Error connecting to server: {e}")
    sys.exit(1)

#login authentication
# Send the LOGIN command to the server
client_socket.sendall(f"LOGIN {username}\n".encode('utf-8'))

# Receive the server's response
response = client_socket.recv(1024).decode('utf-8').strip()
print("Server response:", response)

if response.strip() == "LOGIN SUCCESSFUL":
    print("You are now authenticated.")

    # After successful login, you can keep the connection open and interact with the server
    while True:
        # Example: Requesting a list of files or any other command
        command = input("Enter command (e.g., LIST_FILES, UPLOAD, DOWNLOAD, or EXIT): ")

        if command == "EXIT":
            client_socket.sendall("EXIT\n".encode('utf-8'))
            break  # Exit the loop and close the connection
        
        client_socket.sendall(command.encode('utf-8'))

        # Receive the server's response
        response = client_socket.recv(1024).decode('utf-8').strip()
        print(f"Server response: {response}")

# Close the client socket after exiting the loop
client_socket.close()
