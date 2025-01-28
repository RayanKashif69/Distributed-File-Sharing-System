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
    print("Connected to the {hostname} at port {port}")
except socket.error as e:
    print(f"Error connecting to server: {e}")
    sys.exit(1)

#login authentication
client_socket.sendall(f"LOGIN {username}".encode())

                       # Send the LOGIN command to the server
client_socket.sendall(f"LOGIN {username}\n".encode('utf-8'))

# Receive the server's response
response = client_socket.recv(1024).decode('utf-8').strip()
print("Server response:", response)

if response == "LOGIN SUCCESS":
    print("You are now authenticated.")

# Close the client socket after receiving response
client_socket.close()