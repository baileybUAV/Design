# Curriculum Helper Project - Team 11

This project is a student-focused curriculum management application that helps students track their academic progress, plan their course schedules, and prepare for academic advising. The application will feature visual flowcharts, course information management, and academic planning tools.

## Description

This project provides the functionality listed below:

### Curriculum Flowcharts
- Interactive visual representation of curriculum
- Course prerequisite chains
- Completed vs remaining courses highlighting
- Color coding for different course types

### Course Details
- Database of course information
- Credit hours tracking
- Prerequisites display
- Course descriptions
- Search functionality

### Planning Tools
- Semester-by-semeter planning
- Prerequisite checking
- Course load calculator
- Progress tracking
- Graduation requirement verification

### Pre-Advising Checklist
- Dynamic checklist generation
- Customizable question templates
- Progress saving
- PDF export capability

### Resource Links
- Categorized resource organization
- Faculty directory
- Academic support services links
- Direct email integration

### File Management
- Transcript upload and parsing
- Progress report generation
- Data export functionality
- File format validation
- Error handling

### Application Integration
- Menu system and navigation between features
- Data sharing between components
- Error handling across features
- System stability

## Getting Started

### Software Requirements

- Python 3.5+
- 64-bit Operating System


### Library Requirements

- Graphviz (graphing)
- pdfplumber (transcript reading)

Other used libraries that are included in Python's Standard Library or are installed with Python 3.x, and so do not need to be installed:

- webbrowser (web browser controller)
- tkinter (Graphical User Interface)
- re (regular expression operations)
- os (operating system interfaces)
- json (data interchange)
- pip (recommended package install method)


### Installing
The libraries listed above should be installed in the "Program Files" folder in your main drive. 

#### 1. Installing Graphviz
Use the link below to navigate to graphviz's listed install packages.

https://graphviz.org/download/

Click the *graphviz-12.2.0 64-bit EXE installer* to start the download. Run the .exe, click next, and agree to the license agreement

In install options, select *Add Graphviz to the system PATH for all users* and click next. Make sure the Destination Folder is placed within the Program Files folder, click next, and click install.

#### 2. Installing pdfplumber
pdfplumber can be installed using pip by opening the command prompt and typing the following command:
```
pip install pdfplumber
```

### Executing program

To start the application, run the FULL_PROGRAM_UI.py python file. Make sure to use the Transcript Parser to upload your transcript before using the rest of the Curriculum Helper's functionality.

## Help

Test cases, each with sample input files and expected output files, have been provided for each major feature in the Testing Materials folder. A user manual describing how to use each feature, input/output formats, and troubleshooting error messages has also been provided.

## Authors

Samuel Jackson (samich915)

Graham Taylor (GTA69420)

Brandon Bailey (baileybUAV)

Alexander Lee (alee714)
