import hashlib


def calculate_hashes(file_path):
    sha256_hash = hashlib.sha256()
    sha512_hash = hashlib.sha512()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
            sha512_hash.update(chunk)

    return sha256_hash.hexdigest(), sha512_hash.hexdigest()
