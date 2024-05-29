import streamlit as st
import gspread
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
import toml
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile
from PIL import Image
import base64
import requests

def upload_to_drive(file, credentials_json):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.getbuffer())
        temp_file_path = temp_file.name
    
    # Load the credentials
    credentials = Credentials.from_service_account_info(credentials_json, scopes=["https://www.googleapis.com/auth/drive.file"])
    
    # Build the Drive service
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Define file metadata
    file_metadata = {
        'name': file.name,
        'parents': ['1oV1rN9Y8WZWLB4c3xBZKLNRK2FIm0J7h']  # Your Google Drive folder ID
    }
    
    # Create the media file upload
    media = MediaFileUpload(temp_file_path, resumable=True)
    
    # Upload the file
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Get the file ID and generate a shareable link
    file_id = uploaded_file.get('id')
    shareable_link = f"https://drive.google.com/uc?export=view&id={file_id}"
    
    return shareable_link

# Check if running locally by trying to import toml and reading the local secrets file
try:
    secrets = toml.load("newyorkah/myenv/secrets.toml")
except FileNotFoundError:
    secrets = st.secrets

# Load the service account info from Streamlit secrets
key_file_path = secrets["gcp_service_account"]["path"]

with open(key_file_path) as source:
    service_account_info = json.load(source)

# Define the required scopes
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Use the credentials to authenticate with Google Sheets
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet_id = secrets["gcp_sheet_id"]["api_key"]
sheet = client.open_by_key(sheet_id)

#im = Image.open("favicon.ico")
def get_base64_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')
    
# Path to your local avatar image
image_url = "https://raw.githubusercontent.com/sausans/newyorkah/main/myenv/favicon.ico" 
avatar_base64 = get_base64_image_from_url(image_url)
avatar_url = f"data:image/x-icon;base64,{favicon_base64}"

#im = "myenv/icon.webp"
# Set the page configuration
st.set_page_config(
    page_title="TokTok: Apartment Services",
    page_icon=avatar_url,
    layout="wide",  # Assuming your favicon is in the same directory
)

st.title("TokTok: Cause finding apartments in US is a painful experience")

menu = ["Home", "Apartment Checking", "Roommate Matching", "Decoration", "Sell my stuffs please"]
choice = st.sidebar.selectbox("Click dropdown for our services", menu)

if choice == "Home":
    st.subheader("Welcome to the International Student Apartment Helper")
    st.write("""
    **Our Purpose:**
    
    This platform is designed to assist international students with their apartment hunting journey. 
    We understand that finding an apartment, especially from abroad, can be challenging. 
    Our goal is to make this process easier and more efficient by providing the following services:

    1. **Apartment Checking:** We understand that you are not sure whether you can trust the agent or the apartment you see on the website. Submit details about the apartments you are interested in, and we will help check and record information for you via WhatsApp.
   
    2. **Roommate Matching:** Find a new roommate to live together for months? But, do you know what to ask to them to know that they are the right ones? Fill out a questionnaire about your preferences, and we will help you find potential roommates.
    
    3. **Apartment Decoration:** You are about to spend good amount of hours in your room, wandering why you are doing this to yourself so make sure that you will do it in aesthetic condition- at least. Share your Pinterest board with us, and we will provide personalized decoration suggestions and help to decorate! And Hey, we might find  cheapeer stuffs for your room ;) 

    **Pricing**
    1. **Apartment Checking:** 15-20 dollars per 1 apartment view depending on distance
   
    2. **Roommate Matching:** 10 dollars per 1 roommate candidate
    
    3. **Apartment Decoration:** 30 dollars per 1 room

    We hope this platform helps make your transition to a new home smoother and more enjoyable!

    PIC: 
    +1-332-251-1844 - Sausan Huwel
    """)
elif choice == "Apartment Checking":
    st.subheader("Submit Apartment Details")
    with st.form("apartment_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        number = st.text_input("WhatsApp Number")
        apt_location = st.text_input("Location")
        apt_agent_number = st.text_input("Apartment Agent/Broker Phone Number")
        apt_link= st.text_input("Link to The Apartment Location")
        questions= st.text_input("Questions or Things to Check")
        submit = st.form_submit_button("Submit")

        if submit:
            sheet_apt = sheet.worksheet("Apartment Checking")
            sheet_apt.append_row([name, email, number, apt_location, apt_agent_number, apt_link, questions])
            st.success("Submitted successfully")

elif choice == "Roommate Matching":
    st.subheader("Submit Roommate Preferences")
    with st.form("roommate_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        number = st.text_input("WhatsApp Number")

        lifestyle = st.radio(
            "Which statement best describes you?",
            ("I am a morning person and prefer quiet in the evenings", "I am a night person and prefer quiet in the morning", "I am adaptable and don't have a strong preference for quiet time")
        )

        cooking = st.radio(
            "How often do you plan on cooking and eating in the apartment?",
            ("All the time", "Most of the time", "Rarely", "Never")
        )

        guest = st.radio(
            "How often would you like to have guests over to your apartment?",
            ("Frequently", "Occasionally", "Rarely", "Never, but I don't mind if my roommate does")
        )

        other_people = st.radio(
            "Are you okay if someone outside of your gender comes over to the apartment?",
            ("I am not okay", "I am okay as long as my roommate gives me a heads-up", "I am okay")
        )

        cleanliness = st.radio(
            "How often do you clean your living space?",
            ("Daily", "Weekly", "Bi-weekly", "Monthly or more infrequently")
        )

        dietary = st.radio(
            "Do you have any special dietary preferences?",
            ("None", "Vegetarian or Vegan", "Kosher", "Halal")
        )

        shared_utensils = st.radio(
            "Are you okay with sharing utensils?",
            ("I am not okay", "I am okay as long as it is shared with someone with the same dietary requirements as me", "I am okay as long as my roommate cleans them", "I am okay")
        )

        relationship = st.radio(
            "What are your expectations surrounding roommate friendship?",
            ("I don't expect to be close friends, just coexist peacefully", "I am open to naturally developing a good friendship", "I envision becoming close friends and spending time together")
        )

        preferences = st.text_area("Other Preferences")
        submit = st.form_submit_button("Submit")

        if submit:
            sheet_rm = sheet.worksheet("Roommate Matching")
            sheet_rm.append_row([name, email, number, lifestyle, cooking, guest, other_people, cleanliness, dietary, shared_utensils, relationship, preferences])
            st.success("Submitted successfully")

elif choice == "Decoration":
    st.subheader("Submit Pinterest Board")
    with st.form("decoration_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        number = st.text_input("WhatsApp Number")
        apt_address = st.text_input("Your Apartment Address")
        apt_pic = st.text_input("Link to Latest Pictures & Floor Plan of Your Apartment")
        apt_size = st.text_input("Your Apartment Size")
        decor_aesthetic = st.radio(
            "What is your decoration aesthetic?",
            ("Minimalist-Japandi", "Industrial", "Cabin in the Wood Style", " Girlie Cute", "Masculine")
        )
        decor_preference = st.radio(
            "How do you want to handle the furnitures?",
            ("I want to buy the furniture myself (we will only give you the furniture images & purchase link)", "I want TokTok to buy my furniture", "I want TokTok to buy and set up my furniture")
        )
        st.write("""
        Note: 
        1. If you choose "I want TokTok to buy my furniture," you will be charged $10 per piece of furniture.
        2. If you choose "I want TokTok to buy and set up my furniture," you will be charged an additional $10 per piece of furniture for installation, on top of the purchase charge.
        """)
        submit = st.form_submit_button("Submit")

        if submit:
            sheet_dec = sheet.worksheet("Decoration")
            sheet_dec.append_row([name, email, pinterest_link, decor_preference])
            st.success("Submitted successfully")

elif choice == "Sell my stuffs please":
    st.subheader("Submit Items for Sale")
    st.write("""
    Do you want to sell your furniture or clothes? Fill out this form and we will help to promote your stuffs to other people!
    However, we do need your commission / tip ;) Of course it is pay as you wish!
    
    """)
    with st.form("ecommerce_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        item_name = st.text_input("Item Name")
        item_type = st.radio(
            "Item Type",
            ("Furniture", "Fashion")
        )
        brand = st.text_input("Brand Name")
        item_description = st.text_area("Item Description")
        item_price = st.text_input("Item Price")
        item_image = st.file_uploader("Upload Item Image", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Submit")

        if submit:

           # Upload image to Google Drive and get the shareable link
            item_image_url = upload_to_drive(item_image, service_account_info) if item_image else "No Image"
            
            # Append the data to the Google Sheet
            sheet_ecom = sheet.worksheet("E-commerce")
            sheet_ecom.append_row([name, email, phone, item_name, brand, item_type, item_description, item_price, item_image_url])
            st.success("Submitted successfully")
