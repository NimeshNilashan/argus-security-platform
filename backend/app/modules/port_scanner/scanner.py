import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


COMMON_PORTS = {
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP-Proxy",
}


def scan_port(target: str, port: int):
    """
    Scan one TCP port and return structured data
    when the port is open.
    """

    sock = socket.socket()
    sock.settimeout(2.0)

    try:
        sock.connect((target, port))

        service = COMMON_PORTS.get(
            port,
            "Unknown"
        )

        banner = None

        try:
            sock.settimeout(2.0)
            sock.send(b"HEAD / HTTP/1.1\r\n\r\n")
            banner = sock.recv(1024).decode(
                errors="ignore"
            ).strip()

        except (socket.timeout, OSError):
            pass

        return {
            "port": port,
            "service": service,
            "banner": banner
        }

    except (ConnectionRefusedError, socket.timeout, OSError):
        return None

    finally:
        sock.close()


def scan(target: str, max_port: int):
    """
    Scan ports from 1 to max_port concurrently.
    Returns a list of open ports.
    """

    results = []

    with ThreadPoolExecutor(max_workers=50) as executor:

        futures = [
            executor.submit(
                scan_port,
                target,
                port
            )
            for port in range(1, max_port + 1)
        ]

        for future in as_completed(futures):

            result = future.result()

            if result:
                results.append(result)

    results.sort(key=lambda item: item["port"])

    return results