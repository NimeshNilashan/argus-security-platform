import hashlib


def calculate_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()



def verify_hash(
    file_path: str,
    saved_hash: str
):
    """
    Compare current file hash with saved hash.
    """

    current_hash = calculate_hash(file_path)

    return {
        "current_hash": current_hash,
        "saved_hash": saved_hash,
        "modified": current_hash != saved_hash
    }