import base64
import yaml
import threading
from datetime import datetime
from pygnmi.client import gNMIclient
from google.protobuf.json_format import MessageToDict

def decode_val(val):
    if "jsonVal" in val:
        return base64.b64decode(val["jsonVal"]).decode("utf-8")
    elif "stringVal" in val:
        return val["stringVal"]
    elif "intVal" in val:
        return str(val["intVal"])
    elif "uintVal" in val:
        return str(val["uintVal"])
    else:
        return str(val)

def run_subscription(ip, username, password, path, mode="on_change", sample_interval=None):
    sub_entry = {"path": path, "mode": mode}
    if mode == "sample" and sample_interval:
        if sample_interval < 1_000_000_000:
            sample_interval = 1_000_000_000
        sub_entry["sample_interval"] = sample_interval

    sub_req = {"subscription": [sub_entry]}
    event_count = 0

    try:
        with gNMIclient(
            target=(ip, 57400),
            username=username,
            password=password,
            insecure=True,
            timeout=30
        ) as gc:
            print(f"[START] Subscribing to {path} on {ip} (mode={mode})...")
            for resp in gc.subscribe(sub_req):
                if not isinstance(resp, dict):
                    resp = MessageToDict(resp)
                updates = resp.get("update", {}).get("update", [])
                for u in updates:
                    val = decode_val(u.get("val", {}))
                    event_count += 1
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{ts}] ALERT #{event_count} ({ip}): {path} → {val}")
    except Exception as e:
        print(f"[ERROR] Subscription failed for {path} on {ip}: {e}")

def main():
    with open("subscriptions.yaml", "r") as f:
        config = yaml.safe_load(f)

    threads = []
    for host in config["hosts"]:
        ip = host["ip"]
        username = host.get("username", "admin")
        password = host.get("password", "admin")
        for sub in host["subscriptions"]:
            path = sub["path"]
            mode = sub.get("mode", "on_change")
            sample_interval = sub.get("sample_interval")
            t = threading.Thread(
                target=run_subscription,
                args=(ip, username, password, path, mode, sample_interval)
            )
            t.daemon = True
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()