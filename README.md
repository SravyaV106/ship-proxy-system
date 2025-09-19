# Ship–Offshore TCP Proxy

This project simulates a **shipboard proxy system** where all client HTTP/TCP requests pass through a **ship proxy** and are then forwarded to an **offshore proxy**.  
This reduces the number of direct TCP connections from the ship to the internet — only the offshore proxy establishes the actual external connections.

---

##  Architecture

[client] -> [ship_proxy(8080)] -> [offshore_proxy(9999)] -> Internet

## Run locally
1. git clone https://github.com/SravyaV106/ship-proxy-system.git
2. run "python server.py", "python client.py" in termial
3. run "curl.exe -x http://localhost:8080 http://httpforever.com/" in powershell on windows

## Run using Docker containers
1. Pull offshore (server) image: 
docker pull sravyavallabhaneni/offshore

2. Run offshore (server) container on port 9999: 
docker run -d --name offshore-server -p 9999:9999 sravyavallabhaneni/offshore

3. Pull ship (client) image: 
docker pull sravyavallabhaneni/ship

4. Run ship (client) container on port 8080: 
docker run -d --name ship-client \
  -p 8080:8080 \
  -e OFFSHORE_HOST=offshore-server \
  sravyavallabhaneni/ship
