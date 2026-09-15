import sys

try:
    if len(sys.argv) > 1:
        destination = sys.argv[1]
    else:
        destination = "/tmp/aeo-payload.json"
    payload = sys.stdin.buffer.read()
    with open(destination, "ab") as f:
        f.write(payload + b"\n")
except:
    pass

sys.exit(0)
