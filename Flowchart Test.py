import graphviz
import json

#Example using json library
#creating dictionary
Foundations_of_Engineering = {
    "name": "Foundations_of_Engineering",
    "abbrev": "Foundations of Eng",
    "course": "EGN 3000",
    "type": "Engineering Core",
    "prereq": "N/A",
    "coreq": "N/A",
    "completed": "Y",
}
Calculus_I = {
    "name": "Calculus_I",
    "abbrev": "Calc I",
    "course": "MAC 2281",
    "type": "Major Core",
    "prereq": "N/A",
    "coreq": "N/A",
    "completed": "Y",
}
Foundations_of_Engineering_Lab= {
    "name": "Foundations_of_Engineering_Lab",
    "abbrev": "Foundations of Eng Lab",
    "course": "EGN 3000L",
    "type": "Engineering Core",
    "prereq": "N/A",
    "coreq": "N/A",
    "completed": "Y",
}
Composition_I = {
    "name": "Composition_I",
    "abbrev": "Comp I",
    "course": "ENC 1101",
    "type": "General Core",
    "prereq": "N/A",
    "coreq": "N/A",
    "completed": "Y",
}
#Semester 2
Calculus_II = {
    "name": "Calculus_II",
    "abbrev": "Calc II",
    "course": "MAC 2282",
    "type": "Major Core",
    "prereq": "Calculus_I",
    "coreq": "N/A",
    "completed": "N",
}
General_Physics_I = {
    "name": "General_Physics_I",
    "abbrev": "Gen Physics I",
    "course": "PHY 2048",
    "type": "Major Core",
    "prereq": "Calculus_I",
    "coreq": "General_Physics_I_Lab",
    "completed": "N",
}
General_Physics_I_Lab = {
    "name": "General_Physics_I_Lab",
    "abbrev": "Gen Physics I Lab",
    "course": "PHY 2048L",
    "type": "Major Core",
    "prereq": "N/A",
    "coreq": "General_Physics_I",
    "completed": "N",
}
Composition_II = {
    "name": "Composition_II",
    "abbrev": "Comp II",
    "course": "ENC 1102",
    "type": "General Core",
    "prereq": "Composition_I",
    "coreq": "N/A",
    "completed": "N",
}

schedule = [[],[],[],[],[],[],[],[],[]]

# adds course to schedule list
#semester 0 = first semester taking courses, semester 1 = second semester, etc.
def flowchart_gen(course, semester, add_remove):
    if add_remove == True:
        schedule[semester].append(course)
    else:
        schedule[semester].remove(course)

#Filling course list for the first two semesters
flowchart_gen("Foundations_of_Engineering",0,True)
flowchart_gen("Calculus_I",0,True)
flowchart_gen("Foundations_of_Engineering_Lab",0,True)
flowchart_gen("Composition_I",0,True)

flowchart_gen("Calculus_II",1,True)
flowchart_gen("General_Physics_I",1,True)
flowchart_gen("General_Physics_I_Lab",1,True)
flowchart_gen("Composition_II",1,True)

#Making flowchart
#attr command effects all later nodes/edges in the same sub-graph
dot = graphviz.Digraph('flowchart', comment='Curriculum FLowchart')
for semester in range(2):
    n = len([len(x) for x in schedule[semester]]) #num of classes in the semester sublist
    with dot.subgraph(name = 'cluster_'+str(semester)) as a:
        a.attr(label = 'semester '+str(semester+1))
        for classes in range(n):
            node_name = str(semester)+str(classes)
            course = schedule[semester][classes]
            dictionary = globals()[course] #fetches dictionary
            
            if dictionary.get("completed") == "Y":
                a.attr("node", fontcolor="green")

            if dictionary.get("type") == "General Core":
                a.node(course, style='filled', color='lightblue')
            elif dictionary.get("type") == "Major Core":
                a.node(course, style='filled', color='firebrick3')
            elif dictionary.get("type") == "Engineering Core":
                a.node(course, style='filled', color='darkgoldenrod1')
            else:
                a.node(course)

            if dictionary.get("prereq") != "N/A":
                prereq = dictionary.get("prereq")
                a.edge(prereq, course)
                #a.attr(course, style = 'filled')

            if dictionary.get("coreq") != "N/A":
                coreq = dictionary.get("coreq")
                a.edge(coreq, course, dir='none')

            
print(dot.source)

dot.view()