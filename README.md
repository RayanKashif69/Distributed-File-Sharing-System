# Distributed-File-Sharing-System


## **Part 1: Running the TreeDrive System**
TreeDrive is a stateful file-sharing system that allows clients to authenticate, upload, download, list, and delete files in a shared environment.

- I have implemented the bonus question for cd and ls commands
- server files uploads will be located in the directory /server_files
- /server_files includes the metadata.txt file as well

## Assigned Port Number: 8115-8119

### **How to Run the Server**
1. Open a terminal and navigate to the server directory.
2. Port number is hard coded and hostname is set as empty string to pick the best avaiable interface
3. Run the following command:
  
      ```
      python server.py
      ```

---

### **How to Run the Client**
-  Port number is hard coded in the client code
-  Hostname will be displayed on the terminal as you run the server, its the name of the machine where the server is hosted
-  Enter any Username
-  Run the following command

      ```
      python client.py <username> <hostname>
      ```
  
--- 

### **File Operations & Additional Notes**
All file operations in TreeDrive have been implemented correctly, ensuring proper file handling and access control.

#### **Pushing (Uploading) a File**
- Users can upload files using the `PUSH` command.
- If a user uploads a file **for the first time**, it is stored on the server.
- If the **same user** attempts to push a file with the **same name**, the existing file will be **overwritten**.
- However, if a **different user** tries to push a file that **already exists on the server** (owned by another user), the operation will be **denied** with a proper error message.

### Grader Notes
- As soon as the client connects to the server, the system automatically sends a login command.
- The server responds with a LOGIN SUCCESSFUL message if authentication is successful.
- If login fails, the server will return an INVALID USER message.
- Once the login is successful, the client must enter commands in the command-line interface. Please ensure commands are typed exactly as provided. Though error checking is implemented on the server side




