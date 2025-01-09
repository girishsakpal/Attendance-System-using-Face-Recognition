import cv2
import os
import time
import datetime
import face_recognition
import tkinter as tk
from tkinter import ttk, Button, Frame, Label, Entry, Listbox, END, messagebox
from PIL import Image, ImageTk

# folder where student images will be saved
saved_folder = r"path\of\folder\for\storing\images" 

# folder where attendance will be saved
attendance_folder=r"path\of\folder\for\storing\attendance"

# Ensuring if the folder exists
os.makedirs(saved_folder, exist_ok=True)

# List of subjects
subjects = ['CG', 'EM3', 'DS', 'DLCOA', 'JAVA', 'DSGT']

# Loading the Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Global variable to manage video capture across functions
video_capture = None

#Loading known faces
def load_known_faces(saved_folder):
    known_face_encodings = []
    known_face_names = []
    known_face_uins = []

    for filename in os.listdir(saved_folder):
        if filename.lower().endswith((".jpg", ".png")):
            image_path = os.path.join(saved_folder, filename)
            try:
                # Extract UIN from the filename (assuming format: name_UIN.jpg)
                name, uin = os.path.splitext(filename)[0].rsplit('_', 1)
                image = cv2.imread(image_path)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(image_rgb)
                if face_encodings:
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(name)
                    known_face_uins.append(uin)
                else:
                    print(f"No faces found in {filename}. Skipping.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return (known_face_encodings, known_face_names, known_face_uins)

# Initialize CSV with headers if it doesn't exist
def initialize_csv(attendance_file):
    if not os.path.exists(attendance_file):
        with open(attendance_file, 'w') as f:
            f.write("Subject,Name,UIN,Date,Time\n")

# Mark attendance in a CSV file
def mark_attendance(subject, name, uin, attendance_file):
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    with open(attendance_file, 'a') as f:
        f.write(f"{subject},{name},{uin},{date_str},{time_str}\n")
    print(f"Attendance marked for {name} (UIN: {uin}) in {subject} at {date_str} {time_str}.")

# Function to capture and save a student's image if a face is detected
def capture_student_image(student_name, uin, saved_folder):
    global video_capture  # Now video_capture is a global variable
    video_capture = cv2.VideoCapture(0)

    print("Capturing image... Please position your face in front of the camera.")
    time.sleep(1)

    face_found = False

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Could not read frame. Please check your camera connection.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_cascade.detectMultiScale(rgb_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face_found = True

        cv2.imshow('Capture Student Image', frame)

        if face_found:
            image_path = os.path.join(saved_folder, f"{student_name}_{uin}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"Image saved as {image_path}.")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Image capture canceled.")
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return face_found

# Function to capture student details via GUI
def capture_student_details_gui():
    student_name = entry_name.get().strip()
    uin = entry_uin.get().strip()

    if not student_name or not uin:
        messagebox.showwarning("Input Error", "Please enter both name and UIN.")
        return

    if len(uin) != 7:
        messagebox.showwarning("Input Error", "UIN must be exactly 7 characters long.")
        return

    success = capture_student_image(student_name, uin, saved_folder)
    if success:
        messagebox.showinfo("Success", f"Image captured and saved for {student_name}.")
        entry_name.delete(0, END)
        entry_uin.delete(0, END)
    else:
        messagebox.showerror("Error", "Failed to capture image. Please try again.")

# Function to mark attendance via GUI
def mark_attendance_gui():
    global video_capture  # Use the global video_capture
    selected_subject = subject_combobox.get()
    if selected_subject not in subjects:
        messagebox.showwarning("Selection Error", "Please select a valid subject.")
        return

    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    attendance_file = os.path.join(attendance_folder, f"{selected_subject}_{date_str}.csv")
    initialize_csv(attendance_file)

    (known_face_encodings, known_face_names, known_face_uins) = load_known_faces(saved_folder)

    if not known_face_encodings:
        messagebox.showwarning("No Data", "No known faces found. Please add student details first.")
        return

    marked_attendees = set()
    session_active = True

    btn_start_attendance.config(state='disabled')
    subject_combobox.config(state='disabled')
    lbl_status.config(text=f"Attendance Session for {selected_subject} Started...", fg="green")

    def process_frame():
        nonlocal session_active
        if not session_active:
            return

        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame.")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            uin = ""

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                uin = known_face_uins[first_match_index]

                if (name, uin, selected_subject) not in marked_attendees:
                    mark_attendance(selected_subject, name, uin, attendance_file)
                    marked_attendees.add((name, uin, selected_subject))
                    attendance_list.insert(0, f"{selected_subject}: {name} ({uin}) at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            if uin:
                cv2.putText(frame, f"{name} ({uin})", (left + 6, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 255, 255), 2)
            else:
                cv2.putText(frame, name, (left + 6, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 255, 255), 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

        lbl_video.after(10, process_frame)

    # Re-enable the Stop Attendance button and subject combobox
        btn_stop.config(state='normal')
        subject_combobox.config(state='readonly')

    def stop_attendance():
        nonlocal session_active
        session_active = False
        video_capture.release()
        cv2.destroyAllWindows()
        lbl_status.config(text=f"Attendance Session for {selected_subject} Stopped.", fg="red")
        btn_start_attendance.config(state='normal')
        subject_combobox.config(state='readonly')
        btn_stop.config(state='disabled')
    
    def start_video_capture():
        global video_capture  # Use the global video_capture
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            messagebox.showerror("Camera Error", "Could not open video capture.")
            lbl_status.config(text=f"Failed to start session for {selected_subject}.", fg="red")
            btn_start_attendance.config(state='normal')
            subject_combobox.config(state='readonly')
            return

        process_frame()
    start_video_capture()

def stop_attendance_gui():
        global video_capture  # Access the global video capture object

        # Stop the session
        session_active = False
        if video_capture.isOpened():
            video_capture.release()  # Release the video capture
        cv2.destroyAllWindows()  # Close any OpenCV windows

        # Update the UI to indicate the session has stopped
        lbl_status.config(text="Attendance session has been stopped.", fg="red")

        # Re-enable the Start Attendance button and subject combobox
        btn_start_attendance.config(state='normal')
        subject_combobox.config(state='readonly')

        # Disable the Stop Attendance button
        btn_stop.config(state='disabled')

        # Clear the attendance list from the GUI (optional)
        attendance_list.delete(0, END)

# Create the main window
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("1000x800")
root.resizable(False, False)

# Set a background color
root.configure(bg="#f0f0f0")

# Create a header frame with a logo
header_frame = Frame(root, bg="#4a90e2")
header_frame.pack(fill='x')

# Header title
header_title = Label(header_frame, text="Face Recognition Attendance System", font=("Helvetica", 24, "bold"), fg="white", bg="#4a90e2")
header_title.pack(pady=7)

# Create tabs
tab_control = ttk.Notebook(root)

# Styling for tabs
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', background="#4a90e2", foreground="white", padding=10, font=("Helvetica", 12, "bold"))
style.map("TNotebook.Tab", background=[("selected", "#1e81b0")], foreground=[("selected", "white")])

# Tab for capturing student details
tab_add = ttk.Frame(tab_control)
tab_control.add(tab_add, text='Add Student')

# Tab for marking attendance
tab_attendance = ttk.Frame(tab_control)
tab_control.add(tab_attendance, text='Mark Attendance')

tab_control.pack(expand=1, fill='both')

# ----- Add Student Tab -----
frame_add = Frame(tab_add, bg="#f0f0f0")
frame_add.pack(pady=40)

# Student Name
lbl_name = Label(frame_add, text="Student Name:", font=("Arial", 14), bg="#f0f0f0")
lbl_name.grid(row=0, column=0, padx=20, pady=20, sticky=tk.E)
entry_name = Entry(frame_add, font=("Arial", 14), width=30)
entry_name.grid(row=0, column=1, padx=20, pady=20)

# Student UIN
lbl_uin = Label(frame_add, text="Student UIN:", font=("Arial", 14), bg="#f0f0f0")
lbl_uin.grid(row=1, column=0, padx=20, pady=20, sticky=tk.E)
entry_uin = Entry(frame_add, font=("Arial", 14), width=30)
entry_uin.grid(row=1, column=1, padx=20, pady=20)

# Capture Image Button with styling
btn_capture = Button(frame_add, text="Capture Image", font=("Arial", 14, "bold"), bg="#4caf50", fg="white", width=20, command=capture_student_details_gui)
btn_capture.grid(row=2, column=0, columnspan=2, pady=30)

# ----- Mark Attendance Tab -----
mark_attendance_tab = Frame(tab_attendance, bg="#f0f0f0")
mark_attendance_tab.pack(pady=5)

# Subject Selection
lbl_subject = Label(mark_attendance_tab, text="Select Subject:", font=("Arial", 14), bg="#f0f0f0")
lbl_subject.pack(pady=5)

subject_combobox = ttk.Combobox(mark_attendance_tab, values=subjects, font=("Arial", 14), state='readonly', width=27)
subject_combobox.pack(pady=2)
subject_combobox.set("Select a subject")

# Start Attendance Button with styling
btn_start_attendance = Button(mark_attendance_tab, text="Start Attendance Session", font=("Arial", 14, "bold"), bg="#2196f3", fg="white", width=25, command=mark_attendance_gui)
btn_start_attendance.pack(pady=2)

# Status Label
lbl_status = Label(mark_attendance_tab, text="", font=("Arial", 12), bg="#f0f0f0")
lbl_status.pack(pady=2)

# Stop Attendance Button with styling
btn_stop = Button(mark_attendance_tab, text="Stop Attendance Session", font=("Arial", 14, "bold"), bg="#2196f3", fg="white", width=25, command= stop_attendance_gui)
btn_stop.pack()

# Listbox to show attendance
lbl_attendance = Label(mark_attendance_tab, text="Attendance Log:", font=("Arial", 14), bg="#f0f0f0")
lbl_attendance.pack(pady=2)

attendance_list = Listbox(mark_attendance_tab, width=80,height=1, font=("Arial", 12), bg="#ffffff", fg="#000000")
attendance_list.pack(pady=2)

# Label to show video feed
lbl_video = Label(mark_attendance_tab, bg="#f0f0f0")
lbl_video.pack(pady=2)

# Run the GUI event loop
root.mainloop()