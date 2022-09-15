import sys
import socket
from encryption import my_decode
from encryption import my_encode
import myFunctions

HOST = sys.argv[-1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = myFunctions.PORT
BUFFER_SIZE = 1024

if __name__ == '__main__':
    while True:
        try:
            # Creating our socket and connecting to the server
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            print(f'\nConnected to {HOST}:{PORT}')
            print('''Type message, enter to send, 'q' to quit''')

            # Taking input from the user
            msg = input()
            msg_list = msg.split()
            command = msg_list[0]

            if msg == 'q':
                break

            # Getting our encryption method input from the user
            print("Choose encryption method: ")
            while True:
                print("1. Plain text(DEFAULT)\n2. Substitute\n3. Reverse")
                encrypt_mode = input()
                if(encrypt_mode != '1' and encrypt_mode != '2' and encrypt_mode != '3'):
                    print("Invalid number. Select again")
                else:
                    break

            # Sending info about the encryption mode wihout any encryption
            myFunctions.send_msg(sock, encrypt_mode)

            if command == "DWD":
                # We first send the entire input message to the server for the server to know which command is being requested
                to_send_msg = my_encode(msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)

                # Getting our filename
                # I ran this for loop because file names can have spaces in between. To handle this case, we concatenate the 
                # words in our split list as only the first word is the command and the remaining is the file name.
                filename = msg_list[1]
                for i in range(2, len(msg_list)):
                    filename = filename + " " + msg_list[i]

                # Receiving our file
                with open(filename, "w") as f:
                    while True:
                        # Once we receive our data, we must first decode the 'utf-8' encoding layer on it. 
                        # We then proceed to decode our encryption layer chosen by the user
                        bytes_read = sock.recv(BUFFER_SIZE).decode()
                        bytes_read = my_decode(bytes_read, encrypt_mode)
                        if not bytes_read:
                            f.close()
                            break
                        f.write(bytes_read)
                        # There were some bugs when breaking this loop only from the condition above. Therefore, according to what
                        # Professor told, I check the data size that we are receiving and break when we receive data less than the bufeer
                        # size. 
                        # NOTE: As mentioned in the echo_server.py file comments, we can merge these two "if" conditions and check as well.
                        if len(bytes_read) < BUFFER_SIZE:
                            f.close()
                            break

                # Waiting for the status of download from the server.
                msg = myFunctions.recv_msg(sock)
                msg = my_decode(msg, encrypt_mode)
                print(msg)

            elif command == "UPD":
                # Sending our upload request/command
                to_send_msg = my_encode(msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)

                # Getting our filename and sending the file name
                # For loop for the same reason stated in the DWD section
                filename = msg_list[1]
                for i in range(2, len(msg_list)):
                    filename = filename + " " + msg_list[i]

                # Here we are sending the filename to the server in order to save some time running the loop. 
                # However, I am not too sure which one works faster. 
                # NOTE: This is only implemented in the UPD section. In the DWD section, both server and client run the for loop
                # to get the filename.
                to_send_filename = my_encode(filename, encrypt_mode)
                myFunctions.send_msg(sock, to_send_filename)

                # Sending our file by reading chunks from the files in binary
                with open(filename, "r") as f:
                    while True:
                        # Reads file data as strings
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            f.close()
                            # File transmission has been done
                            break
                        # We first encrypt the bytes_read data using our encryption algorithm 
                        # We then encode it using 'utf-8' encoding as we need a bytes object in order to send it over the network
                        bytes_read = my_encode(bytes_read, encrypt_mode)
                        bytes_read = bytes(bytes_read, 'utf-8')
                        # We use sendall to assure tranmissisons in busy networks
                        sock.sendall(bytes_read)
                    
                # Waiting for the status of uplaod from the server.
                msg = myFunctions.recv_msg(sock)
                msg = my_decode(msg, encrypt_mode)
                print(msg)

            else:
                # We call the function to send the message that takes as arguments:
                # 1. The socket through which to send the message
                # 2. The message itself
                to_send_msg = my_encode(msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)  # Blocks until sent
                print(f'Sent message: {msg}')

                # Block until it receives complete message
                msg = myFunctions.recv_msg(sock)
                msg = my_decode(msg, encrypt_mode)
                print('Received message: ' + msg)

        except ConnectionError:
            print('Socket error')
            break

        finally:
            sock.close()
            print('Closed connection to server\n')
