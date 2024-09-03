import streamlit as st
import pandas as pd
import json
from pathlib import Path

# define grade points
grade_points = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}

# define options for course credit units
credit_units_options = list(range(1, 16))

# directory for saving and loading data
data_dir = Path("saved_gpa_data")
data_dir.mkdir(exist_ok=True)

def calculate_gpa(courses):
    total_weight = 0
    total_credits = 0
    for course in courses:
        if course['grade'] in grade_points:
            course_weight = grade_points[course['grade']] * course['credit_unit']
            total_weight += course_weight
            total_credits += course['credit_unit']
    return total_weight / total_credits if total_credits > 0 else 0

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
    
def authenticate_user():
    # simple authentication (for demonstration purposes)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # dummy authentication check
    if st.button("Login"):
        if username == "admin" and password == "password":
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success("Authenticated successfully!")
        else:
            st.error("Invalid credentials!")

def main():
    st.title("cGPA Calculator")

    # check if the user is authenticated
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        authenticate_user()
        st.stop()

    # Optional: load or create a new session
    load_data = st.checkbox("Load previous session data")
    if load_data:
        session_data = load_session_data(st.session_state["username"])
        if session_data:
            level = session_data["level"]
            session_type = session_data["session_type"]
            courses = session_data["courses"]
        else:
            st.stop()
    else:
        level = st.selectbox("Select Level", ["100", "200", "300", "400", "500", "600", "700"])
        session_type = st.radio("Select Session Type", ["First Semester", "Second Semester", "Full Session"])
        courses = []

    # course input section
    st.subheader("Course Input")

    course_container = st.container()

    if load_data and session_data:
        for i, course in enumerate(courses):
            with course_container:
                course_code = st.text_input(f"Course Code", value=course['course_code'], key=f"code_{course['course_code']}_{i}")
                course_title = st.text_input(f"Course Title (Optional)", value=course.get('course_title', ''), key=f"title_{course['course_code']}_{i}")
                credit_unit = st.selectbox(f"Credit Unit", credit_units_options, index=credit_units_options.index(course['credit_unit']), key=f"unit_{course['course_code']}_{i}")
                grade = st.selectbox(f"Grade", list(grade_points.keys()), index=list(grade_points.keys()).index(course['grade']), key=f"grade_{course['course_code']}_{i}")
                courses[i] = {"course_code": course_code, "course_title": course_title, "credit_unit": credit_unit, "grade": grade}
    else:
        num_courses = st.number_input("Number of Courses", min_value=1, max_value=60, value=5, step=1)

        for i in range(num_courses):
            with course_container:
                course_code = st.text_input(f"Course Code {i+1}", f"Course {i+1}", key=f"new_code_{i}")
                course_title = st.text_input(f"Course Title {i+1} (Optional)", key=f"new_title_{i}")
                credit_unit = st.selectbox(f"Credit Unit {i+1}", credit_units_options, key=f"new_unit_{i}")
                grade = st.selectbox(f"Grade {i+1}", list(grade_points.keys()), key=f"new_grade_{i}")

                # store course details
                courses.append({"course_code": course_code, "course_title": course_title, "credit_unit": credit_unit, "grade": grade})

    # GPA calculation and display
    if session_type != "Full Session":
        gpa = calculate_gpa(courses)
        st.write(f"Your GPA for the selected semester is: **{gpa:.2f}**")
        gpa_class, message = classify_gpa(gpa)
        st.subheader(gpa_class)
        st.write(message)
    else:
        # assuming the user inputs both semesters' courses
        session_courses = [course for course in courses if course['grade'] != '']
        cGPA = calculate_gpa(session_courses)
        st.write(f"Your cGPA for the selected session is: **{cGPA:.2f}**")
        gpa_class, message = classify_gpa(cGPA)
        st.subheader(gpa_class)
        st.write(message)
        
    # save data option
    if st.button("Save Session Data"):
        save_session_data(level, session_type, courses, st.session_state["username"])

if __name__ == '__main__':
    main()
