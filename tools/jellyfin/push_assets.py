import os, sys, glob, base64, hashlib

os.environ["TV_HOST"] = "192.168.0.193"
sys.path.insert(0, r"C:\Users\Sadman\.gemini\antigravity\scratch\cleanyourtv\tools")
import tv

def b64_push_file(dev, local_path, remote_path):
    with open(local_path, "rb") as f:
        data = f.read()
    want = hashlib.md5(data).hexdigest()
    chunk = min(48 * 1024, dev.max_chunk_size * 3 // 4 - 64)
    chunk -= chunk % 3
    tmp = remote_path + ".b64"
    dev.shell(f"rm -f {remote_path} {tmp}")
    n = (len(data) + chunk - 1) // chunk
    for i in range(n):
        part = base64.b64encode(data[i * chunk:(i + 1) * chunk]).decode()
        out = dev.shell(f"echo '{part}' >> {tmp} && echo ok{i}", read_timeout_s=30.0)
        if f"ok{i}" not in out:
            raise RuntimeError(f"chunk {i} failed: {out}")
    out = dev.shell(f"base64 -d {tmp} > {remote_path} && rm {tmp} && md5sum {remote_path}", read_timeout_s=30.0)
    got = out.split()[0] if out.strip() else ""
    if got != want:
        raise RuntimeError(f"MD5 mismatch for {remote_path}: got {got}, want {want}")

local_dir = r"C:\Users\Sadman\.gemini\antigravity\scratch\cleanyourtv\jellyfin_showcase"
remote_dir = "/sdcard/jellyfin_showcase"

print("Connecting to TV...")
dev = tv.connect(timeout=15)
print("Connected!")

dev.shell(f"mkdir -p {remote_dir}")

files = [
    "movies.json",
    "tile_0.jpg", "tile_1.jpg", "tile_2.jpg", "tile_3.jpg", "tile_4.jpg", "tile_5.jpg",
    "backdrop_0.jpg", "backdrop_1.jpg", "backdrop_2.jpg", "backdrop_3.jpg", "backdrop_4.jpg", "backdrop_5.jpg"
]

for fname in files:
    loc = os.path.join(local_dir, fname)
    rem = f"{remote_dir}/{fname}"
    print(f"Pushing {fname} ({os.path.getsize(loc)//1024} KB)...")
    b64_push_file(dev, loc, rem)

print("Checking remote files:")
print(dev.shell(f"ls -lh {remote_dir}"))

dev.close()
print("All showcase assets pushed to TV successfully!")
