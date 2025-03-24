#==========================================================================
#PDF CODE TO BE FUSED
import re
import json
import PyPDF2
import os

# Function to extract classes taken with their assigned letter grade
def extract_classes_and_grades(pdf_path):
    # Pattern to capture course codes (e.g., "EEE 4351C")
    class_pattern = re.compile(r'\b[A-Z]{3}\s?\d{4}[A-Z]?\b')
    
    # Pattern to capture letter grades, including S, W, and IP
    grade_pattern = re.compile(r'\b(?:[A-F]|S|W|IP)\b')

    passed = []
    failed = []
    inprog = []

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
        for k,s in extracted_data.items():
            if s in ["A","B","C","S"]:
                passed.append(k)

            elif s == "IP":
                inprog.append(k)

            else:
                failed.append(k)

    return extracted_data,passed,failed,inprog

#Function to read cached JSON file of transcript
def Read_Json_Grades(JSON_data):

    passed = []
    failed = []
    inprog = []

    extracted_data = {}

    for k,s in JSON_data.items():
            if s in ["A","B","C","S"]:
                passed.append(k)

            elif s == "IP":
                inprog.append(k)

            else:
                failed.append(k)
    return passed,failed,inprog

#===================================================================================================

# Checking if previous data is saved in cache
if os.path.exists("classes_with_grades.json"):
    with open("classes_with_grades.json", "r") as file:
        data = json.load(file)  # Load JSON data
    file.close()

    passed,failed,inprog = Read_Json_Grades(data)

# Creating data from PDF
else:
    # Calling function to extract data
    pdf_path = "transcript.pdf"  # File path name 
    classes_with_grades,passed,failed,inprog = extract_classes_and_grades(pdf_path)

    # Save to JSON file
    json_output = json.dumps(classes_with_grades, indent=4)
    with open("classes_with_grades.json", "w") as json_file:
        json_file.write(json_output)
    json_file.close()

    print("Extracted classes and grades saved to classes_with_grades.json")

# Testing extracted Lists
print(passed)
print(failed)
print(inprog)

#==========================================================================