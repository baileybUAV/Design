

import json
from graphviz import Digraph

# Load course data
with open('curriculum.json') as f:
    curriculum = json.load(f)

# Load student progress data
with open('student_progress.json') as f:
    progress = json.load(f)

courses = curriculum['courses']
completed = progress['completed_courses']

# 1. Print completed and remaining courses
print("✅ Completed Courses:")
for code in completed:
    name = courses[code]["name"]
    print(f" - {code}: {name}")

print("\n📌 Remaining Courses:")
for code, info in courses.items():
    if code not in completed:
        print(f" - {code}: {info['name']}")

# 2. Generate Prerequisite Flowchart
dot = Digraph(comment='Curriculum Flowchart')
dot.attr(rankdir='LR', size='8,5')

for code, info in courses.items():
    style = 'filled' if code in completed else 'dashed'
    color = 'lightblue' if info["type"] == "core" else 'lightgray'
    dot.node(code, f"{code}\n{info['name']}", style=style, fillcolor=color)

    for prereq in info.get("prerequisites", []):
        dot.edge(prereq, code)

# 3. Save and render the flowchart
dot.render('curriculum_flowchart', view=True, format='png')
print("\n🖼️ Flowchart generated: curriculum_flowchart.png")
