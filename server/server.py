import socket
import threading

OFFSHORE_HOST = "0.0.0.0"
OFFSHORE_PORT = 9999
BUFFER_SIZE = 8192

def tunnel(sock1, sock2):
    """Bidirectional copy between sock1 and sock2"""
    try:
        while True:
            data = sock1.recv(BUFFER_SIZE)
            if not data:
                break
            sock2.sendall(data)
    except:
        pass
    finally:
        sock1.close()
        sock2.close()

def handle_ship(ship_sock, addr):
    try:

        target = ship_sock.recv(BUFFER_SIZE).decode().strip()
        if ":" not in target:
            print("[OFFSHORE] Invalid request from ship")
            ship_sock.close()
            return

        host, port = target.split(":")
        port = int(port)

        print(f"[OFFSHORE] Ship requested {host}:{port}")

        
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect((host, port))

        ship_sock.sendall(b"OK\n")

        threading.Thread(target=tunnel, args=(ship_sock, remote_sock), daemon=True).start()
        threading.Thread(target=tunnel, args=(remote_sock, ship_sock), daemon=True).start()

    except Exception as e:
        print("[OFFSHORE] Error:", e)
        ship_sock.close()

def start_offshore():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((OFFSHORE_HOST, OFFSHORE_PORT))
    server_sock.listen(100)
    print(f"[*] Offshore Server listening on {OFFSHORE_HOST}:{OFFSHORE_PORT}")

    while True:
        ship_sock, addr = server_sock.accept()
        threading.Thread(target=handle_ship, args=(ship_sock, addr), daemon=True).start()

if __name__ == "__main__":
    start_offshore()
