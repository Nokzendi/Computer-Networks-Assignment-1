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
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            print(f'\nConnected to {HOST}:{PORT}')
            print('''Type message, enter to send, 'q' to quit''')
            msg = input()
            msg_list = msg.split()
            command = msg_list[0]

            if msg == 'q':
                break

            # Getting our encryption method
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
                to_send_msg = my_encode(msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)

                # Getting our filename
                filename = msg_list[1]
                for i in range(2, len(msg_list)):
                    filename = filename + " " + msg_list[i]

                # Receiving our file
                with open(filename, "w") as f:
                    while True:
                        bytes_read = sock.recv(BUFFER_SIZE).decode()
                        bytes_read = my_decode(bytes_read, encrypt_mode)
                        if not bytes_read:
                            f.close()
                            break
                        f.write(bytes_read)
                        if len(bytes_read) < BUFFER_SIZE:
                            f.close()
                            break
                msg = myFunctions.recv_msg(sock)
                msg = my_decode(msg, encrypt_mode)
                print(msg)

            elif command == "UPD":
                # Sending our upload request/command
                to_send_msg = my_encode(msg, encrypt_mode)
                myFunctions.send_msg(sock, to_send_msg)

                # Getting our filename and sending the file name
                filename = msg_list[1]
                for i in range(2, len(msg_list)):
                    filename = filename + " " + msg_list[i]

                to_send_filename = my_encode(filename, encrypt_mode)
                myFunctions.send_msg(sock, to_send_filename)

                # Sending our file by reading chunks from the files in binary
                with open(filename, "r") as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            f.close()
                            # File transmission has been done
                            break
                        # We use sendall to assure tranmissisons in busy networks
                        bytes_read = my_encode(bytes_read, encrypt_mode)
                        bytes_read = bytes(bytes_read, 'utf-8')
                        sock.sendall(bytes_read)
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
