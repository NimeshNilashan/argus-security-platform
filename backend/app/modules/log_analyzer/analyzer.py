import re


ATTACK_PATTERNS = {
    "SQL Injection": r"union|select|drop|insert|or\s+1=1",
    "Directory Traversal": r"\.\./",
    "XSS": r"<script|onerror\s*=|javascript:",
    "Scanner Detected": r"nikto|sqlmap|nmap",
}


IP_PATTERN = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"
REQUEST_PATTERN = r'"([A-Z]+) (.+?) HTTP/([0-9.]+)"'
USER_AGENT_PATTERN = r'"([^"]*)"$'


def analyze_log(file_path: str):
    """
    Analyze a log file and return structured security results.
    """

    findings = {
        name: []
        for name in ATTACK_PATTERNS
    }

    total_lines = 0

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        for line in file:

            total_lines += 1

            ip_match = re.search(
                IP_PATTERN,
                line
            )

            ip_address = (
                ip_match.group()
                if ip_match
                else None
            )

            # Check HTTP request path.
            request_match = re.search(
                REQUEST_PATTERN,
                line,
                re.IGNORECASE
            )

            if request_match:

                path = request_match.group(2)

                for name, pattern in ATTACK_PATTERNS.items():

                    if (
                        ip_address
                        and re.search(
                            pattern,
                            path,
                            re.IGNORECASE
                        )
                    ):
                        findings[name].append(
                            ip_address
                        )

            # Check User-Agent.
            user_agent_match = re.search(
                USER_AGENT_PATTERN,
                line.strip()
            )

            if user_agent_match:

                user_agent = user_agent_match.group(1)

                for name, pattern in ATTACK_PATTERNS.items():

                    if (
                        ip_address
                        and re.search(
                            pattern,
                            user_agent,
                            re.IGNORECASE
                        )
                    ):
                        findings[name].append(
                            ip_address
                        )

    attacks_detected = sum(
        len(entries)
        for entries in findings.values()
    )

    return {
        "total_lines": total_lines,
        "attacks_detected": attacks_detected,
        "findings": findings,
    }