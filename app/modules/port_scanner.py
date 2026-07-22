import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Asset, ScanJob, Finding


class PortScannerModule:
    def __init__(self, db: Session):
        self.db = db
        self.common_ports = {
            21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL"
        }

    # ... (Keep the _scan_single_port and run_scan methods we discussed earlier) ...
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
        try:
            # 1. Fetch the asset from the DB
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                raise ValueError(f"Asset ID {asset_id} not found")

            target_host = asset.target
            open_ports = []

            # 2. Concurrently scan target ports
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {
                    executor.submit(self._scan_single_port, target_host, port): port
                    for port in range(1, max_ports + 1)
                }
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        open_ports.append(result)

            open_ports.sort(key=lambda x: x["port"])

            # 3. Handle Database comparisons
            self._process_scan_results(asset_id, open_ports)

            return {"status": "completed", "open_ports_count": len(open_ports)}

        except Exception as e:
            # --- THE SAFETY NET ---
            # 1. Clear any corrupted or pending database transactions
            self.db.rollback()

            # 2. Record the failure in the database so you have an audit trail
            failed_job = ScanJob(
                asset_id=asset_id,
                module_name="port_scan",
                status="FAILED",
                raw_output={"error": str(e)}  # Save the exact Python error message
            )
            self.db.add(failed_job)
            self.db.commit()

            # Print to your server console so you can see it while debugging
            print(f"Scan failed for asset {asset_id}: {str(e)}")

            return {"status": "failed", "error": str(e)}
    def _process_scan_results(self, asset_id: int, current_open_ports: list[dict]):
        # 1. DATABASE FETCH: Get the previous scan data
        last_job = (
            self.db.query(ScanJob)
            .filter(ScanJob.asset_id == asset_id, ScanJob.module_name == "port_scan", ScanJob.status == "SUCCESS")
            .order_by(desc(ScanJob.timestamp))
            .first()
        )

        previous_ports = []
        if last_job and "open_ports" in last_job.raw_output:
            previous_ports = last_job.raw_output["open_ports"]


        prev_port_nums = set([item["port"] for item in previous_ports])  # Update this
        crnt_port_nums = set([port["port"] for port in current_open_ports])  # Update this

        # 2. Do your set math to find the changes
        newly_opened_nums = set(crnt_port_nums - prev_port_nums)  # Update this
        newly_closed_nums = set(prev_port_nums - crnt_port_nums)  # Update this

        print("newly_opened_nums : ", newly_opened_nums)
        print("newly_closed_nums : ", newly_closed_nums)

        # 3. Now, write loops to find the FULL dictionary for the changed ports
        newly_opened_details = []
        # Write a loop that checks current_scan for the ports in newly_opened_nums
        for item in current_open_ports:
            if item["port"] in newly_opened_nums:
                newly_opened_details.append(item)

        newly_closed_details = []
        # Write a loop that checks previous_scan for the ports in newly_closed_nums
        for item in previous_ports:
            if item["port"] in newly_closed_nums:
                newly_closed_details.append(item)

        print(f"Newly opened details: {newly_opened_details}")
        print(f"Newly closed details: {newly_closed_details}")
        # 3. DATABASE SAVE: Record the raw scan
        new_job = ScanJob(
            asset_id=asset_id,
            module_name="port_scan",
            status="SUCCESS",
            raw_output={"open_ports": current_open_ports}
        )
        self.db.add(new_job)
        self.db.flush()  # Gets us the new_job.id without finalizing yet

        # 4. DATABASE SAVE: Record the Findings (Alerts)
        for detail in newly_opened_details:
            finding = Finding(
                asset_id=asset_id,
                scan_job_id=new_job.id,
                severity="MEDIUM",  # Medium severity for a new open port
                title=f"New Open Port Discovered: {detail['port']}",
                details=detail
            )
            self.db.add(finding)

        for detail in newly_closed_details:
            finding = Finding(
                asset_id = asset_id,
                scan_job_id=new_job.id,
                severity="INFO",
                title=f"Previously Open Port Closed: {detail['port']}",
                details=detail
            )
            self.db.add(finding)

        # 5. Commit the transaction to PostgreSQL
        self.db.commit()