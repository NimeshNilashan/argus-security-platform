# app/modules/port_scanner.py

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models import Asset, ScanJob, Finding


class PortScannerModule:
    def __init__(self, db: Session):
        self.db = db
        # A list of common ports we want to scan (heuristic map)
        self.common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 443: "HTTPS", 3306: "MySQL",
            3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy"
        }

    def _scan_single_port(self, target: str, port: int) -> dict | None:
        """
        Attempts a TCP connection to a port.
        Returns a dictionary with details if open, or None if closed/filtered.
        """
        sock = socket.socket()
        sock.settimeout(1.5)
        try:
            sock.connect((target, port))
            # Grab banner (optional/basic probe)
            banner = None
            try:
                sock.send(b'HEAD / HTTP/1.1\r\n\r\n')
                banner = sock.recv(512).decode(errors="ignore").strip()
            except socket.timeout:
                pass

            return {
                "port": port,
                "service": self.common_ports.get(port, "Unknown"),
                "banner": banner if banner else None
            }
        except (ConnectionRefusedError, socket.timeout):
            return None
        finally:
            sock.close()

    def run_scan(self, asset_id: int, max_ports: int = 1000) -> dict:
        """
        Main runner: Coordinates the thread pool and database logic.
        """
        # 1. Fetch the asset from the DB
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset ID {asset_id} not found")

        target_host = asset.target
        open_ports = []

        # 2. Concurrently scan target ports (replacing your global executor)
        with ThreadPoolExecutor(max_workers=50) as executor:
            # We scan up to the user's requested port count
            futures = {
                executor.submit(self._scan_single_port, target_host, port): port
                for port in range(1, max_ports + 1)
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)

        # Sort the results by port number for consistency
        open_ports.sort(key=lambda x: x["port"])

        # 3. Handle Database comparisons (THE TASK AT HAND)
        self._process_scan_results(asset_id, open_ports)

        return {"status": "completed", "open_ports_count": len(open_ports)}

    def _process_scan_results(self, asset_id: int, current_open_ports: list[dict]):
        """
        Calculates the differences between the new scan and the last completed scan.
        Saves a ScanJob and creates Findings for status changes.
        """
        pass