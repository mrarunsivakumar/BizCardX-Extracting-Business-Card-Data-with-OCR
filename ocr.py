import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image #Image Processing
import numpy as np #Image Processing 
import mysql.connector #sql database
import pandas as pd
import cv2
from streamlit_option_menu import option_menu

# Connect to the database
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="arunsiva",
  database="business_cards"
)

# Get a cursor to execute SQL queries
cursor = db.cursor()

# Create the ocr_results table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS ocr_results (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), job_title VARCHAR(255), address VARCHAR(255), postcode VARCHAR(255), phone VARCHAR(255), email VARCHAR(255), website VARCHAR(255), company_name VARCHAR(225))")
#title
st.title("BizCardX: Extracting Business Card Data with OCR")

# Add a sidebar menu
with st.sidebar:
  selected = option_menu(menu_title=None, options=["Extract","View", "Delete","Update"], icons=["clipboard-data","award","capslock-fill","capslock-fill"], orientation="vertical")

if selected == "Extract":
   #image uploader
   image = st.file_uploader(label = "Upload your image here",type=['png','jpg','jpeg'])

   @st.cache_data 
   def load_model(): 
       reader = ocr.Reader(['en'],model_storage_directory='.')
       return reader 

   reader = load_model() #load model

   if image is not None:

        input_image = Image.open(image) #read image
        # Perform image processing techniques to enhance the image quality before passing it to the OCR engine
        # Convert the image to a numpy array
        img_np = np.array(input_image)

        # Apply image processing techniques
        # Resize the image to reduce processing time and improve OCR accuracy
        resized = cv2.resize(img_np, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

        # Apply Gaussian blur to remove noise
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)

        # Convert the image to grayscale
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to binarize the image
        threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        # Perform OCR on the processed image
        result = reader.readtext(threshold)

        result_text = [] #empty list for results
        st.image(input_image) #display image

        with st.spinner("🤖 AI is at Work! "):
            

            result = reader.readtext(np.array(input_image))

            result_text = [] #empty list for results


            for text in result:
                result_text.append(text[1])

            # Display the extracted information in a table
            st.table({"Text": result_text})
            # Insert the OCR results into the database
            image_name = image.name
            result_text_str = ", ".join(result_text)
            query = "INSERT INTO ocr_results (name, job_title, address, postcode, phone, email, website, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (result_text[0], result_text[1], result_text[2], result_text[3], result_text[4], result_text[5], result_text[6],result_text[7])
            cursor.execute(query, values)
            db.commit()
    




# Display the stored business card information
if selected == 'View':
   cursor.execute("SELECT * FROM ocr_results")
   result = cursor.fetchall()
   df = pd.DataFrame(result, columns=['id', 'name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website', 'company_name'])
   st.write(df)

if selected == 'Update':
    # Create a dropdown menu to select a business card to update
    cursor.execute("SELECT id, name FROM ocr_results")
    result = cursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[1]] = row[0]
    selected_card_name = st.selectbox("Select a business card to update", list(business_cards.keys()))
    
    # Get the current information for the selected business card
    cursor.execute("SELECT * FROM ocr_results WHERE name=%s", (selected_card_name,))
    result = cursor.fetchone()

    # Display the current information for the selected business card
    st.write("Name:", result[1])
    st.write("Job Title:", result[2])
    st.write("Address:", result[3])
    st.write("Postcode:", result[4])
    st.write("Phone:", result[5])
    st.write("Email:", result[6])
    st.write("Website:", result[7])
    st.write("company_name:", result[8])

    # Get new information for the business card
    name = st.text_input("Name", result[1])
    job_title = st.text_input("Job Title", result[2])
    address = st.text_input("Address", result[3])
    postcode = st.text_input("Postcode", result[4])
    phone = st.text_input("Phone", result[5])
    email = st.text_input("Email", result[6])
    website = st.text_input("Website", result[7])
    company_name = st.text_input("Company Name", result[8])

    # Create a button to update the business card
    if st.button("Update Business Card"):
        # Update the information for the selected business card in the database
        cursor.execute("UPDATE ocr_results SET name=%s, job_title=%s, address=%s, postcode=%s, phone=%s, email=%s, website=%s, company_name=%s WHERE name=%s", 
                             (name, job_title, address, postcode, phone, email, website, company_name, selected_card_name))
        db.commit()
        st.success("Business card information updated in database.")

# Add a section to delete OCR results from the database
if selected == "Delete": 
   cursor.execute("SELECT * FROM ocr_results")
   results = cursor.fetchall()
   st.markdown("## Delete Extracted Information")
   result_to_delete = st.selectbox("Select result to delete", [result[1] for result in results])
   if st.button("Delete"):
      cursor.execute(f"DELETE FROM ocr_results WHERE name = '{result_to_delete}'")
      db.commit()
      st.write(f"Result '{result_to_delete}' deleted successfully.")
   
