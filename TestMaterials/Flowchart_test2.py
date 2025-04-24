import json
import graphviz

# ----------------------------
# Load classes_with_grades.json
# ----------------------------
with open("classes_with_grades.json", "r") as f:
    data = json.load(f)

# ----------------------------
# Group courses by term
# ----------------------------
term_groups = {}
for course_code, info in data.items():
    term = info.get("term", "Unknown")
    term_groups.setdefault(term, []).append(course_code)

# ----------------------------
# Sort terms chronologically
# ----------------------------
def term_sort_key(term):
    parts = term.split()
    if len(parts) == 2:
        season, year = parts
        season_order = {"Spring": 1, "Summer": 2, "Fall": 3}
        return (int(year), season_order.get(season, 0))
    return (9999, 0)

sorted_terms = sorted(term_groups.keys(), key=term_sort_key)

# ----------------------------
# Create Graphviz flowchart
# ----------------------------
dot = graphviz.Digraph("flowchart")
dot.attr(rankdir="TB")  # Top to bottom

previous_term = None
term_anchor_nodes = []

for i, term in enumerate(sorted_terms):
    with dot.subgraph(name=f"cluster_{term.replace(' ', '_')}") as sub:
        sub.attr(label=term)
        sub.attr(style="rounded")
        sub.attr(rank="same")

        # Add anchor node for centering
        anchor_id = f"anchor_{i}"
        sub.node(anchor_id, label="", shape="point", width="0", height="0", style="invis")
        term_anchor_nodes.append(anchor_id)

        # Add course nodes
        for course_code in term_groups[term]:
            sub.node(course_code, label=course_code, style="filled", color="lightblue")

# Create invisible vertical chain to stack anchors and force vertical alignment
for i in range(len(term_anchor_nodes) - 1):
    dot.edge(term_anchor_nodes[i], term_anchor_nodes[i + 1], style="invis", weight="100")

# ----------------------------
# Output PNG file
# ----------------------------
dot.render("transcript_semester_flowchart", format="png", cleanup=True)
print("✅ Flowchart saved as transcript_semester_flowchart.png")
