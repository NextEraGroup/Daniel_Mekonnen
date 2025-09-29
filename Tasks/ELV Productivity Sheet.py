# tasks/task_1.py
import streamlit as st
import os

def run():
    st.subheader("📊 ELV Productivity Sheet")
    st.markdown("Download the official ELV productivity tracking Excel sheet.")

    file_path = "data/productivity.xlsx"

    # Preview if file exists
    if os.path.exists(file_path):
        # Download button
        with open(file_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Productivity Excel",
                data=f,
                file_name="ELV_Productivity.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Optional preview inside Streamlit
        import pandas as pd
        df = pd.read_excel(file_path)
        st.dataframe(df, use_container_width=True)

    else:
        st.error("❌ Productivity sheet not found. Please upload it to `data/productivity.xlsx`")
