import json
import os
import socket

PORT = 53533
DB_FILE = "records.json"


def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {}


def save(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)


def parse(msg):
    fields = {}
    for token in msg.replace("\n", " ").split():
        if "=" in token:
            k, v = token.split("=", 1)
            fields[k] = v
    return fields


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
print(f"AS listening on UDP {PORT}", flush=True)

while True:
    data, addr = sock.recvfrom(1024)
    fields = parse(data.decode())
    name = fields.get("NAME")
    if not name:
        continue

    if "VALUE" in fields:  # registration
        db = load()
        db[name] = {"type": fields.get("TYPE", "A"),
                    "value": fields["VALUE"],
                    "ttl": fields.get("TTL", "10")}
        save(db)
        print("Registered", name, fields["VALUE"], flush=True)
    else:  # DNS query
        rec = load().get(name)
        if rec:
            reply = f"TYPE={rec['type']}\nNAME={name} VALUE={rec['value']} TTL={rec['ttl']}\n"
            sock.sendto(reply.encode(), addr)
