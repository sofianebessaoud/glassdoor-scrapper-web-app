import datetime

import pandas as pd
import streamlit as st

import data_cleaning
import map_view
import scraper

# Set page width to full width
st.set_page_config(
    page_title="Custom Button Example", page_icon=":guardsman:", layout="wide"
)

# Add font stylesheet
url = "https://fonts.googleapis.com/css?family=Montserrat:900"
st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

# Add custom CSS stylesheet
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Define page title and introductory text
_, col22, _ = st.columns(3)
with col22:
    st.title(" :mushroom: Jobs Scraper :mushroom:")
    st.write("Welcome to the Homemade Glassdoor Job Scraper! ")
    st.write(
        " :speech_balloon: Choose your options and you will be ready to go :speech_balloon: "
    )

# Add text inputs for job name, location, and number of jobs to scrape
col1, col2, col3 = st.columns(3)

with col1:
    job_name = st.text_input("job_name", value="data scientist intern")

with col2:
    job_location = st.text_input("job_location", value="United States")

with col3:
    job_number = st.number_input("jobs_number", value=100)

st.write("")

# Check if jobs have been scrapped and cleaned
if "scrapped" not in st.session_state:
    st.session_state["scrapped"] = False

if "cleaned" not in st.session_state:
    st.session_state["cleaned"] = False

# Add button to initiate job scraping
if st.button("Scrap Jobs"):
    date = datetime.datetime.now()
    st.session_state["date"] = date
    time = int(2 * job_number / 60)
    time_change = datetime.timedelta(time)
    st.write(
        f" :speech_balloon: The {job_number} jobs are being scrapped. "
        f"It will take approximately "
        + str(time)
        + " minutes. Go grab a cup of coffee :coffee: "
        "and come back around "
        + (date + time_change).strftime("%H:%M:%S")
        + " to check the results! :speech_balloon: "
    )

    df = scraper.get_jobs(job_name, job_location, int(job_number))
    df.to_excel(f"output/raw_output/raw_output_{date}.xlsx")
    st.write(f"the output was saved under reference raw_output_{date}.xlsx")
    st.session_state["scrapped"] = True

    st.dataframe(df)
    st.write("")

# Add button to clean scrapped data
if st.session_state["scrapped"]:
    if st.button("Clean scrapped data"):
        st.session_state["cleaned"] = True

# Add button to clean and output data
if st.session_state["scrapped"] and st.session_state["cleaned"]:
    raw_output_df = pd.read_excel(
        f'output/raw_output/raw_output_{st.session_state["date"]}.xlsx', index_col=0
    )

    st.write("cleaning output")
    cleaned_df = data_cleaning.data_cleaning_pipeline(raw_output_df)
    cleaned_df.to_excel(
        f'output/cleaned_output/cleaned_output_{st.session_state["date"]}.xlsx'
    )
    st.write("cleaned output saved")
    st.dataframe(
        cleaned_df[
            [
                "company_name",
                "location",
                "job_title",
                "purchasing_power",
                "job_description",
            ]
        ]
    )

# Add button to clean scrapped data
if st.session_state["scrapped"]:
    if st.session_state["cleaned"]:
        if st.button("Show top 10 job offers"):
            df = (
                pd.read_excel(
                    f'output/cleaned_output/cleaned_output_{st.session_state["date"]}.xlsx',
                    index_col=0,
                )
                .sort_values("purchasing_power", ascending=False)
                .head(10)
            )
            st.write("These job offers are remote:")
            st.dataframe(
                df[df.location == "Remote"][
                    [
                        "company_name",
                        "location",
                        "job_title",
                        "purchasing_power",
                        "job_description",
                    ]
                ]
            )
            map_view.map_view(df)
