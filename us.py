import socket
import requests
from flask import Flask, request

app = Flask(__name__)


def dns_lookup(hostname, as_ip, as_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    try:
        sock.sendto(f"TYPE=A\nNAME={hostname}\n".encode(), (as_ip, int(as_port)))
        data, _ = sock.recvfrom(1024)
    except socket.timeout:
        return None
    finally:
        sock.close()
    for token in data.decode().replace("\n", " ").split():
        if token.startswith("VALUE="):
            return token.split("=", 1)[1]
    return None


@app.route("/fibonacci")
def fibonacci():
    keys = ["hostname", "fs_port", "number", "as_ip", "as_port"]
    p = {k: request.args.get(k) for k in keys}
    if not all(p.values()):
        return "Missing parameters", 400

    ip = dns_lookup(p["hostname"], p["as_ip"], p["as_port"])
    if ip is None:
        return "Hostname not found", 404

    try:
        r = requests.get(f"http://{ip}:{p['fs_port']}/fibonacci",
                         params={"number": p["number"]}, timeout=5)
    except requests.RequestException:
        return "Could not reach Fibonacci server", 502
    return r.text, r.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
