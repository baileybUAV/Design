
import json
import graphviz
import re

# Load JSON from file
with open("curriculum_full.json", "r") as f:
    courses = json.load(f)["courses"]

# Generate safe aliases for course codes
def make_alias(code, name):
    safe = re.sub(r'\W+', '_', name.strip())
    return f"{safe}_{code.replace(' ', '_')}"

# Create aliases
aliases = {code: make_alias(code, data["name"]) for code, data in courses.items()}

# Build semester mapping from JSON
semester_mapping = {
    code: data["semester"]
    for code, data in courses.items()
    if "semester" in data and data["semester"] is not None and code in aliases
}

# Build course dictionary with metadata
course_dicts = {}
for code in semester_mapping:
    data = courses[code]
    alias = aliases[code]
    prereqs = [aliases[p] for p in data.get("prerequisites", []) if p in aliases and p != "NONE"]
    course_dicts[alias] = {
        "name": alias,
        "abbrev": data["name"],
        "course": code,
        "type": "Major Core" if data["type"] == "required" else "General Core",
        "prereq": prereqs,
        "coreq": "N/A",
        "completed": "Y" if semester_mapping[code] == 0 else "N",
        "semester": semester_mapping[code]
    }

# Build schedule
max_sem = max(semester_mapping.values(), default=0)
schedule = [[] for _ in range(max_sem + 1)]
for code, sem in semester_mapping.items():
    schedule[sem].append(aliases[code])

# Create the flowchart with vertical layout
dot = graphviz.Digraph("flowchart")
dot.attr(rankdir="TB")

for semester in range(len(schedule)):
    with dot.subgraph(name=f"cluster_{semester}") as sub:
        sub.attr(label=f"Semester {semester + 1}")
        sub.attr(rank="same")
        for course_key in schedule[semester]:
            data = course_dicts[course_key]
            if data["completed"] == "Y":
                sub.attr("node", fontcolor="green")

            node_color = {
                "General Core": "lightblue",
                "Major Core": "firebrick3",
                "Engineering Core": "darkgoldenrod1"
            }.get(data["type"], "white")

            sub.node(course_key, data["abbrev"], style="filled", color=node_color)

# Add prerequisite edges, avoiding same-semester links
for course_key, data in course_dicts.items():
    for prereq in data["prereq"]:
        if course_dicts[prereq]["semester"] != data["semester"]:
            dot.edge(prereq, course_key)

# Output the flowchart
dot.render("vertical_course_flowchart", format="png")
print("Flowchart saved as vertical_course_flowchart.png")

