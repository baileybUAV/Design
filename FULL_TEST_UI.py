import tkinter as tk
import webbrowser as wb
from tkinter import messagebox, filedialog
import re
import json
import PyPDF2
import os

#==================================================================================================
#User Defined Functions

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
    elif option == "Close":
        progress_window = tk.Toplevel(root)
        progress_window.title("Help")
        root.destroy()

#Grade and class extractor from the PDF file
def extract_classes_and_grades(pdf_path):
    class_pattern = re.compile(r'\b[A-Z]{3}\s?\d{4}[A-Z]?\b')
    grade_pattern = re.compile(r'\b(?:[A-F]|S|W|IP)\b')
    passed, failed, inprog, extracted_data = [], [], [], {}
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                classes = class_pattern.findall(text)
                grades = grade_pattern.findall(text)
                for i, course in enumerate(classes):
                    grade = grades[i] if i < len(grades) else "N/A"
                    extracted_data[course] = grade
    for k, s in extracted_data.items(): #List maker
        if s in ["A", "B", "C", "S"]:
            passed.append(k)
        elif s == "IP":
            inprog.append(k)
        else:
            failed.append(k)
    return extracted_data

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
class HelpPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Help Resources")
        self.root.geometry("600x500")
        
        self.label = tk.Label(root, text="Help Resources and Communication Channels:", font=("Arial", 14, "bold"), wraplength=600)
        self.label.pack(pady=20)
        self.label = tk.Label(root, text="Click Hyperlinks below for more information", font=("Arial", 10), wraplength=600)
        self.label.pack(pady=20)

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
class FileUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcript Parser")
        self.root.geometry("300x200")

        self.upload_button = tk.Button(root, text="Upload Transcripts", command=self.upload_transcripts, state=tk.DISABLED if data else tk.NORMAL)
        self.upload_button.pack(pady=20)
        self.label = tk.Label(root, text="No file selected", wraplength=400)
        self.label.pack(pady=20)
        self.ok_button = tk.Button(root, text="OK", command=self.confirm_selection)
        self.ok_button.pack(pady=20)
        self.selected_file = None

    def upload_transcripts(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.label.config(text=f"Selected File: {os.path.basename(file_path)}")
            self.ok_button.config(state=tk.NORMAL)

    def confirm_selection(self):
        global data, passed, failed, inprog

        if self.selected_file:
            data = extract_classes_and_grades(self.selected_file)
            with open("classes_with_grades.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
            messagebox.showinfo("Success", "Transcript processed and saved for future reference")

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