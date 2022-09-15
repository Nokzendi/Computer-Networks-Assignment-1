def plain_text(msg):
    return msg


def encode_substitute(msg):
    # Predefining the offset as 5
    offset = 5
    encrypted_msg = ""

    # Traversing through the message
    for i in range(len(msg)):
        char = msg[i]

        if(char.isalnum()):
            # Encrypting upper case letters
            if(char.isupper()):
                encrypted_msg += chr((ord(char) - 65 + offset) % 26 + 65)

            # Encrypting lower case letters
            elif(char.islower()):
                encrypted_msg += chr((ord(char) - 97 + offset) % 26 + 97)

            # Encrypting numbers
            else:
                encrypted_msg += chr((ord(char) - 48 + offset) % 10 + 48)
        else:
            encrypted_msg += char

    return encrypted_msg


def decode_substitute(msg):
    # Predefining the offset as 5
    offset = 5
    decrypted_msg = ""

    # Traversing through the message
    for i in range(len(msg)):
        char = msg[i]

        if(char.isalnum()):
            # Decrypting upper case letters
            if(char.isupper()):
                decrypted_msg += chr((ord(char) - 65 - offset) % 26 + 65)

            # Decrypting lower case letters
            elif(char.islower()):
                decrypted_msg += chr((ord(char) - 97 - offset) % 26 + 97)

            # Decrypting numbers
            else:
                decrypted_msg += chr((ord(char) - 48 - offset) % 10 + 48)
        else:
            decrypted_msg += char

    return decrypted_msg


def transpose(msg):
    # Splitting our message into words separated by spaces. Stores it in an array
    msg_words = msg.split()
    reversed_msg = ""

    # Traversing through our words array and reversing every word
    for i in range(len(msg_words)):
        msg_words[i] = msg_words[i][::-1]

    # Concatenating the reversed words to get our full message 
    for i in range(len(msg_words)):
        reversed_msg = reversed_msg + msg_words[i] + " "

    return reversed_msg

# def transpose(msg):
#     # Splitting our message into words separated by spaces. Stores it in an array
#     nomsg = str(msg)
#     msg_words = nomsg.split()

#     for i in (msg_words):
#         strz = ""
#         for j in msg:
#             strz += str(j)
#             if (strz == i):
#                 strz = ""
#                 j[::-1]

#     return msg


def my_encode(msg, mode):
    # msg = str(msg)
    if mode == '2':
        return encode_substitute(msg)
    elif mode == '3':
        return transpose(msg)
    else:
        return plain_text(msg)


def my_decode(msg, mode):
    # msg = str(msg)
    if mode == '2':
        return decode_substitute(msg)
    elif mode == '3':
        return transpose(msg)
    else:
        return plain_text(msg)
