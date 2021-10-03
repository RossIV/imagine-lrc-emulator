import socket
import re

src_list = [
    'Source 1', 'Source 2', 'Source 3', 'Source 4', 'Source 5', 'Source 6',
    'Source 7', 'Source 8', 'Source 9', 'Source 10', 'Source 11', 'Source 12',
    'Source 13', 'Source 14', 'Source 15', 'Source 16', 'Source 17', 'Source 18',
]
dst_list = [
    'Dest 1', 'Dest 2', 'Dest 3', 'Dest 4', 'Dest 5', 'Dest 6',
    'Dest 7', 'Dest 8', 'Dest 9', 'Dest 10', 'Dest 11', 'Dest 12',
    'Dest 13', 'Dest 14', 'Dest 15', 'Dest 16', 'Dest 17', 'Dest 18',
]
salvo_list = [
    'Salvo 1', 'Salvo 2', 'Salvo 3', 'Salvo 4', 'Salvo 5', 'Salvo 6'
]
msg_q_src_count = "~SRC?Q${COUNT}\\"
msg_q_src_count_resp = "~SRC%COUNT#{{{COUNT}}}\\".format(COUNT=len(src_list))
msg_q_src_name = "~SRC?Q${NAME}\\"
msg_q_dst_count = "~DEST?Q${COUNT}\\"
msg_q_dst_count_resp = "~DEST%COUNT#{{{COUNT}}}\\".format(COUNT=len(dst_list))
msg_q_dst_name = "~DEST?Q${NAME}\\"
msg_q_salvo_name_regex = r"~XSALVO\?ID#{(\d+)}\\"
msg_q_protocol_name = "~PROTOCOL?Q${NAME}\\"
msg_q_protocol_version = "~PROTOCOL?Q${VERSION}\\"


def handle_message(message):
    print('Handling {}'.format(message))
    # Source Count
    if message == msg_q_src_count:
        return msg_q_src_count_resp
    # Source Names
    elif message == msg_q_src_name:
        formatted_srcs = []
        for key, value in enumerate(src_list):
            formatted_srcs.append("~SRC%I#{{{}}};NAME${{{}}}\\".format(key+1, value))
        return formatted_srcs
    # Destination Count
    elif message == msg_q_dst_count:
        return msg_q_dst_count_resp
    # Destination Names
    elif message == msg_q_dst_name:
        formatted_dests = []
        for key, value in enumerate(dst_list):
            formatted_dests.append("~DEST%I#{{{}}};NAME${{{}}}\\".format(key+1, value))
        return formatted_dests
    # Salvo Names
    elif re.search(msg_q_salvo_name_regex, message) is not None:
        result = re.search(msg_q_salvo_name_regex, message)
        salvo_id = result.group(1)
        try:
            salvo_name = salvo_list[int(salvo_id)-1]
            return "~XSALVO%ID#{{{}}};NAME${{{}}}\\".format(salvo_id, salvo_name)
        except IndexError as e:
            return
    elif message == msg_q_protocol_name:
        return 'Logical Router Control Protocol'
    elif message == msg_q_protocol_version:
        return '1.1'
    else:
        return


def main():
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Ensure that you can restart your server quickly when it terminates
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the client socket's TCP "well-known port" number
    well_known_port = 52116
    sock.bind(('', well_known_port))

    # Set the number of clients waiting for connection that can be queued
    sock.listen(5)

    # loop waiting for connections (terminate with Ctrl-C)
    try:
        while 1:
            newSocket, address = sock.accept()
            print("Connected from", address)
            # loop serving the new client
            while 1:
                receivedData = newSocket.recv(1024)
                if not receivedData: break
                # print('Received: {}'.format(receivedData))

                receivedDataSplit = receivedData.split(b'~')
                for data in receivedDataSplit:
                    resp = handle_message("~{}".format(data.decode('UTF-8')))
                    if isinstance(resp, list):
                        for item in resp:
                            newSocket.send(item.encode())
                            print('Sent: {}'.format(item))
                    elif resp is None:
                        print('Sent nothing')
                    else:
                        print('Sent: {}'.format(resp))
                        newSocket.send(resp.encode())
            newSocket.close()
            print("Disconnected from", address)
    finally:
        sock.close()


if __name__ == '__main__':
    main()