import streamlit as st
import os
import glob


st.title('LPRNet Annotation')
st.sidebar.title("Settings")
col1, col2 = st.columns(2)

if 'counter' not in st.session_state: 
    st.session_state.counter = 0

side_bar =  st.sidebar.form("my_form")
imgs_dir = side_bar.text_input('Path to Images')
is_imgs_dir = os.path.exists(imgs_dir)
# print(imgs_path)
txts_dir = side_bar.text_input('Path to Labels')
is_txts_dir = os.path.exists(txts_dir)
# print(txts_path)
start = side_bar.form_submit_button("Submit")
# print(submit)

if start:
    if not is_imgs_dir:
        side_bar.error(f"[ERROR] {imgs_dir} not exit")
    else:
        side_bar.success(f"[INFO] Loaded {imgs_dir}")
    
    if not is_txts_dir:
        side_bar.error(f"[ERROR] {txts_dir} not exit")
        os.makedirs(txts_dir, exist_ok=True)
        side_bar.success(f"[INFO] Created {txts_dir}")
    else:
        st.success(f"[INFO] Loaded {txts_dir}")

if is_imgs_dir:
    img_list = glob.glob(os.path.join(imgs_dir, "*.jpg")) + \
               glob.glob(os.path.join(imgs_dir, "*.jpeg")) + \
               glob.glob(os.path.join(imgs_dir, "*.png"))
    img_list = sorted(img_list)
    def showPhoto(photo):
        col1.image(photo,caption=photo)
        col1.write(f"Index as a session_state attribute: {st.session_state.counter}")
        
        ## Increments the counter to get next photo
        st.session_state.counter += 1
        if st.session_state.counter >= len(img_list):
            st.session_state.counter = 0

    # col1.subheader("List of images in folder")
    # col1.write(img_list)

    # Select photo a send it to button
    name = os.path.splitext(os.path.split(img_list[st.session_state.counter-1])[1])[0]
    img_path = img_list[st.session_state.counter]
    # print(img_list, imgs_path)
    # for img_path in img_list:
    #     # img_path = img_list[0]
    txt_name = name + ".txt"
    txt_path = os.path.join(txts_dir, txt_name)
    # with col1:
    # col1.subheader(img_path)
    # col1.image(img_path)
    # with col3:
    col2.subheader(txt_name)
    # is_txt_path = os.path.exists(txt_path)
    file_txt = open(txt_path, 'w+')
    number_plate = file_txt.read()
    anot_txt = col2.text_input('number_plate', number_plate)

    show_btn = col2.button("Show next Image ⏭️",on_click=showPhoto,args=([img_path]))
    
    if st.button("Submit"):
        print(anot_txt, type(anot_txt))
        file_txt.write(anot_txt)
        file_txt.close()
    