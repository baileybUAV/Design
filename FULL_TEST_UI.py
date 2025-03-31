import tkinter as tk
import webbrowser as wb
from tkinter import messagebox, filedialog
import re
import json
import PyPDF2
import os

#==================================================================================================
#User Defined Functions and Setup

#Function that refreshes UI (checking if the transcript JSON file exists)
def refresh_ui():
    
    file_exists = os.path.exists("classes_with_grades.json")
    
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button) and widget["text"] in options:
            widget.config(state=tk.NORMAL if file_exists else tk.DISABLED)

    root.after(3000, refresh_ui)  # Check again every 3 seconds

#Opens windows for each selected option (only finished options implemented at the moment)
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

    elif option == "Pre-Advising Checklist":
        progress_window = tk.Toplevel(root)
        progress_window.title("Pre-Advising Checklist")
        app = Pre_Advising(progress_window)

    elif option == "Close":
        progress_window = tk.Toplevel(root)
        progress_window.title("Help")
        root.destroy()

#Grade and class extractor from the PDF file
import pdfplumber

def extract_classes_and_grades(pdf_path):
    class_pattern = re.compile(r'\b[A-Z]{3,4}\s?\d{4}[A-Z]?\b')
    grade_pattern = re.compile(r'\b(A|A-|B\+|B|B-|C\+|C|C-|D\+|D|D-|F|S|U|W|IP)\b')

    passed, failed, inprog, extracted_data = [], [], [], {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            classes = class_pattern.findall(text)
            grades = grade_pattern.findall(text)

            print(f"Page {page_num + 1} — Classes found: {classes}")
            print(f"Page {page_num + 1} — Grades found: {grades}")

            for i, course in enumerate(classes):
                grade = grades[i] if i < len(grades) else "N/A"
                extracted_data[course] = grade

    for k, s in extracted_data.items():
        if s in ["A", "A-", "B+", "B", "B-", "C+", "C", "S"]:
            passed.append(k)
        elif s == "IP":
            inprog.append(k)
        else:
            failed.append(k)

    if not extracted_data:
        print("⚠️ Warning: No classes or grades extracted. Check if the transcript is a scanned image.")


    return extracted_data, passed, failed, inprog

#Reads Json file and outputs lists from the data
def Read_Json_Grades(JSON_data): 
    passed, failed, inprog = [], [], []
    for k, s in JSON_data.items():
        if s in ["A", "B", "C", "S"]:
            passed.append(k)
        elif s == "IP":
            inprog.append(k)
        else:
            failed.append(k)
    return passed, failed, inprog

data, passed, failed, inprog = {}, [], [], []

#==================================================================================================
#Class for pre-advising checklist
class Pre_Advising:
    def __init__(self, root):
        self.root = root
        self.root.title("Pre-Advising Checklist")
        self.root.geometry("600x600")

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

        # Default Lower-Level Widgets
        self.lowl = tk.Label(root, text="Enter Phone Number:", font=("Arial", 10), wraplength=600)
        self.lowl.pack(pady=5)
        self.lowlen = tk.Entry(root, width=30)
        self.lowlen.pack(pady=5)

        self.campusl = tk.Label(root, text="Enter Campus:", font=("Arial", 10), wraplength=600)
        self.campusl.pack(pady=5)
        self.campus = tk.Entry(root, width=30)
        self.campus.pack(pady=5)

        self.collegel = tk.Label(root, text="Enter College (Ex. Engineering):", font=("Arial", 10), wraplength=600)
        self.collegel.pack(pady=5)
        self.college = tk.Entry(root, width=30)
        self.college.pack(pady=5)

        self.majorl = tk.Label(root, text="Enter Major (Ex. Electrical Engineering):", font=("Arial", 10), wraplength=600)
        self.majorl.pack(pady=5)
        self.major = tk.Entry(root, width=30)
        self.major.pack(pady=5)

        self.reasonl = tk.Label(root, text="Enter reason for appointment (Be concise and specific):", font=("Arial", 10), wraplength=600)
        self.reasonl.pack(pady=5)
        self.reason = tk.Text(root, width=30, height=4)
        self.reason.pack(pady=5)

        self.linklow = tk.Label(root, text="Click here when ready to schedule an appointment", font=("Arial", 10, "underline"), fg="blue", cursor="hand2", wraplength=600)
        self.linklow.pack(pady=5)
        self.linklow.bind("<Button-1>", self.lowlin)

        self.rembrd = tk.Label(root, text="Remember to decide if you will do a drop-in appointment or schedule one for later.", font=("Arial", 10, "bold"), wraplength=600)
        self.rembrd.pack(pady=5)

        # Initialize upper-level widgets (set to None initially)
        self.extra_button = None
        self.name_label = None
        self.name_entry = None
        self.email_label = None
        self.email_entry = None
        self.uid_label = None
        self.uid_entry = None
        self.reason_label = None
        self.reason_entry = None
        self.linkup = None
        self.rembr = None

        # Back Button
        self.ok_button = tk.Button(root, text="Back", command=self.confirm_selection, font=("Arial", 14), width=4, height=1)
        self.ok_button.pack(pady=20)
    
    def toggle(self):
        if self.upper_level_var.get():  # Upper Level Selected
            # Destroy lower-level widgets
            for widget in [self.lowl, self.lowlen, self.campusl, self.campus, self.collegel, self.college,
                           self.majorl, self.major, self.reasonl, self.reason, self.linklow, self.rembrd]:
                if widget:
                    widget.destroy()

            # Reset lower-level variables
            self.lowl = self.lowlen = self.campusl = self.campus = None
            self.collegel = self.college = self.majorl = self.major = None
            self.reasonl = self.reason = self.linklow = self.rembrd = None

            # Add Upper-Level Widgets **before Back button**
            self.extra_button = tk.Checkbutton(self.root, text="Is this your first meeting?", font=("Arial", 12))
            self.extra_button.pack(pady=5, before=self.ok_button)

            self.name_label = tk.Label(self.root, text="Enter Name:", font=("Arial", 10))
            self.name_label.pack(before=self.ok_button)
            self.name_entry = tk.Entry(self.root, width=30)
            self.name_entry.pack(pady=5, before=self.ok_button)

            self.email_label = tk.Label(self.root, text="Enter Email:", font=("Arial", 10))
            self.email_label.pack(before=self.ok_button)
            self.email_entry = tk.Entry(self.root, width=30)
            self.email_entry.pack(pady=5, before=self.ok_button)

            self.uid_label = tk.Label(self.root, text="Enter UID:", font=("Arial", 10))
            self.uid_label.pack(before=self.ok_button)
            self.uid_entry = tk.Entry(self.root, width=30)
            self.uid_entry.pack(pady=5, before=self.ok_button)

            self.reason_label = tk.Label(self.root, text="Reason for Meeting (be concise and specific):", font=("Arial", 10))
            self.reason_label.pack(before=self.ok_button)
            self.reason_entry = tk.Text(self.root, width=30, height=4)
            self.reason_entry.pack(pady=5, before=self.ok_button)

            self.linkup = tk.Label(self.root, text="Click here when ready to schedule an appointment", font=("Arial", 12, "underline"), fg="blue", cursor="hand2", wraplength=600)
            self.linkup.pack(pady=5, before=self.ok_button)
            self.linkup.bind("<Button-1>", self.upplin)

            self.rembr = tk.Label(self.root, text="Remember to copy all information!", font=("Arial", 10, "bold"), wraplength=600)
            self.rembr.pack(pady=5, before=self.ok_button)

        else:  # Lower Level Selected
            # Destroy upper-level widgets
            for widget in [self.extra_button, self.name_label, self.name_entry, self.email_label, self.email_entry,
                        self.uid_label, self.uid_entry, self.reason_label, self.reason_entry, self.linkup, self.rembr]:
                if widget:
                    widget.destroy()

            # Reset upper-level variables
            self.extra_button = self.name_label = self.name_entry = None
            self.email_label = self.email_entry = self.uid_label = self.uid_entry = None
            self.reason_label = self.reason_entry = self.linkup = self.rembr = None 

            # Restore Default Lower-Level Widgets **before Back button**
            self.lowl = tk.Label(self.root, text="Enter Phone Number:", font=("Arial", 10), wraplength=600)
            self.lowl.pack(pady=5, before=self.ok_button)
            self.lowlen = tk.Entry(self.root, width=30)
            self.lowlen.pack(pady=5, before=self.ok_button)

            self.campusl = tk.Label(self.root, text="Enter Campus:", font=("Arial", 10), wraplength=600)
            self.campusl.pack(pady=5, before=self.ok_button)
            self.campus = tk.Entry(self.root, width=30)
            self.campus.pack(pady=5, before=self.ok_button)

            self.collegel = tk.Label(self.root, text="Enter College (Ex. Engineering):", font=("Arial", 10), wraplength=600)
            self.collegel.pack(pady=5, before=self.ok_button)
            self.college = tk.Entry(self.root, width=30)
            self.college.pack(pady=5, before=self.ok_button)

            self.majorl = tk.Label(self.root, text="Enter Major (Ex. Electrical Engineering):", font=("Arial", 10), wraplength=600)
            self.majorl.pack(pady=5, before=self.ok_button)
            self.major = tk.Entry(self.root, width=30)
            self.major.pack(pady=5, before=self.ok_button)

            self.reasonl = tk.Label(self.root, text="Enter reason for appointment (Be concise and specific):", font=("Arial", 10), wraplength=600)
            self.reasonl.pack(pady=5, before=self.ok_button)
            self.reason = tk.Text(self.root, width=30, height=4)
            self.reason.pack(pady=5, before=self.ok_button)

            self.linklow = tk.Label(self.root, text="Click here when ready to schedule an appointment", font=("Arial", 10, "underline"), fg="blue", cursor="hand2", wraplength=600)
            self.linklow.pack(pady=5, before=self.ok_button)
            self.linklow.bind("<Button-1>", self.lowlin)

            self.rembrd = tk.Label(self.root, text="Remember to decide if you will do a drop-in appointment or schedule one for later.", font=("Arial", 10, "bold"), wraplength=600)
            self.rembrd.pack(pady=5, before=self.ok_button)

    def lowlin(self, event):
        wb.open("https://usf.appiancloud.com/suite/sites/archivum/page/archivum/report/M_NuSA.com")

    def upplin(self, event):
        wb.open("https://usflearn.instructure.com/courses/923318/wiki")

    def confirm_selection(self):
        self.root.destroy()

#==================================================================================================
#Class for help page
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
#Class for page to upload pdf to create JSON file
class FileUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcript Upload")
        self.root.geometry("450x250")

        # Checkbox to use previous data
        self.use_previous_data = tk.BooleanVar(value=bool(data))  # Default to True if data exists
        self.checkbox = tk.Checkbutton(root, text="Use previous data", variable=self.use_previous_data, command=self.toggle_file_selection)
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
#Root Page Code

root = tk.Tk()
root.title("Electrical Engineering Course Planning Tool")
root.geometry("400x500")

title_label = tk.Label(root, text="Select a Feature", font=("Arial", 14, "bold")) #Titles and subtitles
title_label.pack(pady=10)

title_label = tk.Label(root, text="Parse your transcripts before using tools", font=("Arial", 10))
title_label.pack(pady=10)

btn = tk.Button(root, text="Transcript Parser", font=("Arial", 12), command=lambda opt="Transcript Parser": show_selection(opt)) #Buttons to select feature
btn.pack(pady=5, fill=tk.X, padx=20)

options = ["Progress Tracking", "Planning Tools", "Dynamic Checklist Generation", "Pre-Advising Checklist"]
for option in options:
    btn = tk.Button(root, text=option, font=("Arial", 12), state=tk.NORMAL if os.path.exists("classes_with_grades.json") else tk.DISABLED, command=lambda opt=option: show_selection(opt))
    btn.pack(pady=5, fill=tk.X, padx=20)

btn = tk.Button(root, text="Help", font=("Arial", 12), command=lambda opt="Help": show_selection(opt))
btn.pack(pady=5, fill=tk.X, padx=20)

btn = tk.Button(root, text="Close", font=("Arial", 12), command=lambda opt="Close": show_selection(opt))
btn.pack(pady=5, fill=tk.X, padx=20)

selection_label = tk.Label(root, text="Previous Selection: ...", font=("Arial", 12)) #Display of previously selected feature
selection_label.pack(pady=10)


refresh_ui()

root.mainloop()