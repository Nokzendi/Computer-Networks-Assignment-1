import myFunctions
import os
from encryption import my_decode
from encryption import my_encode

HOST = myFunctions.HOST
PORT = myFunctions.PORT
BUFFER_SIZE = 1024


def handle_client(sock, addr):
    # """ Receive data from the client via sock and echo it back """
    try:
        # Receives the encryption mode
        encrypt_mode = myFunctions.recv_msg(sock)

        # Blocks until it receives complete message
        msg = myFunctions.recv_msg(sock)
        msg = my_decode(msg, encrypt_mode)
        print(f'{addr}: {msg}')

        # IMPLEMENTING THE COMMANDS REQUIRED
        msg_list = msg.split()
        command = msg_list[0]
        if(command == "CWD"):
            to_send_msg = my_encode(os.getcwd(), encrypt_mode)
            myFunctions.send_msg(sock, to_send_msg)

        elif(command == "LS"):
            to_send_msg = str(os.listdir())
            to_send_msg = my_encode(to_send_msg, encrypt_mode)
            myFunctions.send_msg(sock, to_send_msg)

        elif(command == "CD"):
            # Getting the name of the folder/file after CD command
            # NOTE: Names might contain spaces within themselves, so we run a loop to concatenate all other
            # strings in msg_list
            path = msg_list[1]
            for i in range(2, len(msg_list)):
                path = path + " " + msg_list[i]

            # Checking if the input directory is a valid directory
            # We run a separate check for ".." as it is a valid command to back one level from our current directory
            dir_list = os.listdir()
            if path in dir_list:
                os.chdir(path)
                to_send_msg = f"Directory Changed. Current Directory - {os.getcwd()}"
                to_send_msg = my_encode(to_send_msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)
            elif path == '..':
                os.chdir('..')
                to_send_msg = f"Directory Changed. Current Directory - {os.getcwd()}"
                to_send_msg = my_encode(to_send_msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)
            else:
                to_send_msg = "[ERROR] No such directory exists"
                to_send_msg = my_encode(to_send_msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)

        elif(command == "DWD"):
            # Getting our filename requested by our client
            filename = msg_list[1]
            for i in range(2, len(msg_list)):
                filename = filename + " " + msg_list[i]

            # Reading the file and send it in bytes of BUFFER_SIZE
            with open(filename, "r") as f:
                while True:
                    # Reads the file data in strings BUFFER_SIZE at a time
                    bytes_read = f.read(BUFFER_SIZE)
                    # If no data is read, transfer is complete
                    if not bytes_read:
                        f.close()
                        break
                    # Since our bytes_read is a string, we encrypt it using our encryption algorithm 
                    # We then encode it using 'utf-8' to send it over the network
                    bytes_read = my_encode(bytes_read, encrypt_mode)
                    bytes_read = bytes(bytes_read, 'utf-8')
                    sock.sendall(bytes_read)

            # Sending the downnload status to the client when it finishes.
            msg = "Download Completed"
            msg = my_encode(msg, encrypt_mode)
            myFunctions.send_msg(sock, msg)

        elif(command == "UPD"):
            # Getting our filename and removing any absolute path sent by the client
            filename = myFunctions.recv_msg(sock)
            filename = my_decode(filename, encrypt_mode)
            # filename = os.path.basename(filename)

            # Receiving our file
            with open(filename, "w") as f:
                while True:
                    # Once we receive our data, we first decode the 'utf-8' layer
                    # Then we decrypt according to the encrytion types chosen by the client.
                    bytes_read = sock.recv(BUFFER_SIZE).decode()
                    bytes_read = my_decode(bytes_read, encrypt_mode)
                    if not bytes_read:
                        f.close()
                        # Nothing received. File transmission done
                        break
                    f.write(bytes_read)
                    # Checking the file size received from the connection. 
                    # NOTE: I could have merged the two "if" conditions into one using a logical OR operator
                    # Not done here only because the Design document is already made with this structure
                    if len(bytes_read) < BUFFER_SIZE:
                        f.close()
                        break
            
            # Sending the upload status to the client after it finishes.
            msg = "Upload Completed"
            msg = my_encode(msg, encrypt_mode)
            myFunctions.send_msg(sock, msg)
        else:
            # Server sends back the same message it received from the client
            to_send_msg = my_encode(msg, encrypt_mode)
            myFunctions.send_msg(sock, to_send_msg)
    except (ConnectionError, BrokenPipeError):
        print('Socket error')
    finally:
        # If nothing comes from the client it closes the connection
        print(f'Closed connection to {addr}')
        sock.close()


if __name__ == '__main__':
    # Creating a socket to make our connection with
    listen_sock = myFunctions.create_listen_socket(HOST, PORT)

    addr = listen_sock.getsockname()
    print('Listening on {}'.format(addr))
    while True:
        # Waiting for a client to make a connection
        client_sock, addr = listen_sock.accept()

        print(f'Connection from {addr}')
        handle_client(client_sock, addr)
