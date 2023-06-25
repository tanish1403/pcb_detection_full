import os
import subprocess
import streamlit as st
import sys
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="PCB detection", layout="wide",page_icon="assets/icon.png")

def run_image_processing(file):
    # Define your image processing logic here
    cache = 'cache'
    weights = "pcb_detection.pt" 
    detectorScript = "detect.py"

    cacheAbsolutePath = os.path.join(os.getcwd(), cache)
    if not os.path.exists(cacheAbsolutePath):
        os.makedirs(cacheAbsolutePath)
    detectPath = os.path.join(cacheAbsolutePath, 'detect')
    if not os.path.exists(detectPath):
        os.makedirs(detectPath)
    filepath = os.path.join(cacheAbsolutePath, file)
    try:
        python_executable = sys.executable
        #add iamge size
        subprocess.run([python_executable , detectorScript, '--source', filepath, '--weights', weights, '--conf', '0.25', '--name', 'detect', '--exist-ok', '--project', cacheAbsolutePath, "--no-trace"])
    
        # subprocess.run([python_executable, detectorScript, "--weights", weights, "--source", filepath, "--img-size", "416", "--save-txt", "--save-conf", "--save-crop", "--nosave", "--exist-ok", "--project", cacheAbsolutePath, "--name", "detect"])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the subprocess: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    return True

def resize_image(image_path, max_width):

    # Open the image using Pillow
    image = Image.open(image_path)

    # Get the original dimensions
    width, height = image.size

    # Calculate the new height while maintaining the aspect ratio
    new_width = max_width
    new_height = int(height * (new_width / width))

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    # Save the resized image
    resized_image.save(image_path)

def process_uploaded_image(uploaded_file):
    
    saveDir = os.path.join(os.getcwd(), 'cache')

    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    

    fileExtension=uploaded_file.name.split(".")[-1]
    fileName = "1."+fileExtension
    savePath = os.path.join(saveDir, fileName)

    with open(savePath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    resize_image(savePath, 1000)
    reponse = run_image_processing(fileName)

    if not reponse:
        return False

    output_filepath=os.path.join(os.getcwd(),"cache/detect",fileName)
    col1,col2 = st.columns(2)

    with col1:
        st.image(output_filepath, caption="Processed Image")
    with col2:
        st.image(uploaded_file, caption="Original Image")

    return True

def handle_detection_ui():
    col1,col2= st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png","webp"],key=f"fileUploader")
        # Image processing button
        response = False
        buttonPressed = st.button("Process Image",key=f"buton@fileUplaod")
    if buttonPressed and uploaded_file is not None:
        # saving this file to a temporary location
        response = process_uploaded_image(uploaded_file)
    with col2:
        if not response and uploaded_file:
            st.caption("Uploaded Image")
            st.image(uploaded_file)

def load_heading():
    st.image("assets/head.png")
    st.markdown("### ⚡️ PCB Fault Identification Application")

def load_info():
    st.markdown("Welcome to our Streamlit-based interface engineered specifically for the analysis of Printed Circuit Board (PCB) images. Our sophisticated application harnesses advanced image processing to detect an array of PCB defects with significant accuracy. ")
    st.caption("This application serves as a demonstration of the capabilities inherent in our state-of-the-art PCB defect detection model. Its primary function is to validate the model's effectiveness and showcase its potential for practical implementation.")

    st.markdown("Our system is currently equipped to identify the following categories of defects:")
    cols = st.columns(8) 
    
    defects = ["Missing Holes","Mouse Bites" ,"Open Circuit", "Short","Spur","Spurious Copper"]
    for index, defect in enumerate(defects):
        with cols[index]:
            st.info(defect)
    
    st.markdown("---")
    st.markdown("##### ⚙️ About Model")
    st.markdown("The model used for this application is a [YOLOv7](https://github.com/WongKinYiu/yolov7). The model was trained for 100 epochs. To download the weights, click [here](https://drive.google.com/file/d/1HhgrRnlixFtZlZA_E19eW7wVro818Kfk/view?usp=sharing)")
    
    st.markdown("---")
    st.markdown("##### 🛄️ About Dataset")
    st.markdown(" model trained on the [PCB dataset](https://www.kaggle.com/datasets/akhatova/pcb-defects) from kaggle.")

    st.markdown("---")
    st.markdown("##### 🌟️ Performance")
    st.caption("The model has an mAP of 0.9 on the validation set.")
    st.markdown("> Losses after 100 epochs")
    st.markdown("""
| Loss | Validation | Train |
| ----------- | ----------- | ----------- |
| Box Loss | 0.07389 | 0.01253 |
| Object Loss | 0.007394 | 0.004433 |
| Class Loss | 0.01108 | 0.0007131 |
""")
    st.markdown("> Graphs")
    cf,dumb,dumb = st.columns(3)
    with cf:
        st.image("assets/cf.png",caption="Confusion Matrics")
    pr,dumb,dumb = st.columns(3)
    with pr :
        st.image("assets/pr.png", caption="Precision Recall")

def main():
    tab1, tab2 = st.tabs(["About", "Try it out"])
    with tab1:
        load_heading()
        load_info()
    with tab2:
        handle_detection_ui()
if __name__ == "__main__":
    main()