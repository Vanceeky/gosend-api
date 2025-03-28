
def mask_name(name: str) -> str:
    parts = name.split()
    masked_parts = []  # List to hold the masked parts

    for part in parts:
        if len(part) > 1:
            # Mask all but the first character of each part
            masked_parts.append(part[0] + '*' * (len(part) - 1))
        else:
            # If the part is a single character, no masking is needed
            masked_parts.append(part)

    return ' '.join(masked_parts)  # Join the list of masked parts back into a string

@staticmethod
def format_name(details):
    """Format the full name correctly"""
    if not details:
        return "Unknown"

    first_name = details.first_name or ""
    middle_name = details.middle_name or ""
    last_name = details.last_name or ""
    suffix_name = details.suffix_name or ""

    return f"{first_name} {middle_name} {last_name} {suffix_name}".strip()