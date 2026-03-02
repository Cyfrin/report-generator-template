import json
import os

AUDITORS_JSON = './source/auditors.json'
SOURCE_LEAD = './source/lead_auditors.md'
SOURCE_ASSISTING = './source/assisting_auditors.md'
WORKING_LEAD = './working/lead_auditors.md'
WORKING_ASSISTING = './working/assisting_auditors.md'


def _load_auditor_mapping():
    if not os.path.exists(AUDITORS_JSON):
        print(f"Auditor mapping file not found: '{AUDITORS_JSON}'. Please create it.")
        exit(1)

    with open(AUDITORS_JSON, 'r') as f:
        try:
            mapping = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in '{AUDITORS_JSON}': {e}")
            exit(1)

    for name, entry in mapping.items():
        if 'link' not in entry:
            print(f"Auditor '{name}' in '{AUDITORS_JSON}' is missing required 'link' field.")
            exit(1)

    return mapping


def _read_names(filepath):
    if not os.path.exists(filepath):
        print(f"Auditor source file not found: '{filepath}'.")
        exit(1)

    with open(filepath, 'r') as f:
        names = [line.strip() for line in f if line.strip()]

    return names


def _resolve_name(name, mapping):
    if name not in mapping:
        print(f"Auditor '{name}' not found in '{AUDITORS_JSON}'. Please add them to the mapping.")
        exit(1)

    entry = mapping[name]
    result = f"[{name}]({entry['link']})"

    if 'members' in entry:
        member_parts = []
        for member_name in entry['members']:
            if member_name not in mapping:
                print(f"Team member '{member_name}' (referenced by '{name}') not found in '{AUDITORS_JSON}'. Please add them to the mapping.")
                exit(1)
            member_parts.append(f"[{member_name}]({mapping[member_name]['link']})")
        result += " (" + ", ".join(member_parts) + ")"
    elif 'suffix' in entry:
        result += f" ({entry['suffix']})"

    return result


def _resolve_file(source_path, output_path, mapping):
    names = _read_names(source_path)
    lines = []
    for name in names:
        lines.append(_resolve_name(name, mapping))

    with open(output_path, 'w') as f:
        f.write("\n\n".join(lines))
        if lines:
            f.write("\n")


def resolve_auditors():
    mapping = _load_auditor_mapping()

    lead_names = _read_names(SOURCE_LEAD)
    if not lead_names:
        print(f"No lead auditors found in '{SOURCE_LEAD}'. At least one lead auditor is required.")
        exit(1)

    _resolve_file(SOURCE_LEAD, WORKING_LEAD, mapping)

    assisting_names = _read_names(SOURCE_ASSISTING)
    if assisting_names:
        _resolve_file(SOURCE_ASSISTING, WORKING_ASSISTING, mapping)
    else:
        with open(WORKING_ASSISTING, 'w') as f:
            f.write("")
