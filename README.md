# Attendance-System-using-Face-Recognition
This repository consists of a mini project on Attendance System using Face Recognition which I have made using python in order to increase my knowledge on the subject as well as for practice.

This is a Python-based attendance management system that utilizes face recognition for marking attendance. The system includes a GUI for managing students and marking their attendance across various subjects.

Features
1.Add Students: Capture and store student images with their names and unique identification numbers (UIN).
2.Face Recognition: Recognize registered students using face recognition technology.
3.Mark Attendance: Automatically log attendance into CSV files.
4.Subject Management: Choose subjects for marking attendance.
5.GUI Interface: Easy-to-use graphical user interface built with Tkinter.

Prerequisites
Make sure you have the following installed:
Python 3.8 or higher
OpenCV (cv2)
dlib (required by face_recognition)
face_recognition library
tkinter (comes pre-installed with Python)
PIL (Pillow)

Install dependencies using:
pip install opencv-python face-recognition pillow

Setup:
1.Clone the repository:
git clone https://github.com/yourusername/face-recognition-attendance.git
cd face-recognition-attendance
2.Update paths for storing student images and attendance files:
Modify saved_folder and attendance_folder in the code to appropriate paths on your system.
3.Ensure the Haar Cascade file is available:
The script uses haarcascade_frontalface_default.xml from OpenCV. It is automatically included if OpenCV is installed.

How to Run:
1.Execute the script:
python face_recognition_attendance.py
2.Use the GUI to:
Add students by entering their name and UIN, and capturing their image.
Mark attendance by selecting a subject and starting the attendance session.

Folder Structure:
1.Student Images: All captured student images are stored in the saved_folder directory.
2.Attendance Records: Attendance data is stored in CSV files under the attendance_folder directory.

Usage Notes:
1.Ensure good lighting and a clear face view during image capture for accurate recognition.
2.UIN must be a 7-character alphanumeric string.
3.Stop the attendance session before closing the application to ensure data integrity.

Known Issues
1.Camera initialization may fail on certain systems. Ensure the webcam is functioning correctly.
2.Face recognition accuracy may vary based on image quality.
