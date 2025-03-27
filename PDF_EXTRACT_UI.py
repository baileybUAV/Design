import re
import json
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Function to extract classes taken with their assigned letter grade
def extract_classes_and_grades(pdf_path):
    """Extracts course names and grades from a transcript PDF."""
    class_pattern = re.compile(r'\b[A-Z]{3}\s?\d{4}[A-Z]?\b')  # Course code pattern
    grade_pattern = re.compile(r'\b(?:[A-F]|S|W|IP)\b')  # Grade pattern

    passed, failed, inprog = [], [], []
    extracted_data = {}

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

    for k, s in extracted_data.items():
        if s in ["A", "B", "C", "S"]:
            passed.append(k)
        elif s == "IP":
            inprog.append(k)
        else:
            failed.append(k)

    return extracted_data, passed, failed, inprog

# Function to read cached JSON file of transcript
def Read_Json_Grades(JSON_data):
    """Reads a JSON file and extracts passed, failed, and in-progress courses."""
    passed, failed, inprog = [], [], []

    for k, s in JSON_data.items():
        if s in ["A", "B", "C", "S"]:
            passed.append(k)
        elif s == "IP":
            inprog.append(k)
        else:
            failed.append(k)

    return passed, failed, inprog

# Check if previous data exists in cache
if os.path.exists("classes_with_grades.json"):
    with open("classes_with_grades.json", "r") as file:
        data = json.load(file)  # Load JSON data
    passed, failed, inprog = Read_Json_Grades(data)
else:
    data, passed, failed, inprog = {}, [], [], []  # Initialize empty values

# ----------------------------------------------------------------------------------------------
# Tkinter UI Section
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

    def toggle_file_selection(self):
        """Enable/Disable file selection based on checkbox state."""
        if self.use_previous_data.get():
            self.upload_button.config(state=tk.DISABLED)
            self.label.config(text="Using previous data")
            self.ok_button.config(state=tk.NORMAL)  # Enable OK button if using previous data
        else:
            self.upload_button.config(state=tk.NORMAL)
            self.label.config(text="No file selected")
            self.ok_button.config(state=tk.DISABLED)  # Disable until a file is uploaded

    def upload_transcripts(self):
        """Handle file selection and process transcript."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.label.config(text=f"Selected File: {os.path.basename(file_path)}")
            self.ok_button.config(state=tk.NORMAL)  # Enable OK button

    def confirm_selection(self):
        """Process either the selected file or cached data and close the UI."""
        global data, passed, failed, inprog

        if self.use_previous_data.get():
            messagebox.showinfo("Info", "Using previous data from cache.")
        elif self.selected_file:
            # Extract data from the new PDF
            data, passed, failed, inprog = extract_classes_and_grades(self.selected_file)

            # Save to JSON file
            with open("classes_with_grades.json", "w") as json_file:
                json.dump(data, json_file, indent=4)

            messagebox.showinfo("Success", "Transcript processed and saved.")
        else:
            messagebox.showwarning("Warning", "No file selected!")
            return  # Prevent closing if no file is selected

        # Close the Tkinter window after confirmation
        self.root.destroy()

# Create the main window
root = tk.Tk()
app = FileUploader(root)
root.mainloop()

# FOR TESTING PURPOSES
print("Passed Classes:", passed)
print("Failed Classes:", failed)
print("In Progress:", inprog)