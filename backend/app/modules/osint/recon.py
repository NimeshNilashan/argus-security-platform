import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.exception
import dns.resolver
import requests
import whois


COMMON_SUBDOMAINS = [
    "www",
    "mail",
    "ftp",
    "dev",
    "test",
    "api",
    "admin",
]


def get_whois(domain: str):
    """Return WHOIS information for a domain."""

    try:
        details = whois.whois(domain)

        return {
            "domain_name": details.domain_name,
            "registrar": details.registrar,
            "creation_date": str(details.creation_date),
            "expiration_date": str(details.expiration_date),
            "updated_date": str(details.updated_date),
            "name_servers": list(details.name_servers or []),
            "country": details.country,
        }

    except Exception as error:
        return {
            "error": str(error)
        }


def get_dns_records(domain: str):
    """Return common DNS records."""

    records = {
        "A": [],
        "MX": [],
        "TXT": [],
        "NS": [],
    }

    for record_type in records:

        try:
            answers = dns.resolver.resolve(
                domain,
                record_type
            )

            for answer in answers:

                if record_type == "A":
                    records[record_type].append(
                        answer.address
                    )

                elif record_type == "MX":
                    records[record_type].append(
                        str(answer.exchange)
                    )

                elif record_type == "TXT":
                    records[record_type].append(
                        [
                            part.decode()
                            if isinstance(part, bytes)
                            else str(part)
                            for part in answer.strings
                        ]
                    )

                elif record_type == "NS":
                    records[record_type].append(
                        str(answer.target)
                    )

        except Exception as error:
            records[record_type] = {
                "error": str(error)
            }

    return records


def check_subdomain(subdomain: str):
    """Check whether a subdomain resolves."""

    try:
        answers = dns.resolver.resolve(
            subdomain,
            "A"
        )

        addresses = [
            answer.address
            for answer in answers
        ]

        return {
            "subdomain": subdomain,
            "addresses": addresses
        }

    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.exception.Timeout,
    ):
        return None

    except Exception as error:
        return {
            "subdomain": subdomain,
            "error": str(error)
        }


def enumerate_subdomains(domain: str):
    """Enumerate common subdomains."""

    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = [
            executor.submit(
                check_subdomain,
                f"{word}.{domain}"
            )
            for word in COMMON_SUBDOMAINS
        ]

        for future in as_completed(futures):

            result = future.result()

            if result:
                results.append(result)

    results.sort(
        key=lambda item: item["subdomain"]
    )

    return results


def check_reputation(
    domain: str,
    api_key: str
):
    """Check domain reputation using VirusTotal."""

    if not api_key:
        return {
            "error": "VirusTotal API key is not configured"
        }

    headers = {
        "x-apikey": api_key,
        "User-Agent": "Argus"
    }

    try:

        response = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": domain},
            timeout=15
        )

        response.raise_for_status()

        analysis_id = response.json()["data"]["id"]

        analysis_url = (
            "https://www.virustotal.com/api/v3/analyses/"
            f"{analysis_id}"
        )

        # Give VirusTotal a short time to process the request.
        time.sleep(5)

        result = requests.get(
            analysis_url,
            headers=headers,
            timeout=15
        )

        result.raise_for_status()

        data = result.json()

        attributes = (
            data
            .get("data", {})
            .get("attributes", {})
        )

        return {
            "stats": attributes.get("stats", {}),
            "results": attributes.get("results", {}),
        }

    except Exception as error:

        return {
            "error": str(error)
        }


def run_recon(
    domain: str,
    virustotal_api_key: str
):
    """Run the complete OSINT reconnaissance."""

    return {
        "domain": domain,
        "whois": get_whois(domain),
        "dns": get_dns_records(domain),
        "subdomains": enumerate_subdomains(domain),
        "reputation": check_reputation(
            domain,
            virustotal_api_key
        ),
    }