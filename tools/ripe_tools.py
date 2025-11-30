from crewai.tools import tool
import requests
import re
from netaddr import IPNetwork, IPSet
import time
from typing import List, Dict

RIPE = "https://stat.ripe.net/data"
HEADERS = {'User-Agent': 'CrewAI Ripe IP Analyzer'}


@tool
def fetch_country_prefixes(country: str = "IL") -> str:
    """Fetch all IPv4 prefixes assigned to a given country code from RIPE NCC."""
    try:
        url = f"{RIPE}/country-resource-list/data.json"
        r = requests.get(
            url,
            params={"resource": country.lower(), "v4_format": "prefix"},
            headers=HEADERS,
            timeout=10
        )
        r.raise_for_status()
        response_data = r.json()

        if "data" not in response_data:
            return f"ERROR: Invalid response structure"

        data = response_data["data"]

        # תמיכה בפורמטים שונים של RIPE
        if isinstance(data, dict):
            if "ipv4_prefixes" in data:
                prefixes = data["ipv4_prefixes"]
            elif "resources" in data:
                prefixes = data["resources"].get("ipv4", [])
            else:
                return f"ERROR: Unknown data structure"
        elif isinstance(data, list):
            prefixes = data
        else:
            return f"ERROR: Data is unexpected type"

        if not prefixes:
            return f"WARNING: No prefixes found for {country}"

        # Extract prefix strings
        if prefixes and isinstance(prefixes[0], dict):
            prefix_list = [p.get("prefix") or p.get("resource") for p in prefixes]
        else:
            prefix_list = prefixes

        prefix_list = [p for p in prefix_list if p]

        if not prefix_list:
            return f"ERROR: Could not extract prefixes"

        result = ", ".join(prefix_list[:20])
        return f"Found {len(prefix_list)} prefixes for {country}: {result}"
    except Exception as e:
        return f"ERROR: Failed to fetch prefixes. {str(e)}"


@tool
def prefixes_by_isp(prefixes_list: str) -> str:
    """Get ASN and ISP info for IP prefixes. Input: comma-separated CIDR prefixes or IPs."""
    try:
        # Extract CIDR patterns or single IPs
        cidr_pattern = r'\b\d+\.\d+\.\d+\.\d+(?:/\d+)?\b'
        matches = re.findall(cidr_pattern, prefixes_list)

        if matches:
            prefixes = matches
        else:
            prefixes = [p.strip() for p in prefixes_list.split(",") if p.strip()]

        if not prefixes:
            return "ERROR: No valid IP addresses or CIDR prefixes found"

        output: Dict[str, Dict] = {}

        # Process each prefix/IP
        for item in prefixes[:10]:  # Limit to first 10
            try:
                # חלץ את ה-IP הראשון מה-CIDR (אם זה CIDR)
                ip = item.split('/')[0]

                # השתמש ב-RIPE prefix-overview API
                r = requests.get(
                    f"{RIPE}/prefix-overview/data.json",
                    params={"resource": item},
                    timeout=15,
                    headers=HEADERS
                )
                r.raise_for_status()
                response_data = r.json()

                asn = "UNKNOWN"
                description = "Unknown ISP"

                if "data" in response_data and response_data["data"]:
                    data = response_data["data"]

                    if isinstance(data, dict):
                        # קבל את ה-ASN
                        if "asns" in data and isinstance(data["asns"], list) and len(data["asns"]) > 0:
                            asn_item = data["asns"][0]
                            if isinstance(asn_item, dict):
                                asn = str(asn_item.get("asn", "UNKNOWN"))
                                description = str(asn_item.get("holder", "Unknown ISP"))
                            elif isinstance(asn_item, str):
                                asn = asn_item

                # שמור את המידע
                key = f"AS{asn}"
                if key not in output:
                    output[key] = {
                        "description": description,
                        "prefixes": []
                    }
                output[key]["prefixes"].append(item)

            except requests.exceptions.Timeout:
                key = "ERROR_TIMEOUT"
                if key not in output:
                    output[key] = {"description": "Request timed out", "prefixes": []}
                output[key]["prefixes"].append(item)
            except requests.exceptions.RequestException as req_err:
                key = "ERROR_HTTP"
                if key not in output:
                    output[key] = {"description": str(req_err), "prefixes": []}
                output[key]["prefixes"].append(item)
            except Exception as e:
                key = "ERROR"
                if key not in output:
                    output[key] = {"description": str(e), "prefixes": []}
                output[key]["prefixes"].append(item)

            time.sleep(0.2)

        # פורמט התשובה בצורה קריאה
        result_lines = []
        for asn, info in sorted(output.items()):
            prefixes = info.get("prefixes", [])
            description = info.get("description", "")

            if asn.startswith("AS"):
                result_lines.append(f"\n{asn}: {description}")
                result_lines.append(f"  Prefixes ({len(prefixes)}): {', '.join(prefixes)}")
            else:
                result_lines.append(f"\n{asn}: {description}")
                result_lines.append(f"  Items ({len(prefixes)}): {', '.join(prefixes)}")

        return "\n".join(result_lines) if result_lines else "No results found"

    except Exception as e:
        return f"ERROR: Failed to get ASN info. {str(e)}"


