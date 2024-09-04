import streamlit as st
import json
from pathlib import Path
import hashlib
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# define grade points
grade_points = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}

# define options for course credit units
credit_units_options = list(range(1, 17))

# directory for saving and loading data
data_dir = Path("saved_gpa_data")
data_dir.mkdir(exist_ok=True)

# helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

def calculate_gpa(courses):
    total_points = 0
    total_credits = 0

    for course in courses:
        grade = course['grade']
        if isinstance(grade, list):
            grade = grade[0]  # convert list to a single value
        if grade in grade_points:
            total_points += grade_points[grade] * course['credit_unit']
            total_credits += course['credit_unit']

    if total_credits == 0:
        return 0

    return total_points / total_credits

def classify_gpa(gpa):
    if 4.50 <= gpa <= 5.00:
        return "First Class", "🎉 Congratulations! You're in the First Class. Outstanding performance!"
    elif 3.50 <= gpa <= 4.49:
        return "Second Class Upper", "👏 Great job! You're in the Second Class Upper. Keep it up!"
    elif 2.40 <= gpa <= 3.49:
        return "Second Class Lower", "👍 Good work! You're in the Second Class Lower. Well done!"
    elif 1.50 <= gpa <= 2.39:
        return "Third Class", "🙂 You've earned a Third Class. There's room for improvement, keep pushing!"
    elif 1.00 <= gpa <= 1.49:
        return "Pass", "🙂 You've passed. Keep striving to improve!"
    else:
        return "No Class", "😟 Your GPA is below the minimum passing grade. Don't give up, work hard next time!"

def save_user_data(username, password):
    user_data = {
        "username": username,
        "password": hash_password(password)
    }
    with open(data_dir / "user_data.json", 'a') as file:
        json.dump(user_data, file)
        file.write('\n')

def load_user_data():
    users = []
    file_path = data_dir / "user_data.json"
    if file_path.exists():
        with open(file_path, 'r') as file:
            for line in file:
                users.append(json.loads(line.strip()))
    return users


def save_session_data(level, session_type, courses, username=None):
    data = {
        "level": level,
        "session_type": session_type,
        "courses": courses
    }
    filename = f"{username}_gpa_data.json" if username else "gpa_data.json"
    with open(data_dir / filename, 'w') as file:
        json.dump(data, file, indent=4)
    st.success("Data saved successfully!")

def load_session_data(username=None):
    filename = f"{username}_gpa_data.json" if username else "gpa_data.json"
    file_path = data_dir / filename
    if file_path.exists():
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        st.warning("No saved data found.")
        return None

def generate_pdf(username, level, session_type, courses, gpa, gpa_class, message):
    # convert Path to string
    pdf_file = data_dir / f"{username}_gpa_results.pdf"
    pdf_file_str = str(pdf_file)  # Convert to string

    doc = SimpleDocTemplate(pdf_file_str, pagesize=letter)
    content = []
    styles = getSampleStyleSheet()

    # title and user information
    content.append(Paragraph("Student cGPA Report", styles['Title']))
    content.append(Paragraph(f"Username: {username}", styles['Normal']))
    content.append(Paragraph(f"Level: {level}", styles['Normal']))
    content.append(Paragraph(f"Session Type: {session_type}", styles['Normal']))
    content.append(Spacer(1, 12))

    # course Table
    data = [["Course Code", "Course Title", "Credit Unit", "Grade"]]
    for course in courses:
        data.append([
            course.get('course_code', 'N/A'),
            course.get('course_title', 'N/A'),
            str(course.get('credit_unit', 'N/A')),
            course.get('grade', 'N/A')
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(table)
    content.append(Spacer(1, 12))

    # GPA and Classification
    content.append(Paragraph(f"GPA: {gpa:.2f}", styles['Normal']))
    content.append(Paragraph(f"Classification: {gpa_class}", styles['Normal']))
    content.append(Paragraph(f"Message: {message}", styles['Normal']))

    doc.build(content)
    return pdf_file


def authenticate_user():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_user_data()
        for user in users:
            if user["username"] == username and verify_password(user["password"], password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Authenticated successfully!")
                return
        st.error("Invalid credentials!")

def register_user():
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password == confirm_password:
            users = load_user_data()
            if any(user["username"] == username for user in users):
                st.error("Username already exists. Please choose a different username.")
            else:
                save_user_data(username, password)
                st.session_state["username"] = username
                st.session_state["authenticated"] = True
                st.success(f"Username '{username}' registered successfully!")
                save_session_data(None, None, [], username)  # Initialize with empty data
        else:
            st.error("Passwords do not match.")

# generate a unique course code and title for each new course added
def generate_unique_course(existing_courses):
    base_code = "ELE"
    base_title = "Introduction to Course "
    
    course_number = len(existing_courses) + 101  # start course numbers from 101 and increment
    course_code = f"{base_code}{course_number}"
    course_title = f"{base_title}{course_number - 100}"  # adjust title to reflect course number

    return course_code, course_title

def main():
    st.title("cGPA Calculator")

    # initialize session state variables if they don't exist
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = None

    if "courses" not in st.session_state:
        st.session_state["courses"] = []

    if not st.session_state["authenticated"]:
        authenticate_user()  # implement your user authentication logic here
        st.stop()

    load_data = st.checkbox("Load previous session data")
    if load_data:
        session_data = load_session_data(st.session_state["username"])
        if session_data:
            level = session_data["level"]
            session_type = session_data["session_type"]
            st.session_state["courses"] = session_data["courses"]
        else:
            st.stop()
    else:
        level = st.selectbox("Select Level", ["100", "200", "300", "400", "500", "600", "700"])
        session_type = st.radio("Select Session Type", ["First Semester", "Second Semester", "Full Session"])

    st.subheader("Course Input")

    # add a new course if the "Add Course" button is pressed
    if st.button("Add Course"):
        # generate unique course code and title
        course_code, course_title = generate_unique_course(st.session_state["courses"])
        # append the new course to the session state with unique course code and title, and fixed credit unit and grade
        st.session_state["courses"].append({
            "course_code": course_code,
            "course_title": course_title,
            "credit_unit": credit_units_options[0],
            "grade": list(grade_points.keys())[0]
        })

    # render course input fields based on current state
    course_container = st.container()
    with course_container:
        num_courses = len(st.session_state["courses"])

        updated_courses = []

        for i in range(num_courses):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2])
                with col1:
                    course_code = st.text_input(f"Course Code {i+1}", value=st.session_state["courses"][i]['course_code'], key=f"code_{i}")
                with col2:
                    course_title = st.text_input(f"Course Title {i+1} (Optional)", value=st.session_state["courses"][i].get('course_title', ''), key=f"title_{i}")
                with col3:
                    credit_unit = st.selectbox(
                        f"Credit Unit {i+1}", 
                        credit_units_options, 
                        index=credit_units_options.index(st.session_state["courses"][i].get('credit_unit', credit_units_options[0])), 
                        key=f"unit_{i}"
                    )
                with col4:
                    grade = st.selectbox(
                        f"Grade {i+1}", 
                        list(grade_points.keys()), 
                        index=list(grade_points.keys()).index(st.session_state["courses"][i].get('grade', list(grade_points.keys())[0])), 
                        key=f"grade_{i}"
                    )
                with col5:
                    remove_button = st.button("Remove", key=f"remove_{i}")
                    if remove_button:
                        # directly update session state
                        st.session_state["courses"].pop(i)
                        # remove course from list and display updated fields
                        updated_courses = st.session_state["courses"]
                        break

                # add course details to updated_courses list
                updated_courses.append({
                    "course_code": course_code,
                    "course_title": course_title,
                    "credit_unit": credit_unit,
                    "grade": grade
                })

        # update session state with new course details
        st.session_state["courses"] = updated_courses

    if st.button("Save Session Data"):
        save_session_data(level, session_type, st.session_state["courses"], st.session_state["username"])

    # Debug: Print session state
    # st.write("Session State:", st.session_state["courses"])

    # GPA calculation and display
    gpa = calculate_gpa(st.session_state["courses"])
    if session_type != "Full Session":
        st.write(f"Your GPA for the selected semester is: **{gpa:.2f}**")
        gpa_class, message = classify_gpa(gpa)
        st.subheader(gpa_class)
        st.write(message)
    else:
        session_courses = [course for course in st.session_state["courses"] if course['grade'] != '']
        cGPA = calculate_gpa(session_courses)
        st.write(f"Your cGPA for the selected session is: **{cGPA:.2f}**")
        gpa_class, message = classify_gpa(cGPA)
        st.subheader(gpa_class)
        st.write(message)

    # PDF download
    if st.button("Download PDF"):
        with st.spinner('Generating PDF...'):
            pdf_file = generate_pdf(
                st.session_state["username"],
                level,
                session_type,
                st.session_state["courses"],
                gpa,
                gpa_class,
                message
            )
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="Download PDF to Your Device",
                    data=f,
                    file_name=pdf_file.name,
                    mime="application/pdf"
                )


if __name__ == '__main__':
    main()
