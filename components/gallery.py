import streamlit as st
from config import t

def render_gallery():
    with st.expander(t("gallery_title")):
        c1, c2 = st.columns(2)
        with c1:
            st.image("https://agrihunt.com/images/crops/tomato_healthy.jpg", caption="صحت مند")
        with c2:
            st.image("https://agrihunt.com/images/crops/tomato_disease.jpg", caption="بیمار")
