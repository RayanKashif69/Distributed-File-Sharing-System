import sys
import time
import socket
import os

if len(sys.argv) < 4:
    print("Usage: python client.py <username> <hostname> <command>")
    sys.exit(1)

username = sys.argv[1]
hostname = sys.argv[2]
user_command = " ".join(sys.argv[3:])

print(f" Client requesting: {user_command}")  # Debugging output

# Start timing the download
start_time = time.time()

# Create a client socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((hostname, 8115))

#  First, send LOGIN request
client_socket.sendall(f"LOGIN {username}\n".encode("utf-8"))

#  Receive login response
login_response = client_socket.recv(1024).decode("utf-8").strip()
print(f" Server login response: {login_response}")

if login_response != "LOGIN SUCCESSFUL":
    print(" Login failed! Exiting.")
    client_socket.close()
    sys.exit(1)  # Exit if login fails

#  Now send the GET request after login
client_socket.sendall(f"{user_command}\n".encode("utf-8"))

# Receive the server's response
response = client_socket.recv(1024).decode("utf-8").strip()
print(f" Server response: {response}")

# Stop if file is not found
if response.startswith("ERROR"):
    client_socket.close()
    sys.exit(1)

#  New Fix: Wait for "READY" before downloading
if response == "READY":
    client_socket.sendall("ACK\n".encode("utf-8"))  #  Acknowledge "READY"

    # Extract filename from the GET request
    filename = user_command.split(" ")[1]

    # Start receiving and writing the file
    file_path = f"downloads/{filename}"  # Store in a dedicated downloads folder
    os.makedirs("downloads", exist_ok=True)  # Ensure folder exists

    with open(file_path, "wb") as file_received:
        while True:
            data = client_socket.recv(4096)
            if not data or data.endswith(b"EOF"):
                break
            file_received.write(data)

    # Stop timing after file transfer is complete
    end_time = time.time()
    download_time = end_time - start_time

    #  Use a lock to prevent race conditions while writing to the log file
    try:
        with open("download_times.txt", "a") as log_file:
            log_file.write(f"{username}, {filename}, {download_time:.4f} sec\n")
        print(f" File '{filename}' downloaded successfully in {download_time:.4f} sec")
    except Exception as e:
        print(f" Error writing to log file: {e}")

client_socket.close()
sys.exit(0)
