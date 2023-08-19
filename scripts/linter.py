import re


def replace_org_in_link(line, internal_org, source_org):    
    # Identify all links
    links = re.findall('https?://[^\s<>"]+|[^\s<>"]+\.[^\s<>"]+', line)

    for link in links:
        if re.search(internal_org, link, re.IGNORECASE):
            # Replace internal organization link with source repo link (case-insensitive)
            new_link = re.sub(internal_org, source_org, link, flags=re.IGNORECASE)
            line = line.replace(link, new_link)

    return line


def replace_ampersand_in_findings_headings(line):
    # If the line is a finding markdown heading and contains '&', replace '&' with 'and'
    if line.strip().startswith('###') and '&' in line:
        line = line.replace('&', 'and')

    return line


def lint(report, team_name, source_org, internal_org):
    for line in report:
        new_line = line
        
        # Replace any internal organization repo links
        new_line = replace_org_in_link(new_line, internal_org, source_org)
        
        # Replace any '&' in finding headings with 'and'
        new_line = replace_ampersand_in_findings_headings(new_line)

        report[report.index(line)] = new_line

    # Check for link structures ( format [something](url) ) that don't start with http
    for line in report:
        pos = line.find("](")
        while pos != -1:
            # Check if the first 4 characters after the open-paren are "http"
            if line[pos+2:pos+6] != "http" and line[pos+2] != "#":
                position = report.index(line)
                print(f"Possible broken link at report.md line {position}: ")
                print(f"\t{line}")
            pos = line.find("](", pos+1)

    # Check for raw links ("http" string not immediately preceded by a link structure)
    for line in report:
        pos = line.find("http")
        while pos != -1:
            # Check if the character to the left of "http" is an open-paren preceded by a close-bracket
            if line[pos-2:pos] != "](":
                position = report.index(line)
                print(f"Possible raw link at report.md line {position}: ")
                print(f"\t{line}")
            pos = line.find("http", pos+1)

    # Check for descriptions not starting in the same line as the headers
    lineNumber = 0
    for line in report:        
        # If there's a newline, merge the next line with the current one
        if (
            (line.startswith("**Context:**") and len(line) < len("**Context:**") + 5) or
            (line.startswith("**Description:**") and len(line) < len("**Description:**") + 5) or
            (line.startswith("**Impact:**") and len(line) < len("**Impact:**") + 5) or
            (line.startswith("**Recommendation:**") and len(line) < len("**Recommendation:**") + 5) or
            (line.startswith("**" + internal_org + ":**") and len(line) < len("**" + internal_org +":**") + 5) or
            (line.startswith("**" + team_name + ":**") and len(line) < len("**" + team_name + ":**") + 5)):
            
            # There might be more than one empty lines following the header, remove them
            while report[lineNumber + 1] == "":
                del report[lineNumber + 1]

            nextLine = report[lineNumber + 1]
            # If it's a list, code or quote, don't merge
            if (not nextLine.lstrip().startswith("-") and 
                not nextLine.lstrip().startswith("1.") and 
                not nextLine.lstrip().startswith("```") and
                not nextLine.lstrip().startswith("#") and
                not nextLine.lstrip().startswith(">")): 
                
                report[lineNumber] = line + " " + nextLine.lstrip()
                del report[lineNumber + 1]

        lineNumber = lineNumber + 1

    return report
