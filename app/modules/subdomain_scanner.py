# app/modules/subdomain_scanner.py

import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Asset, ScanJob, Finding

DEFAULT_WORDLIST = ["www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2", "smtp", "secure", "vpn", "api", "dev", "staging"]

class SubdomainScannerModule:
    def __init__(self, db: Session):
        self.db = db

    def _resolve_subdomain(self, subdomain: str) -> dict | None:
        """Helper to resolve a single subdomain via dnspython."""
        try:
            answers = dns.resolver.resolve(subdomain, 'A')
            ips = [rdata.address for rdata in answers]
            return {
                "subdomain": subdomain,
                "ips": ips
            }
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            return None
        except Exception:
            return None

    def run_scan(self, asset_id: int, wordlist: list[str] = DEFAULT_WORDLIST) -> dict:
        """Main runner for subdomain enumeration."""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset ID {asset_id} not found")

        domain = asset.target
        discovered_subdomains = []

        # 1. Multi-threaded resolution using your dnspython logic
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {
                executor.submit(self._resolve_subdomain, f"{word}.{domain}"): word
                for word in wordlist
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    discovered_subdomains.append(result)

        # Sort results by subdomain name
        discovered_subdomains.sort(key=lambda x: x["subdomain"])

        # 2. Process results through the differential engine
        self._process_scan_results(asset_id, discovered_subdomains)

        return {"status": "completed", "discovered_count": len(discovered_subdomains)}

    def _process_scan_results(self, asset_id: int, current_subdomains: list[dict]):
        # Fetch previous scan
        last_job = (
            self.db.query(ScanJob)
            .filter(ScanJob.asset_id == asset_id, ScanJob.module_name == "subdomain_scan", ScanJob.status == "SUCCESS")
            .order_by(desc(ScanJob.timestamp))
            .first()
        )

        previous_subdomains = []
        if last_job and "subdomains" in last_job.raw_output:
            previous_subdomains = last_job.raw_output["subdomains"]

        # Differential Set Math
        prev_set = set(item["subdomain"] for item in previous_subdomains)
        crnt_set = set(item["subdomain"] for item in current_subdomains)

        newly_discovered_names = crnt_set - prev_set
        newly_removed_names = prev_set - crnt_set

        newly_discovered_details = [s for s in current_subdomains if s["subdomain"] in newly_discovered_names]
        newly_removed_details = [s for s in previous_subdomains if s["subdomain"] in newly_removed_names]

        # Record Scan Job
        new_job = ScanJob(
            asset_id=asset_id,
            module_name="subdomain_scan",
            status="SUCCESS",
            raw_output={"subdomains": current_subdomains}
        )
        self.db.add(new_job)
        self.db.flush()

        # Generate Alerts (Findings)
        for detail in newly_discovered_details:
            finding = Finding(
                asset_id=asset_id,
                scan_job_id=new_job.id,
                severity="LOW",
                title=f"New Subdomain Discovered: {detail['subdomain']}",
                details=detail
            )
            self.db.add(finding)

        for detail in newly_removed_details:
            finding = Finding(
                asset_id=asset_id,
                scan_job_id=new_job.id,
                severity="INFO",
                title=f"Subdomain Unreachable / Removed: {detail['subdomain']}",
                details=detail
            )
            self.db.add(finding)

        self.db.commit()