import socket
from flask import Flask, request

app = Flask(__name__)


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.route("/register", methods=["PUT"])
def register():
    body = request.get_json(silent=True) or {}
    hostname = body.get("hostname")
    ip = body.get("ip")
    as_ip = body.get("as_ip")
    as_port = body.get("as_port", 53533)
    if not (hostname and ip and as_ip):
        return "Missing fields", 400

    msg = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (as_ip, int(as_port)))
    sock.close()
    return "Registered", 201


@app.route("/fibonacci")
def fibonacci():
    number = request.args.get("number")
    try:
        n = int(number)
        if n < 0:
            raise ValueError
    except (TypeError, ValueError):
        return "Bad number", 400
    return str(fib(n)), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
