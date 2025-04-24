import tkinter as tk
import webbrowser as wb
from tkinter import messagebox, filedialog, ttk, PhotoImage, Label
from PIL import Image, ImageTk
import re
import json
import os
import pdfplumber
import graphviz


#==================================================================================================
# User Defined Functions and Setup

# Checking if the previous file for new classes exists
global data3

try:
    with open("current_classes.json", "r") as file3:
        data3 = json.load(file3)
except FileNotFoundError:
    data3 = []

# Function that refreshes UI (checking if the transcript JSON file exists)
def refresh_ui():
    
    file_exists = os.path.exists("classes_with_grades.json")
    
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button) and widget["text"] in options:
            widget.config(state=tk.NORMAL if file_exists else tk.DISABLED)

    root.after(3000, refresh_ui)  # Check again every 3 seconds

# Opens windows for each selected option (only finished options implemented at the moment)
def show_selection(option):
    selection_label.config(text=f"Previous Selection: {option}")
    if option == "Transcript Parser":
        progress_window = tk.Toplevel(root)
        progress_window.title("Transcript Parser")
        app = FileUploader(progress_window)

    elif option == "Help":
        progress_window = tk.Toplevel(root)
        progress_window.title("Help")
        app = HelpPage(progress_window)

    elif option == "Planning Tools":
        progress_window = tk.Toplevel(root)
        progress_window.title("Planning Tools")
        app = Sch_Maker(progress_window)

    elif option == "Progress Tracking":
        progress_window = tk.Toplevel(root)
        progress_window.title("Progress Tracking")
        app = Progress(progress_window)

    elif option == "Pre-Advising Checklist":
        progress_window = tk.Toplevel(root)
        progress_window.title("Pre-Advising Checklist")
        app = Pre_Advising(progress_window)

    elif option == "Flowchart Maker":
        app = Flowchart_Generator()

    elif option == "Close":
        progress_window = tk.Toplevel(root)
        progress_window.title("Help")
        root.destroy()

# Grade and class extractor from the PDF file

def extract_classes_and_grades(pdf_path):

    class_pattern = re.compile(r'\b[A-Z]{3,4}\s?\d{4}[A-Z]?\b')
    term_pattern = re.compile(r'(Spring|Summer|Fall)\s20\d{2}')
    valid_grades = {"A", "A-", "A+", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F", "S", "U", "W", "IP"}

    extracted_data = {}
    current_term = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')
            for line in lines:
                # Check for term updates
                term_match = term_pattern.search(line)
                if term_match:
                    current_term = term_match.group()

                # Look for course code
                course_match = class_pattern.search(line)
                if course_match:
                    course_code = course_match.group()
                    tokens = line.split()

                    # Try to find grade in tokens after course code
                    try:
                        idx = tokens.index(course_code.split()[0])  # E.g., "MAC" in "MAC 2281"
                        grade = None
                        for token in tokens[idx+1:]:
                            if token in valid_grades:
                                grade = token
                                break
                        if grade:
                            extracted_data[course_code] = {
                                "grade": grade,
                                "term": current_term or "Unknown"
                            }
                    except ValueError:
                        continue

    if not extracted_data:
        print("⚠️ No classes or grades extracted.")
    else:
        print("✅ Transcript parsing complete.")


    return extracted_data, passed, failed, inprog

# Reads Json file and outputs lists from the data
def Read_Json_Grades(JSON_data): 
    passed, failed, inprog = [], [], []
    for k, s in JSON_data.items():
        if s['grade'] in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "S"]:
            passed.append(k)
        elif s['grade'] == "IP":
            inprog.append(k)
        else:
            failed.append(k)
    return passed, failed, inprog

data, passed, failed, inprog = {}, [], [], []  # Initialize empty Variables

#==================================================================================================
# Class FLowchart Generator
class Flowchart_Generator:
    def __init__(self):
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
        messagebox.showinfo("Operation Succesful", "✅ Flowchart saved as transcript_semester_flowchart.png")

#==================================================================================================
# Class for progress checker
class Progress:
    def __init__(self, root):
        self.root = root
        root.title("Progress Checker")
        root.geometry("700x700")

        # Title Label
        self.title_label = tk.Label(root, text="Current Progress Until Now", font=("Arial", 14, "bold"), wraplength=600)
        self.title_label.pack(pady=10)

        # Create a frame for the scrollable canvas
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Enable scrolling with the mouse wheel
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows & Mac
        self.canvas.bind_all("<Button-4>", lambda event: self.canvas.yview_scroll(-1, "units"))  # Linux Scroll Up
        self.canvas.bind_all("<Button-5>", lambda event: self.canvas.yview_scroll(1, "units"))  # Linux Scroll Down

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Import and display previous classes
        creds = 0

        with open("curriculum_full.json", "r") as file:
            data = json.load(file)  # Load JSON data
        
        with open("classes_with_grades.json", "r") as file2:
            datat = json.load(file2)
        
        passed, failed, inprog = Read_Json_Grades(datat) 
        courses_data = data.get("courses", {})

        course_label = tk.Label(self.scrollable_frame, text="Passed Classes:", font=("Arial", 12, "bold"))
        course_label.pack(pady=2, anchor="center")

        # Printing Passed classes by order taken
        for course_code in passed:
            course_info = courses_data.get(course_code)
            if course_info is None:
                course_info = {'name': 'N/A', 'credits': 3}
            course_label = tk.Label(self.scrollable_frame, text=f"Code: {course_code}       Name: {course_info['name']}\nGrade:  {datat[course_code]['grade']}       Term: {datat[course_code]['term']} \n\n")
            course_label.pack(pady=2, anchor="center")
            creds += int(course_info['credits'])

        if failed:
            course_label = tk.Label(self.scrollable_frame, text="Failed Classes:", font=("Arial", 12, "bold"))
            course_label.pack(pady=2, anchor="center")
            # Printing Failed classes by order taken
            for course_code in failed:
                course_info = courses_data.get(course_code)
                if course_info is None:
                    course_info = {'name': 'N/A', 'credits': 0}
                course_label = tk.Label(self.scrollable_frame, text=f"Code: {course_code}       Name: {course_info['name']}\nGrade:  {datat[course_code]['grade']}       Term: {datat[course_code]['term']} \n\n")
                course_label.pack(pady=2, anchor="center")
                creds += int(course_info['credits'])
        
        course_label = tk.Label(self.scrollable_frame, text="In Progress Classes:", font=("Arial", 12, "bold"))
        course_label.pack(pady=2, anchor="center")

        # Printing IP classes by order taken
        for course_code in inprog:
            course_info = courses_data.get(course_code)
            if course_info is None:
                course_info = {'name': 'N/A', 'credits': 0}
            course_label = tk.Label(self.scrollable_frame, text=f"Code: {course_code}       Name: {course_info['name']}\nGrade:  {datat[course_code]['grade']}       Term: {datat[course_code]['term']} \n\n")
            course_label.pack(pady=2, anchor="center")
            creds += int(course_info['credits'])

        self.total_credits = tk.Label(root, text=f"The Total Credits Applied: {creds}", font=("Arial", 14, "bold"), wraplength=600)
        self.total_credits.pack(pady=10)

        # Back Button
        self.ok_button = tk.Button(root, text="Back", command=self.confirm_selection, font=("Arial", 14), width=4, height=1)
        self.ok_button.pack(pady=20)
    
    def confirm_selection(self):
        self.root.destroy()

#==================================================================================================
# Class for schedule maker
class Sch_Maker:
    def __init__(self, root):
        self.root = root
        root.title("Schedule Selector")
        root.geometry("300x250")

        # Title Label
        self.title_label = tk.Label(root, text="Schedule Selection", font=("Arial", 14, "bold"), wraplength=600)
        self.title_label.pack(pady=10)

        # Button to add classes
        self.add = tk.Button(root, text="Add Class", font=("Arial", 12), command=self.add_class)
        self.add.pack(pady=5)

        # Button to remove classes
        self.remove = tk.Button(root, text="Remove Class", font=("Arial", 12), command=self.remove_class)
        self.remove.pack(pady=5)

        # Button to check classes
        self.check = tk.Button(root, text="Check Class", font=("Arial", 12), command=self.inspect_schedule)
        self.check.pack(pady=5)

        # Back Button
        self.ok_button = tk.Button(root, text="Back", command=self.confirm_selection, font=("Arial", 14), width=4, height=1)
        self.ok_button.pack(pady=20)

        # Call the function to check for file existence
        self.check_file_existence()

    def check_file_existence(self):
        file_exists = os.path.exists("current_classes.json")
        
        # Enable or disable buttons based on file existence
        self.remove.config(state=tk.NORMAL if file_exists else tk.DISABLED)
        self.check.config(state=tk.NORMAL if file_exists else tk.DISABLED)

        # Re-run this function every 1000 milliseconds (1 second)
        self.root.after(1000, self.check_file_existence)

    def add_class(self):
        # Create a new window
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Classes")
        add_window.geometry("600x600")

        # Create a frame for the scrollbar
        frame = tk.Frame(add_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas inside the frame
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create another frame inside the canvas
        scrollable_frame = tk.Frame(canvas)

        # Update scroll region when the frame changes
        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scrollregion)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)  # Ensures better centering

        # Enable scrolling with the mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows & Mac
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))  # Linux Scroll Up
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))  # Linux Scroll Down

        # Wrapper Frame (Centers Content)
        content_frame = tk.Frame(scrollable_frame)
        content_frame.pack(pady=10, anchor="center")

        # Label inside new window
        label = tk.Label(content_frame, text="Choose your course:", font=("Arial", 14, "bold"))
        label.pack(pady=10, padx=20)  # Centered with padding

        # Upper Level Checker
        self.upper_level_var = tk.BooleanVar()  
        self.check_button = tk.Checkbutton(content_frame, text="Check if upper level", variable=self.upper_level_var, font=("Arial", 10), wraplength=500)
        self.check_button.pack(pady=5, padx=20)

        # Submit to start process
        self.forward = tk.Button(
            content_frame, text="Confirm", font=("Arial", 10), 
            command=lambda: self.upper(add_window, content_frame, canvas) if self.upper_level_var.get() else self.lower(add_window, content_frame, canvas)
        )
        self.forward.pack(pady=5, padx=20)

        # Back Button
        self.back_button = tk.Button(content_frame, text="Back", command=lambda: self.confirm_selection2(add_window), font=("Arial", 14), width=4, height=1)
        self.back_button.pack(pady=20, padx=20)

        update_scrollregion()  # Ensure the initial scrollregion is set

    def upper(self, window, frame, canvas):
        self.forward.destroy()
        self.check_button.destroy()

        with open("curriculum_full.json", "r") as file:
            data = json.load(file)

        with open("classes_with_grades.json", "r") as file2:
            datat = json.load(file2)

        passed, failed, inprog = Read_Json_Grades(datat)
        courses_data = data.get("courses", {})

        self.allbutton = tk.Button(frame, text="Show all", font=("Arial",12, "bold"), 
                              command=lambda: self.all_in_H(courses_data, frame))
        self.allbutton.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        self.recommended = tk.Button(frame, text="Show recommended", font=("Arial",12, "bold"), 
                                command=lambda: self.rec_high(courses_data, passed, inprog, frame))
        self.recommended.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def lower(self, window, frame, canvas):
        self.forward.destroy()
        self.check_button.destroy()

        with open("curriculum_full.json", "r") as file:
            data = json.load(file)

        with open("classes_with_grades.json", "r") as file2:
            datat = json.load(file2)

        passed, failed, inprog = Read_Json_Grades(datat)
        courses_data = data.get("courses", {})

        self.allbutton = tk.Button(frame, text="Show all", font=("Arial",12, "bold"), 
                              command=lambda: self.all_in_L(courses_data, frame))
        self.allbutton.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        self.recommended = tk.Button(frame, text="Show recommended", font=("Arial",12, "bold"), 
                                command=lambda: self.rec_low(courses_data, passed, inprog, frame))
        self.recommended.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Function for recommended classes (low)
    def rec_low(self, courses_data, passed, inprog, frame):
        self.recommended.destroy()
        self.allbutton.destroy()

        # Creating Buttons for recommended classes
        for course_code, course_info in courses_data.items():
            if (course_code not in passed 
                and course_code not in inprog
                #and course_info['prerequisites'] in (passed or inprog) # Based on how everything is built in the dataset (and school), it cannot be implemented because it wont show classes.
                and course_info.get('alternative') not in (passed or inprog)
                and course_info['type'] == "required"):
                btn = tk.Button(frame, text=f"{course_code}: {course_info['name']}", font=("Arial", 10), 
                                command=lambda opt=course_code: data3.append(opt) if opt not in data3 else print("Already used"))
                btn.pack(pady=5, padx=20, fill=tk.X, before=self.back_button)

        save = tk.Button(frame, text="Save", font=("Arial",12, "bold"), command=lambda: self.save(data3))
        save.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        text = tk.Label(frame, text="To update changes close and open the schedule maker!", font=("Arial",8))
        text.pack(pady=5, padx=5, fill=tk.X, before=self.back_button)

    # Function for recommended classes (High)
    def rec_high(self, courses_data, passed, inprog, frame):
        self.recommended.destroy()
        self.allbutton.destroy()

        def show_recommendations(course_type):

            # Destroy previous buttons
            self.check_core.destroy()
            self.check_track.destroy()
            self.check_tech.destroy()

            titles = {
                "core": "Showing recommended cores",
                "track": "Showing recommended Tracks",
                "tech": "Showing recommended Tech. Elect."
            }

            self.title_2 = tk.Label(frame, text=titles[course_type], font=("Arial", 10, "bold"))
            self.title_2.pack(pady=5, padx=20, before=self.back_button)

            for course_code, course_info in courses_data.items():
                if (course_code not in passed and 
                    course_code not in inprog and 
                    #course_info['prerequisites'] in (passed or inprog) and #  # Based on how everything is built in the dataset (and school), it cannot be implemented because it wont show classes.
                    course_type in course_info["type"]):
                    btn = tk.Button(frame, text=f"{course_code}: {course_info['name']}", font=("Arial", 10),
                                    command=lambda opt=course_code: data3.append(opt) if opt not in data3 else print("Already used"))
                    btn.pack(pady=5, padx=20, fill=tk.X, before=self.back_button)

            save = tk.Button(frame, text="Save", font=("Arial", 12, "bold"), command=lambda: self.save(data3))
            save.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

            text = tk.Label(frame, text="To update changes close and open the schedule maker!", font=("Arial", 8))
            text.pack(pady=5, padx=5, fill=tk.X, before=self.back_button)

        # Create type selector buttons
        self.check_core = tk.Button(frame, text="Check to see recommended Cores",
                                    command=lambda: show_recommendations("core"),
                                    font=("Arial", 10), wraplength=500)
        self.check_core.pack(pady=5, padx=20, before=self.back_button)

        self.check_track = tk.Button(frame, text="Check to see recommended Tracks",
                                    command=lambda: show_recommendations("track"),
                                    font=("Arial", 10), wraplength=500)
        self.check_track.pack(pady=5, padx=20, before=self.back_button)

        self.check_tech = tk.Button(frame, text="Check to see recommended Tech. Elect.",
                                    command=lambda: show_recommendations("tech"),
                                    font=("Arial", 10), wraplength=500)
        self.check_tech.pack(pady=5, padx=20, before=self.back_button)



    # Create all classes buttons
    def all_in_L(self, courses_data, frame):
        self.recommended.destroy()
        self.allbutton.destroy()
        
        for course_code, course_info in courses_data.items():
            btn = tk.Button(frame, text=f"{course_code}: {course_info['name']}", font=("Arial", 10), 
                                command=lambda opt=course_code: data3.append(opt) if opt not in data3 else print("Already used"))
            btn.pack(pady=5, padx=20, fill=tk.X, before=self.back_button)

        save = tk.Button(frame, text="Save", font=("Arial",12, "bold"), command=lambda: self.save(data3))
        save.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        text = tk.Label(frame, text="To update changes close and open the schedule maker!", font=("Arial",8))
        text.pack(pady=5, padx=5, fill=tk.X, before=self.back_button)


    def all_in_H(self, courses_data, frame):
        self.recommended.destroy()
        self.allbutton.destroy()

        for course_code, course_info in courses_data.items():
            btn = tk.Button(frame, text=f"{course_code}: {course_info['name']}", font=("Arial", 10), 
                                command=lambda opt=course_code: data3.append(opt) if opt not in data3 else print("Already used"))
            btn.pack(pady=5, padx=20, fill=tk.X, before=self.back_button)

        save = tk.Button(frame, text="Save", font=("Arial",12, "bold"), command=lambda: self.save(data3))
        save.pack(pady=5, padx=30, fill=tk.X, before=self.back_button)

        text = tk.Label(frame, text="To update changes close and open the schedule maker!", font=("Arial",8))
        text.pack(pady=5, padx=5, fill=tk.X, before=self.back_button)


    def remove_class(self):
        # Create a new window
        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove Classes")
        remove_window.geometry("600x600")

        # Label inside new window
        label = tk.Label(remove_window, text="Choose a course to remove:", font=("Arial", 14, "bold"))
        label.pack(pady=10)

        with open("curriculum_full.json", "r") as file:
            data = json.load(file)
        
        courses_data = data.get("courses", {})
        
        with open("current_classes.json", "r") as file:
            data3 = json.load(file)

        for course_code, course_info in courses_data.items():
            if course_code in data3:
                classes = tk.Button(remove_window, text=f"{course_code}: {course_info['name']}", font=("Arial", 12), command=lambda opt=course_code: data3.remove(opt))
                classes.pack(pady=5, padx=20, fill=tk.X)
        
        # Save Button
        save = tk.Button(remove_window, text="Save", font=("Arial",12, "bold"), command=lambda: self.save(data3))
        save.pack(pady=5, padx=30, fill=tk.X)

        # Back Button
        self.back_button = tk.Button(remove_window, text="Back", command=lambda: self.confirm_selection2(remove_window), font=("Arial", 14), width=4, height=1)
        self.back_button.pack(pady=20)

    def inspect_schedule(self):
        # Create a new window
        inspect = tk.Toplevel(self.root)
        inspect.title("Inspect Schedule")
        inspect.geometry("600x600")

        # Label for currently selected classes
        self.label = tk.Label(inspect, text="Currently selected classes:", font=("Arial", 12, "bold"))
        self.label.pack(pady=5)

        with open("curriculum_full.json", "r") as file:
            data = json.load(file)
        
        courses_data = data.get("courses", {})
        
        with open("current_classes.json", "r") as file:
            data3 = json.load(file)
        
        c = 0  # Total credits

        for course_code, course_info in courses_data.items():
            if course_code in data3:
                classes = tk.Label(inspect, text=f"{course_code}: {course_info['name']}", font=("Arial", 12))
                classes.pack(pady=5)
                c += int(course_info['credits'])

        # Total credits label
        label = tk.Label(inspect, text=f"Total Credits:  {c}", font=("Arial", 12, "bold"))
        label.pack(pady=5)

        # Back Button
        self.back_button = tk.Button(inspect, text="Back", command=lambda: self.confirm_selection2(inspect), font=("Arial", 14, "bold"), width=4, height=1)
        self.back_button.pack(pady=20)

    # User defined functions
    def confirm_selection(self):
        self.root.destroy()

    def confirm_selection2(self, window):
        window.destroy()

    def save(self, data):
        # Save to JSON file
        with open("current_classes.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
        

#==================================================================================================
# Class for pre-advising checklist
class Pre_Advising:
    def __init__(self, root):
        self.root = root
        root.title("Pre-Advising Checklist")
        root.geometry("600x600")

        # Initialize saved data dictionary
        self.saved_data = self.load_saved_data()

        # Title Label
        self.title_label = tk.Label(root, text="Pre-Advising Checklist", font=("Arial", 14, "bold"), wraplength=600)
        self.title_label.pack(pady=10)

        # Description Label
        self.desc_label = tk.Label(root, text="Check carefully before setting up an appointment", font=("Arial", 10), wraplength=600)
        self.desc_label.pack(pady=5)

        # Upper Level Checkbox
        self.upper_level_var = tk.BooleanVar()  
        self.check_button = tk.Checkbutton(root, text="Check if upper level", variable=self.upper_level_var, font=("Arial", 10), wraplength=600, command=self.toggle)
        self.check_button.pack(pady=5)

        # Back Button
        self.ok_button = tk.Button(root, text="Save and Exit", command=self.confirm_selection, font=("Arial", 14, "bold"), width=20, height=2)
        self.ok_button.pack(pady=20)

        # Initialize default lower-level widgets
        self.create_lower_widgets()
    
    # Loads saved data from JSON file, handling errors
    def load_saved_data(self):
        if os.path.exists("appointment_data.json"):
            try:
                with open("appointment_data.json", "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return {}  # Return empty dictionary if file is corrupted
        return {}  # Return empty dictionary if file does not exist
    
    # Creates and populates lower-level widgets with saved data.
    def create_lower_widgets(self):
        self.lowl = tk.Label(self.root, text="Enter Phone Number:", font=("Arial", 10), wraplength=600)
        self.lowl.pack(pady=5, before=self.ok_button)
        self.lowlen = tk.Entry(self.root, width=30)
        self.lowlen.pack(pady=5, before=self.ok_button)
        self.lowlen.insert(0, self.saved_data.get("Phone Number", ""))

        self.campusl = tk.Label(self.root, text="Enter Campus:", font=("Arial", 10), wraplength=600)
        self.campusl.pack(pady=5, before=self.ok_button)
        self.campus = tk.Entry(self.root, width=30)
        self.campus.pack(pady=5, before=self.ok_button)
        self.campus.insert(0, self.saved_data.get("Campus", ""))

        self.collegel = tk.Label(self.root, text="Enter College (Ex. Engineering):", font=("Arial", 10), wraplength=600)
        self.collegel.pack(pady=5, before=self.ok_button)
        self.college = tk.Entry(self.root, width=30)
        self.college.pack(pady=5, before=self.ok_button)
        self.college.insert(0, self.saved_data.get("College", ""))

        self.majorl = tk.Label(self.root, text="Enter Major (Ex. Electrical Engineering):", font=("Arial", 10), wraplength=600)
        self.majorl.pack(pady=5, before=self.ok_button)
        self.major = tk.Entry(self.root, width=30)
        self.major.pack(pady=5, before=self.ok_button)
        self.major.insert(0, self.saved_data.get("Major", ""))

        self.reasonl = tk.Label(self.root, text="Enter reason for appointment (Be concise and specific):", font=("Arial", 10), wraplength=600)
        self.reasonl.pack(pady=5, before=self.ok_button)
        self.reason = tk.Text(self.root, width=30, height=4)
        self.reason.pack(pady=5, before=self.ok_button)
        if self.saved_data.get("Level") == "Lower":
            self.reason.insert("1.0", self.saved_data.get("Reason", ""))

        self.linklow = tk.Label(self.root, text="Click here when ready to schedule an appointment", font=("Arial", 10, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.linklow.pack(pady=5, before=self.ok_button)
        self.linklow.bind("<Button-1>", self.lowlin)

        self.rembrd = tk.Label(self.root, text="Remember to decide if you will do a drop-in appointment or schedule one for later.", font=("Arial", 10, "bold"), wraplength=600)
        self.rembrd.pack(pady=5, before=self.ok_button)
    
    #Toggles between upper and lower level UI elements
    def toggle(self):
        if self.upper_level_var.get():  # Upper Level Selected
            for widget in [self.lowl, self.lowlen, self.campusl, self.campus, self.collegel, self.college,
                           self.majorl, self.major, self.reasonl, self.reason, self.linklow, self.rembrd]:
                if widget:
                    widget.destroy()

            self.extra_button = tk.Checkbutton(self.root, text="Is this your first meeting?", font=("Arial", 12))
            self.extra_button.pack(pady=5, before=self.ok_button)

            self.name_label = tk.Label(self.root, text="Enter Name:", font=("Arial", 10))
            self.name_label.pack(before=self.ok_button)
            self.name_entry = tk.Entry(self.root, width=30)
            self.name_entry.pack(pady=5, before=self.ok_button)
            self.name_entry.insert(0, self.saved_data.get("Name", ""))

            self.email_label = tk.Label(self.root, text="Enter Email:", font=("Arial", 10))
            self.email_label.pack(before=self.ok_button)
            self.email_entry = tk.Entry(self.root, width=30)
            self.email_entry.pack(pady=5, before=self.ok_button)
            self.email_entry.insert(0, self.saved_data.get("Email", ""))

            self.uid_label = tk.Label(self.root, text="Enter UID:", font=("Arial", 10))
            self.uid_label.pack(before=self.ok_button)
            self.uid_entry = tk.Entry(self.root, width=30)
            self.uid_entry.pack(pady=5, before=self.ok_button)
            self.uid_entry.insert(0, self.saved_data.get("UID", ""))

            self.reason_label = tk.Label(self.root, text="Reason for Meeting (be concise and specific):", font=("Arial", 10))
            self.reason_label.pack(before=self.ok_button)
            self.reason_entry = tk.Text(self.root, width=30, height=4)
            self.reason_entry.pack(pady=5, before=self.ok_button)
            if self.saved_data.get("Level") == "Upper":
                self.reason_entry.insert("1.0", self.saved_data.get("Reason", ""))

            self.linkup = tk.Label(self.root, text="Click here when ready to schedule an appointment", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
            self.linkup.pack(pady=5, before=self.ok_button)
            self.linkup.bind("<Button-1>", self.upplin)

            self.rembr = tk.Label(self.root, text="Remember to copy all information!", font=("Arial", 10, "bold"), wraplength=600)
            self.rembr.pack(pady=5, before=self.ok_button)
        else:
            for widget in [self.extra_button, self.name_label, self.name_entry, self.email_label, self.email_entry,
                        self.uid_label, self.uid_entry, self.reason_label, self.reason_entry, self.linkup, self.rembr]:
                if widget:
                    widget.destroy()

            self.create_lower_widgets()

    def lowlin(self, event):
        wb.open("https://usf.appiancloud.com/suite/sites/archivum/page/archivum/report/M_NuSA.com")

    def upplin(self, event):
        wb.open("https://usflearn.instructure.com/courses/923318/wiki")

    # Saves the information on a json file and closes the window
    def confirm_selection(self):
        data = {}

        if self.upper_level_var.get():
            data["Level"] = "Upper"
            data["Name"] = self.name_entry.get() if self.name_entry else ""
            data["Email"] = self.email_entry.get() if self.email_entry else ""
            data["UID"] = self.uid_entry.get() if self.uid_entry else ""
            data["Reason"] = self.reason_entry.get("1.0", "end").strip() if self.reason_entry else ""
        else:
            data["Level"] = "Lower"
            data["Phone Number"] = self.lowlen.get() if self.lowlen else ""
            data["Campus"] = self.campus.get() if self.campus else ""
            data["College"] = self.college.get() if self.college else ""
            data["Major"] = self.major.get() if self.major else ""
            data["Reason"] = self.reason.get("1.0", "end").strip() if self.reason else ""
        
        with open("appointment_data.json", "w") as file:
            json.dump(data, file, indent=4)
        
        self.root.destroy()

#==================================================================================================
# Class for help page
class HelpPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Help Resources")
        self.root.geometry("600x500")
        
        # Title and subtitle
        self.label = tk.Label(root, text="Help Resources and Communication Channels:", font=("Arial", 14, "bold"), wraplength=600)
        self.label.pack(pady=20)
        self.label = tk.Label(root, text="Click Hyperlinks below for more information", font=("Arial", 10), wraplength=600)
        self.label.pack(pady=10)

        #Hyperlink text buttons
        self.label2 = tk.Label(root, text="Where is the latest catalog?", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label2.pack(pady=10)
        self.label2.bind("<Button-1>", self.cataloglat)

        self.label3 = tk.Label(root, text="Who are the career advisors?", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label3.pack(pady=10)
        self.label3.bind("<Button-1>", self.adviswho)

        self.label4 = tk.Label(root, text="How to find a historical list of courses:", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label4.pack(pady=10)
        self.label4.bind("<Button-1>", self.histlist)

        self.label5 = tk.Label(root, text="How to find which technical elective course is offered when?", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label5.pack(pady=10)
        self.label5.bind("<Button-1>", self.techele)

        self.label6 = tk.Label(root, text="What's the current academic plan document the advising office is using?", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label6.pack(pady=10)
        self.label6.bind("<Button-1>", self.curacapla)

        self.label7 = tk.Label(root, text="EE Curriculum Registration Advising Info Session Presentation", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label7.pack(pady=10)
        self.label7.bind("<Button-1>", self.tellmore)

        self.label8 = tk.Label(root, text="EE Curriculum Registration Advising Info Session", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.label8.pack(pady=10)
        self.label8.bind("<Button-1>", self.comyout)

        self.ok_button = tk.Button(root, text="Back", command=self.confirm_selection, font=("Arial", 14), width=4, height=1)
        self.ok_button.pack(pady=20)

    # Hyperlinks for resources
    def cataloglat(self, event):
        wb.open("https://catalog.usf.edu/preview_program.php?catoid=21&poid=10332")

    def adviswho(self, event):
        wb.open("https://www.usf.edu/engineering/ee/undergraduate/career-advisors.aspx")

    def histlist(self, event):
        wb.open("https://www.usf.edu/engineering/ee/documents/class-shedule-archive-10022024.pdf")
    
    def techele(self, event):
        wb.open("https://www.usf.edu/engineering/ee/documents/select-track-2024.pdf")

    def curacapla(self, event):
        wb.open("https://usf.app.box.com/s/or47mx7cvod6mkshv8h9ttmip6l2n2c2")

    def tellmore(self, event):
        wb.open("https://usf.app.box.com/s/o5mlndoxnpbdvu35tnuk98xqw1texsaz")

    def comyout(self, event):
        wb.open("https://www.youtube.com/watch?v=SJyj8-PGj8g")

    def confirm_selection(self):
        self.root.destroy()


#==================================================================================================
# Class for page to upload pdf to create JSON file
class FileUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcript Upload")
        self.root.geometry("450x250")

        # Checkbox to use previous data
        self.use_previous_data = tk.BooleanVar(value=bool(data))  # Default to True if data exists
        self.checkbox = tk.Checkbutton(root, text="Use previous data", variable=self.use_previous_data, command=self.toggle_file_selection, state=tk.NORMAL if os.path.exists("classes_with_grades.json") else tk.DISABLED)
        self.checkbox.pack(pady=10)

        # Upload button
        self.upload_button = tk.Button(root, text="Upload Transcripts", command=self.upload_transcripts, state=tk.DISABLED if data else tk.NORMAL)
        self.upload_button.pack(pady=10)

        # Label to display selected file
        self.label = tk.Label(root, text="Using previous data" if data else "No file selected", wraplength=400)
        self.label.pack(pady=10)

        # OK button
        self.ok_button = tk.Button(root, text="OK", command=self.confirm_selection, state=tk.NORMAL if data else tk.DISABLED)
        self.ok_button.pack(pady=20)

        self.selected_file = None  # Store file path
        
# Enable/Disable file selection based on checkbox state.
    def toggle_file_selection(self):
        
        if self.use_previous_data.get():
            self.upload_button.config(state=tk.DISABLED)
            self.label.config(text="Using previous data")
            self.ok_button.config(state=tk.NORMAL)  # Enable OK button if using previous data
        else:
            self.upload_button.config(state=tk.NORMAL)
            self.label.config(text="No file selected")
            self.ok_button.config(state=tk.DISABLED)  # Disable until a file is uploaded

# Handle file selection and process transcript.
    def upload_transcripts(self):
        
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.label.config(text=f"Selected File: {os.path.basename(file_path)}")
            self.ok_button.config(state=tk.NORMAL)  # Enable OK button

# Process either the selected file or cached data and close the UI.
    def confirm_selection(self):
        
        global data, passed, failed, inprog

        if self.use_previous_data.get() and os.path.exists("classes_with_grades.json"):
            messagebox.showinfo("Info", "Using previous data from cache.")
            with open("classes_with_grades.json", "r") as file:
                data = json.load(file)  # Load JSON data
            passed, failed, inprog = Read_Json_Grades(data)

        elif self.selected_file:
            # Extract data from the PDF
            data, passed, failed, inprog = extract_classes_and_grades(self.selected_file)

            # Save to JSON file
            with open("classes_with_grades.json", "w") as json_file:
                json.dump(data, json_file, indent=4)

            messagebox.showinfo("Success", "Transcript processed and saved for future reference")

        else:
            messagebox.showwarning("Warning", "No cache file exists!")
            return  # Prevent closing if no file is selected

        # Close the Tkinter window after confirmation
        self.root.destroy()

#==================================================================================================
# Root Page Code

root = tk.Tk()
root.title("Electrical Engineering Course Planning Tool")
root.geometry("500x500")

# Load and resize the image to match the window size
bg_image = Image.open("RootPic.png").resize((400, 400))  # Resize to fit the window
rp = ImageTk.PhotoImage(bg_image)

# Create a background label
label1 = Label(root, image=rp)
label1.place(x=0, y=0, relwidth=1, relheight=1)  # Cover full window

title_label = tk.Label(root, text="Select a Feature", font=("Arial", 14, "bold")) #Titles and subtitles
title_label.pack(pady=10)

title_label = tk.Label(root, text="Parse your transcripts before using tools", font=("Arial", 10))
title_label.pack(pady=10)

btn = tk.Button(root, text="Transcript Parser", font=("Arial", 12), command=lambda opt="Transcript Parser": show_selection(opt)) #Buttons to select feature
btn.pack(pady=5, fill=tk.X, padx=20)

options = ["Progress Tracking", "Planning Tools", "Flowchart Maker", "Pre-Advising Checklist"]
for option in options:
    btn = tk.Button(root, text=option, font=("Arial", 12), state=tk.NORMAL if os.path.exists("classes_with_grades.json") else tk.DISABLED, command=lambda opt=option: show_selection(opt))
    btn.pack(pady=5, fill=tk.X, padx=20)

btn = tk.Button(root, text="Help", font=("Arial", 12), command=lambda opt="Help": show_selection(opt))
btn.pack(pady=5, fill=tk.X, padx=20)

btn = tk.Button(root, text="Close", font=("Arial", 12, "bold"), command=lambda opt="Close": show_selection(opt))
btn.pack(pady=5, fill=tk.X, padx=20)

selection_label = tk.Label(root, text="Previous Selection: ...", font=("Arial", 12)) #Display of previously selected feature
selection_label.pack(pady=10)


refresh_ui()
root.mainloop()