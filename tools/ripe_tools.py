from crewai.tools import tool
import requests
from netaddr import IPNetwork, IPSet
import time
import re
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
    """Group a list of IP prefixes by their ASN owner (ISP). Input should be comma-separated CIDR strings."""
    try:
        # Extract CIDR patterns
        cidr_pattern = r'\b\d+\.\d+\.\d+\.\d+/\d+\b'
        matches = re.findall(cidr_pattern, prefixes_list)

        if matches:
            prefixes = matches
        else:
            prefixes = [p.strip() for p in prefixes_list.split(",") if p.strip()]

        if not prefixes:
            return "ERROR: No valid CIDR prefixes found"

        output: Dict[str, List[str]] = {}

        # Limit to first 5
        for prefix in prefixes[:5]:
            try:
                # קודם כל, נסה network-info API
                r = requests.get(
                    f"{RIPE}/network-info/data.json",
                    params={"resource": prefix},
                    timeout=20,
                    headers=HEADERS
                )
                r.raise_for_status()
                response_data = r.json()

                if "data" in response_data and response_data["data"]:
                    data = response_data["data"]

                    # חפש ASN בנתוני network-info
                    if "asns" in data and data["asns"]:
                        asn_info = data["asns"][0]
                        asn = asn_info.get("asn", "UNKNOWN")
                        holder = asn_info.get("holder", "Unknown ISP")
                        key = f"AS{asn}: {holder}"
                    elif "holder" in data:
                        key = data["holder"]
                    else:
                        key = "UNKNOWN"

                    output.setdefault(key, []).append(prefix)
                else:
                    # אם network-info לא עובד, נסה prefix-overview
                    r2 = requests.get(
                        f"{RIPE}/prefix-overview/data.json",
                        params={"resource": prefix},
                        timeout=20,
                        headers=HEADERS
                    )
                    r2.raise_for_status()
                    response_data2 = r2.json()

                    if "data" in response_data2 and response_data2["data"]:
                        data2 = response_data2["data"]
                        if data2.get("asns"):
                            asn_info = data2["asns"][0]
                            asn = asn_info.get("asn", "UNKNOWN")
                            key = f"AS{asn}"
                        else:
                            key = "UNKNOWN"
                        output.setdefault(key, []).append(prefix)
                    else:
                        output.setdefault("UNKNOWN", []).append(prefix)

            except requests.exceptions.Timeout:
                output.setdefault("ERROR_TIMEOUT", []).append(prefix)
            except requests.exceptions.RequestException as re:
                output.setdefault("ERROR_HTTP", []).append(f"{prefix}: {str(re)}")
            except Exception as e:
                output.setdefault("ERROR", []).append(f"{prefix}: {str(e)}")

            time.sleep(0.3)

        return str(output)
    except Exception as e:
        return f"ERROR: Failed to group prefixes. {str(e)}"


