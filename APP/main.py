import streamlit as st
import random
import smtplib
import mysql.connector
import re
import uuid
import base64
import qrcode
import io
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

# For debugging purposes
print(sys.version)

# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# SMTP server configuration
SMTP_SERVER = 'smtp-relay.brevo.com'
SMTP_PORT = 587
EMAIL_ADDRESS = "gaikwaddeepa65@gmail.com"
EMAIL_PASSWORD = "mHY7V86P3Fh9O5qS"

# Database Configuration
db_config = {
    'host': 'streamlit-rds.c3weg86e8fzs.eu-north-1.rds.amazonaws.com',
    'user': 'prajwal',
    'password': 'Prajwal123',
    'database': 'database-1',
    'port': 3306
}

# Initialize session state variables
if 'email_verified' not in st.session_state:
    st.session_state.email_verified = False
    st.session_state.email = ""

if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False

if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None

# Function to send email verification OTP
def send_email_verification(email):
    otp = generate_otp()
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg['Subject'] = 'Email Verification OTP'
    body = f'Your OTP for email verification is: {otp}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        st.session_state.generated_otp = otp  # Store the generated OTP in session state
        return otp
    except Exception as e:
        print("Error sending email:", e)
        return None

# Function to validate email format
def validate_email(email):
    pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    return bool(pattern.match(email))

def create_account():
    st.write("Create Account")
    st.write("Choose account type:")
    account_type = st.radio("Account Type", ["Formal User", "Authorized User"])

    if account_type == "Formal User":
        formal_user()
    elif account_type == "Authorized User":
        authorized_user()

def formal_user():
    st.write("Formal User Account Creation")
    email = st.text_input("Enter your email").strip()
    name = st.text_input("Enter your name")  # Collect name input
    password = st.text_input("Enter your password", type="password")

    verify_email_button = st.button("Verify Email")
    if verify_email_button:
        if validate_email(email):
            st.session_state.email_verified = True
            st.session_state.email = email
            st.session_state.account_type = "Formal User"
            st.session_state.name = name  # Store name in session state
            st.session_state.password = password
            send_email_verification(email)
            st.write("OTP has been sent to your email. Please enter the OTP below.")

    if st.session_state.email_verified:
        entered_otp = st.text_input("Enter the OTP sent to your email")
        verify_otp_button = st.button("Verify OTP")
        if verify_otp_button:
            if entered_otp == st.session_state.generated_otp:
                st.session_state.otp_verified = True
                st.write("Email verified successfully!")
                submit_details(email, name, password)
            else:
                st.write("Invalid OTP. Please try again.")

def authorized_user():
    st.write("Authorized User Account Creation")
    email = st.text_input("Enter your email").strip()
    name = st.text_input("Enter your name")  # Collect name input
    password = st.text_input("Enter your password", type="password")
    designation = st.text_input("Enter your designation")
    department = st.text_input("Enter your department")
    post_credited = st.text_input("Enter post credited")

    verify_email_button = st.button("Verify Email")
    if verify_email_button:
        if validate_email(email):
            st.session_state.email_verified = True
            st.session_state.email = email
            st.session_state.account_type = "Authorized User"
            st.session_state.name = name  # Store name in session state
            st.session_state.designation_input = designation
            st.session_state.department_input = department
            st.session_state.post_credited_input = post_credited
            st.session_state.password = password
            send_email_verification(email)
            st.write("OTP has been sent to your email. Please enter the OTP below.")

    if st.session_state.email_verified:
        entered_otp = st.text_input("Enter the OTP sent to your email")
        verify_otp_button = st.button("Verify OTP")
        if verify_otp_button:
            if entered_otp == st.session_state.generated_otp:
                st.session_state.otp_verified = True
                st.write("Email verified successfully!")
                submit_details(email, name, password, designation, department, post_credited)
            else:
                st.write("Invalid OTP. Please try again.")

def submit_details(email, name, password, designation_input=None, department_input=None, post_credited_input=None):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert user details into the database
        if designation_input is not None and department_input is not None and post_credited_input is not None:
            # This is an authorized user
            cursor.execute("INSERT INTO user_credential (email, username, password, user_type, designation, department, post_credited) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (email, name, password, 'one', designation_input, department_input, post_credited_input))
        else:
            # This is a formal user
            cursor.execute("INSERT INTO user_credential (email, username, password, user_type) VALUES (%s, %s, %s, %s)",
                           (email, name, password, 'zero'))

        # Commit changes and close cursor and connection
        conn.commit()
        cursor.close()
        conn.close()
        st.write("Details submitted successfully!")

    except mysql.connector.Error as err:
        st.write("Error occurred while submitting details:", err)
        

def submit_user_details(uuid_value, name, password, mobile_number, email_id, registration_number, engine_number, puc_image_data, aadhar_card_data, pan_card_data, driving_license_data, username, chasis_number):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Convert file data to bytes
        puc_image_data_bytes = puc_image_data.read() if puc_image_data else None
        aadhar_card_data_bytes = aadhar_card_data.read() if aadhar_card_data else None
        pan_card_data_bytes = pan_card_data.read() if pan_card_data else None
        driving_license_data_bytes = driving_license_data.read() if driving_license_data else None

        # Insert user details into the user_data table
        cursor.execute("INSERT INTO user_data (uuid, name, password, mobile_number, email_id, registration_number, engine_number, puc_image_data, aadhar_card_data, pan_card_data, driving_license_data, username, chasis_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (uuid_value, name, password, mobile_number, email_id, registration_number, engine_number, puc_image_data_bytes, aadhar_card_data_bytes, pan_card_data_bytes, driving_license_data_bytes, username, chasis_number))

        # Commit changes and close cursor and connection
        conn.commit()
        cursor.close()
        conn.close()
        st.write("User details submitted successfully!")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uuid_value)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Convert QR code image to bytes
        qr_byte_io = io.BytesIO()
        qr_img.save(qr_byte_io, format='PNG')
        qr_bytes = qr_byte_io.getvalue()

        # Display the QR code
        st.image(qr_bytes, caption='QR Code', use_column_width=True)

        # Add a download button for the QR code
        st.markdown(get_binary_file_downloader_html(qr_bytes, 'QR_Code', 'Download QR Code'), unsafe_allow_html=True)


    except mysql.connector.Error as err:
        st.write("Error occurred while submitting user details:", err)







def get_binary_file_downloader_html(bin_file, file_label='File', button_text='Download'):
    with io.BytesIO() as stream:
        stream.write(bin_file)
        stream.seek(0)
        bin_data = stream.read()
    bin_str = base64.b64encode(bin_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}.png">{button_text}</a>'
    return href





def verify_and_send_otp(email):
    designation_input = None
    department_input = None
    post_credited_input = None
    
    if validate_email(email):
        if 'otp_verified' not in st.session_state:
            st.session_state.generated_otp = send_email_verification(email)
            if st.session_state.generated_otp:
                st.write(f"OTP sent to {email}")
                st.session_state.otp_verified = False

        if not st.session_state.otp_verified:
            entered_otp = st.text_input("Enter OTP", key="otp")
            submit_button = st.button("Submit")
            if submit_button:
                if entered_otp == st.session_state.generated_otp:
                    st.write("OTP verified successfully!")
                    if st.session_state.account_type == "Formal User":
                        submit_details(email, st.session_state.name, st.session_state.password)
                    elif st.session_state.account_type == "Authorized User":
                        submit_details(email, st.session_state.name, st.session_state.password, st.session_state.designation_input, st.session_state.department_input, st.session_state.post_credited_input)
                    st.session_state.otp_verified = True
                    st.write("Details submitted")
                else:
                    st.write("Invalid OTP. Please try again.")


def forgot_credentials():
    st.write("Forgot Credentials")
    
    email = st.text_input("Enter your registered email").strip()
    send_otp_button = st.button("Send OTP")
    
    if send_otp_button:
        if validate_email(email):
            st.session_state.generated_otp = send_email_verification(email)
            if st.session_state.generated_otp:
                st.write(f"OTP sent to {email}")
                st.session_state.email_for_forgot_credentials = email
        else:
            st.write("Please enter a valid email address.")
    
    if 'generated_otp' in st.session_state:
        entered_otp = st.text_input("Enter OTP", key="forgot_otp")
        verify_otp_button = st.button("Verify OTP")
        
        if verify_otp_button:
            if entered_otp == st.session_state.generated_otp:
                st.write("OTP verified successfully!")
                st.session_state.otp_verified_for_forgot = True
            else:
                st.write("Invalid OTP. Please try again.")
    
    if 'otp_verified_for_forgot' in st.session_state and st.session_state.otp_verified_for_forgot:
        new_password = st.text_input("Enter new password", type='password')
        confirm_password = st.text_input("Confirm new password", type='password')
        reset_password_button = st.button("Reset Password")
        
        if reset_password_button:
            if new_password == confirm_password:
                try:
                    # Connect to the database
                    conn = mysql.connector.connect(**db_config)
                    cursor = conn.cursor()

                    # Update the password in the user_credential table
                    cursor.execute("UPDATE user_credential SET password = %s WHERE email = %s", 
                                   (new_password, st.session_state.email_for_forgot_credentials))
                    
                    # Commit changes and close cursor and connection
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.write("Password reset successfully!")
                    del st.session_state.generated_otp
                    del st.session_state.otp_verified_for_forgot
                    del st.session_state.email_for_forgot_credentials
                except mysql.connector.Error as err:
                    st.write("Error occurred while resetting the password:", err)
            else:
                st.write("Passwords do not match. Please try again.")





def display_user_form(user):
    st.write("Welcome, ", user[1], "please fill below form and generate your QR code")  # Assuming username is in the second column
    st.write("Email: ", user[0])  # Assuming email is in the first column

    with st.form(key='user_details_form'):
        # Create a form to collect additional user information
        st.write("Please provide the following details:")
        uuid_value = uuid.uuid4().hex  # Step 2: Generate UUID
        name = st.text_input("Name")
        password = st.text_input("Password", value=user[2])
        mobile_number = st.text_input("Mobile Number")
        email_id = st.text_input("Email ID", value=user[0])
        registration_number = st.text_input("Registration Number")
        engine_number = st.text_input("Engine Number")
        puc_image_data = st.file_uploader("Upload PUC Image", type=["jpg", "png", "jpeg"])
        aadhar_card_data = st.file_uploader("Upload Aadhar Card", type=["jpg", "png", "jpeg"])
        pan_card_data = st.file_uploader("Upload PAN Card", type=["jpg", "png", "jpeg"])
        driving_license_data = st.file_uploader("Upload Driving License", type=["jpg", "png", "jpeg"])
        username = st.text_input("Username", value=user[1])
        chasis_number = st.text_input("Chasis Number")

        # Add a submit button to submit the form
        submit_user_button = st.form_submit_button("Submit")

    # Check if the form is submitted and handle QR code generation
    if submit_user_button:
        submit_user_details(uuid_value, name, password, mobile_number, email_id, registration_number, engine_number, puc_image_data, aadhar_card_data, pan_card_data, driving_license_data, username, chasis_number)
        st.session_state.qr_code_generated = True



        
def login(username_input, password_input):
    try:
        if not username_input or not password_input:
            st.write("Please enter both email and password.")
            return

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if the username and password match any entry in the user_credential table
        cursor.execute("SELECT * FROM user_credential WHERE email = %s AND password = %s", (username_input, password_input))
        user = cursor.fetchone()

        if user:
            # Check if user details exist in the user_data table
            cursor.execute("SELECT * FROM user_data WHERE email_id = %s", (username_input,))
            user_data = cursor.fetchone()

            if user_data:
                st.write("Login Successful!")
                st.write("Profile details are already filled.")
                st.session_state.logged_in = True  # Set session state variable for logged in status
                st.session_state.profile_filled = True  # Set session state variable for profile filled status
            else:
                st.write("Login Successful!") 
                display_user_form(user)
        else:
            st.write("Invalid email or password. Please try again.")

        # Close cursor and connection
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        st.write("Error occurred while logging in:", err)
        
        
import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import mysql.connector



def fetch_user_details(uuid_value):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch user details based on UUID
        cursor.execute("SELECT * FROM user_data WHERE uuid = %s", (uuid_value,))
        user_data = cursor.fetchone()

        # Commit changes and close cursor and connection
        conn.commit()
        cursor.close()
        conn.close()

        return user_data

    except mysql.connector.Error as err:
        st.error("Error occurred while fetching user details:", err)
        return None

from PIL import Image

def display_profile(user_data):
    if user_data:
        st.title("User Profile")
        st.write(f"Name: {user_data[1]}")
        st.write(f"Email: {user_data[3]}")
        st.write(f"Mobile Number: {user_data[2]}")
        st.write(f"Registration Number: {user_data[4]}")
        st.write(f"Engine Number: {user_data[5]}")
        st.write(f"Username: {user_data[10]}")
        st.write(f"Chasis Number: {user_data[11]}")
        
        # Display uploaded images if available
        if user_data[6]:
            puc_img = blob_to_image(user_data[6])
            if puc_img:
                st.image(puc_img, caption="PUC Image", use_column_width=True)
            else:
                st.warning("Failed to display PUC Image.")
        
        if user_data[7]:
            aadhar_img = blob_to_image(user_data[7])
            if aadhar_img:
                st.image(aadhar_img, caption="Aadhar Card", use_column_width=True)
            else:
                st.warning("Failed to display Aadhar Card.")
        
        if user_data[8]:
            pan_img = blob_to_image(user_data[8])
            if pan_img:
                st.image(pan_img, caption="PAN Card", use_column_width=True)
            else:
                st.warning("Failed to display PAN Card.")
        
        if user_data[9]:
            driving_license_img = blob_to_image(user_data[9])
            if driving_license_img:
                st.image(driving_license_img, caption="Driving License", use_column_width=True)
            else:
                st.warning("Failed to display Driving License.")
    else:
        st.warning("User details not found.")
        
        
        

from PIL import Image
import io

def blob_to_image(blob_data):
    try:
        # Convert blob data to bytes
        blob_bytes = io.BytesIO(blob_data)
        
        # Open image from bytes
        image = Image.open(blob_bytes)
        
        return image
    except Exception as e:
        print("Error converting blob to image:", e)
        return None





def scan_qr_code_and_display_profile():
    st.title("QR Code Scanner")

    # Display webcam feed
    video_feed = st.empty()
    cap = cv2.VideoCapture(0)

    # Define the region of interest (ROI) for QR code detection
    roi_x, roi_y, roi_width, roi_height = 100, 100, 300, 300

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture video.")
            break

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Define the region of interest (ROI) for QR code detection
        roi = gray[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

        # Find QR codes in the ROI
        decoded_objects = decode(roi)

        # Display frame
        video_feed.image(frame, channels="BGR")

        # Display decoded QR codes
        for obj in decoded_objects:
            if obj.type == 'QRCODE':
                # If QR code detected within ROI, stop the video feed
                st.sidebar.markdown("## QR Code Detected")
                st.sidebar.image(frame, channels="BGR", caption="QR Code")
                st.sidebar.markdown("### Decoded Text:")
                st.sidebar.write(obj.data.decode('utf-8'))
                cap.release()  # Release the camera

                # Fetch user details based on the UUID
                user_data = fetch_user_details(obj.data.decode('utf-8'))
                # Display user profile
                display_profile(user_data)
                return  # Exit the function to stop the video feed

    # Release the camera if the loop exits
    cap.release()
    






def main():
    st.title("User Authentication and Profile Management")
    selected_option = st.sidebar.radio("Select Option", ["Create Account", "Login", "Forgot Credentials"])

    if selected_option == "Create Account":
        create_account()
    elif selected_option == "Login":
        username_input = st.text_input('Email')
        password_input = st.text_input('Password', type='password')
        login(username_input, password_input)
        
        # Check if user is logged in and profile details are filled
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            if 'profile_filled' in st.session_state and st.session_state.profile_filled:
                if st.sidebar.button("Update Profile"):
                    pass
                if st.sidebar.button("Scan QR Code"):
                    # Call the scan_qr_code_and_display_profile function
                    scan_qr_code_and_display_profile()
        
    elif selected_option == "Forgot Credentials":
        forgot_credentials()

if __name__ == "__main__":
    main()
