from crewai import Task, Agent


def create_tasks(agent: Agent):
    """יוצר ומחזיר את רשימת המשימות המלאה עבור ה-Agent שסופק."""

    fetch_prefixes_task = Task(
        description=(
            "Use the 'fetch_country_prefixes' tool to retrieve all IPv4 prefixes "
            "assigned to Israel (IL) from RIPE. Get a complete list of all prefixes."
        ),
        expected_output="A clean, raw list of IPv4 prefixes in CIDR format for Israel.",
        agent=agent,
        name="fetch_israeli_prefixes",
    )

    group_by_isp_task = Task(
        description=(
            "Using the raw prefix list from the previous step, use the 'prefixes_by_isp' tool "
            "to group these prefixes by their respective ISP/ASN owner. Analyze which ISPs own which prefixes."
        ),
        expected_output="A mapping (dictionary) where keys are ISP/ASN names (e.g., AS1234) and values are lists of associated CIDR prefixes.",
        agent=agent,
        context=[fetch_prefixes_task],
        name="group_prefixes_by_isp",
    )



    return [
        fetch_prefixes_task,
        group_by_isp_task
    ]