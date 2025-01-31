import socket
import sys
import select

try:
    hostname = '' # Hostname (can be '' or 'localhost' for local machine)
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

try:
 # main loop with the select statement
 while True:

    #select the socket from the readable sockets using a select statement, handles multiple clients
    readable_sockets, writable_sockets, exceptional_sockets = select.select(sockets_list, [], [])

    # for each socket in the readable_sockets list check the following conditions
    for r in readable_sockets:
        
        if r == server_socket: # if r is a server socket establish a new connection
            connection_socket , client_address = server_socket.accept()
            print(f"New Client Connected: {client_address}")
            sockets_list.append(connection_socket) # add new client to the sockets_list
            
        else: #handle client messages
            try:
                message = r.recv(1024).decode('utf-8').strip()
                
                #empty message
                if not message:  # Client disconnected
                    print(f"Client {r.getpeername()} disconnected")
                    sockets_list.remove(r)
                    r.close()
                    continue  # Skip further processing for this socket
                
                #handle client authentication
                if r not in clients:
                        
                      if message.startswith("LOGIN "):  # If login command received
                        username = message.split(" ", 1)[1]
                        clients[r] = username 
                        response = "LOGIN SUCCESSFUL\n"
                        r.sendall(response.encode('utf-8'))  # Send response to client
                        
                      else:#Invalid user since there is no login command sent from client
                            r.sendall("INVALID USER\n".encode('utf-8'))
                            sockets_list.remove(r)
                            r.close()
                                            
                else:  # If user is already authenticated, now im handling further commands
                    username = clients[r]
                    print(f"Command from {username}: {message}")
                    if message == "EXIT":
                        r.sendall("Goodbye!\n".encode('utf-8'))
                        sockets_list.remove(r)
                        r.close()
                    else:
                        r.sendall(f"Unknown command: {message}\n".encode('utf-8'))
            
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
