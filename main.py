import socket
import threading

port = 8888
proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_server.bind(("127.0.0.1", port))
proxy_server.listen(10)

print(f"Proxy server listening on port {port}")


def extract_host_port_from_request(request):
    host_string_start = request.find(b"Host: ") + len(b"Host: ")
    host_string_end = request.find(b"\r\n", host_string_start)
    host_string = request[host_string_start:host_string_end].decode("utf-8")
    webserver_position = host_string.find("/")

    if webserver_position == -1:
        webserver_position = len(host_string)

    port_position = host_string.find(":")

    if port_position == -1 or webserver_position < port_position:
        port = 80
        host = host_string[:webserver_position]
    else:
        port = int(
            (host_string[(port_position + 1) :])[
                : webserver_position - port_position - 1
            ]
        )
        host = host_string[:port_position]

    return host, port


def handle_client_request(client_socket):
    print("Received request")
    request = b""
    client_socket.setblocking(False)

    while True:
        try:
            data = client_socket.recv(1024)
            request = request + data
        except Exception:
            break

    host, port = extract_host_port_from_request(request)
    destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destination_socket.connect((host, port))
    destination_socket.sendall(request)

    while True:
        data = destination_socket.recv(1024)
        if len(data) > 0:
            client_socket.sendall(data)
        else:
            break

    destination_socket.close()
    client_socket.close()


while True:
    client_socket, addr = proxy_server.accept()
    print(f"Accept connection from {addr[0]}:{addr[1]}")

    client_handler = threading.Thread(
        target=handle_client_request, args=(client_socket,)
    )

    client_handler.start()
