# stylect_app.py
import streamlit as st
import os
import json
import bcrypt
from datetime import datetime
from PIL import Image

# -------------- File Paths and Setup -------------- #
USER_DATA_FILE = "data/users.json"
WARDROBE_DIR = "data/wardrobe"
os.makedirs("data", exist_ok=True)
os.makedirs(WARDROBE_DIR, exist_ok=True)
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as f:
        json.dump({}, f)

# -------------- Auto-generate requirements.txt (for deployment) -------------- #
def generate_requirements_txt():
    with open("requirements.txt", "w") as f:
        f.write("streamlit\nbcrypt\npillow\n")
        # f.write("opencv-python-headless\n")  # Uncomment if using cv2 later

generate_requirements_txt()

# -------------- Utility Functions -------------- #
def load_users():
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# -------------- Auth Functions -------------- #
def signup_user(username, password, email, phone, security_answers):
    users = load_users()
    if username in users:
        return False, "Username already exists."

    users[username] = {
        "password": hash_password(password),
        "email": email,
        "phone": phone,
        "security_answers": security_answers,
        "created_at": str(datetime.now()),
        "wardrobe": [],
        "badges": [],
        "shop": [],
        "posts": []
    }
    save_users(users)
    return True, "Account created successfully!"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found."
    if not verify_password(password, users[username]["password"]):
        return False, "Incorrect password."
    return True, "Login successful."

# -------------- Wardrobe Handling -------------- #
def save_wardrobe_image(username, image_file):
    img_path = os.path.join(WARDROBE_DIR, f"{username}_{image_file.name}")
    with open(img_path, "wb") as f:
        f.write(image_file.getbuffer())
    users = load_users()
    users[username]["wardrobe"].append(img_path)
    save_users(users)
    return img_path

# -------------- Logout -------------- #
def show_logout():
    if st.sidebar.button("🚪 Logout"):
        del st.session_state["username"]
        st.success("You’ve been logged out.")
        st.experimental_rerun()

# -------------- App Pages -------------- #
def show_login_signup():
    st.title("👗 Stylect - Login / Sign Up")
    mode = st.radio("Select Mode:", ["Login", "Sign Up"], horizontal=True)

    if mode == "Sign Up":
        st.subheader("Create an Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")

        st.markdown("**Security Questions** (for recovery)")
        security_answers = {
            "q1": st.text_input("What is your grandma's name?"),
            "q2": st.text_input("What elementary school did you attend?"),
            "q3": st.text_input("What is your favorite color?")
        }

        if st.button("Sign Up"):
            success, msg = signup_user(username, password, email, phone, security_answers)
            if success:
                st.success(msg)
                st.session_state.username = username
                st.balloons()
            else:
                st.error(msg)

    elif mode == "Login":
        st.subheader("Welcome Back")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, msg = login_user(username, password)
            if success:
                st.session_state.username = username
                st.success(msg)
                st.experimental_rerun()
            else:
                st.error(msg)

# ---------------- Main Dashboard ---------------- #
def show_dashboard():
    st.title(f"Welcome, {st.session_state.username} 👋")
    show_logout()
    tab = st.sidebar.radio("Go to:", [
        "👚 Wardrobe", "🤖 Outfit Generator", "🎨 Color Analysis", "📅 Lookbook", "🛍️ Shop", "🧑‍🤝‍🧑 Style Feed"
    ])

    users = load_users()
    current_user = users[st.session_state.username]

    if tab == "👚 Wardrobe":
        st.subheader("Your Closet")
        uploaded = st.file_uploader("Upload an outfit image", type=["jpg", "jpeg", "png"])
        if uploaded:
            img_path = save_wardrobe_image(st.session_state.username, uploaded)
            st.image(img_path, caption="Saved to wardrobe", use_column_width=True)
        st.markdown("### Your Items")
        for item_path in current_user.get("wardrobe", []):
            st.image(item_path, width=150)

    elif tab == "🤖 Outfit Generator":
        st.subheader("AI Outfit Generator")
        st.markdown("(AI outfit suggestions will go here based on weather, event, body type, etc.)")

    elif tab == "🎨 Color Analysis":
        st.subheader("Upload Your Face for Color Palette")
        st.markdown("This feature requires OpenCV (cv2) and will show your best colors.")

    elif tab == "📅 Lookbook":
        st.subheader("Plan and Schedule Outfits")
        st.date_input("Select a day for your outfit")
        st.text_area("Describe your outfit plan")

    elif tab == "🛍️ Shop":
        st.subheader("Buy, Sell, or Trade")
        st.markdown("Shop UI and trading logic goes here")

    elif tab == "🧑‍🤝‍🧑 Style Feed":
        st.subheader("See What Others Are Wearing")
        st.markdown("Users can post outfits, like, comment, and vote")

# ---------------- App Entry Point ---------------- #
if __name__ == "__main__":
    st.set_page_config(page_title="Stylect", layout="wide")
    if "username" not in st.session_state:
        show_login_signup()
    else:
        show_dashboard()
