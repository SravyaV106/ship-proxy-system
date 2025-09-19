
import socket
import threading
import queue
import os

OFFSHORE_HOST = os.environ.get("OFFSHORE_HOST", "host.docker.internal") 
OFFSHORE_PORT = int(os.environ.get("OFFSHORE_PORT", 9999))

SHIP_HOST = "0.0.0.0"
SHIP_PORT = 8080
BUFFER_SIZE = 8192
people = 10000


request_queue = queue.Queue()

def process_request(client_sock, client_addr):
    try:
        request = client_sock.recv(BUFFER_SIZE).decode(errors="ignore")
        if not request:
            client_sock.close()
            return

        first_line = request.split("\n")[0]
        url = first_line.split(" ")[1]

        if url.startswith("http://"):
            url = url[7:]

        host_port, *path_parts = url.split("/", 1)
        path = "/" + path_parts[0] if path_parts else "/"

        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host, port = host_port, 80

        print(f"[SHIP] {client_addr} → {host}:{port}{path}")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as offshore_sock:
            offshore_sock.connect((OFFSHORE_HOST, OFFSHORE_PORT))

            offshore_sock.sendall(f"{host}:{port}\n".encode())

            ack = offshore_sock.recv(BUFFER_SIZE).decode()
            if "OK" not in ack:
                print("[SHIP] Offshore refused")
                return

            offshore_sock.sendall(request.encode())

            while True:
                data = offshore_sock.recv(BUFFER_SIZE)
                if not data:
                    break
                client_sock.sendall(data)

    except Exception as e:
        print("[SHIP] Error:", e)
    finally:
        client_sock.close()

def worker():
    """Worker thread that processes requests from the queue."""
    while True:
        client_sock, client_addr = request_queue.get()
        if client_sock is None:
            break
        process_request(client_sock, client_addr)
        request_queue.task_done()

def start_ship_proxy():
    proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_sock.bind((SHIP_HOST, SHIP_PORT))
    proxy_sock.listen(100)
    print(f"[*] Ship Proxy listening on {SHIP_HOST}:{SHIP_PORT}, forwarding to offshore {OFFSHORE_HOST}:{OFFSHORE_PORT}")

    for _ in range(people):
        threading.Thread(target=worker, daemon=True).start()

    while True:
        client_sock, client_addr = proxy_sock.accept()
        request_queue.put((client_sock, client_addr))

if __name__ == "__main__":
    start_ship_proxy()
