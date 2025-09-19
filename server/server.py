import socket
import threading

OFFSHORE_HOST = "0.0.0.0"
OFFSHORE_PORT = 9999
BUFFER_SIZE = 8192


def tunnel(source, destination):
    try:
        while True:
            data = source.recv(BUFFER_SIZE)
            if not data:
                break
            destination.sendall(data)
    except Exception as e:
        # Suppress normal disconnect errors
        if not isinstance(e, OSError):
            print(f"[OFFSHORE] Tunnel error: {e}")
    finally:
        try:
            source.shutdown(socket.SHUT_RD)
        except:
            pass
        try:
            destination.shutdown(socket.SHUT_WR)
        except:
            pass


def handle_ship(ship_sock, addr):
    try:
        ship_sock.settimeout(10)
        data = ship_sock.recv(BUFFER_SIZE)
        if not data:
            ship_sock.close()
            return

        # Split only on first newline
        parts = data.split(b"\n", 1)
        target_line = parts[0].decode(errors="ignore").strip()
        leftover = parts[1] if len(parts) > 1 else b""

        if ":" not in target_line:
            print(f"[OFFSHORE] Invalid request from {addr}: {target_line}")
            ship_sock.close()
            return

        host, port = target_line.split(":")
        port = int(port)

        print(f"[OFFSHORE] Ship requested {host}:{port}")

        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.settimeout(10)
        remote_sock.connect((host, port))

        # Send ack back to ship
        ship_sock.sendall(b"OK\n")

        # Forward leftover request bytes if they exist
        if leftover:
            remote_sock.sendall(leftover)

        # Start tunnels
        threading.Thread(target=tunnel, args=(ship_sock, remote_sock), daemon=True).start()
        threading.Thread(target=tunnel, args=(remote_sock, ship_sock), daemon=True).start()

    except Exception as e:
        print(f"[OFFSHORE] Error handling {addr}: {e}")
        ship_sock.close()


def start_offshore():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((OFFSHORE_HOST, OFFSHORE_PORT))
    server_sock.listen(100)
    print(f"[*] Offshore Server listening on {OFFSHORE_HOST}:{OFFSHORE_PORT}")

    while True:
        ship_sock, addr = server_sock.accept()
        print(f"[OFFSHORE] Connection from ship {addr}")
        threading.Thread(target=handle_ship, args=(ship_sock, addr), daemon=True).start()


if __name__ == "__main__":
    start_offshore()
