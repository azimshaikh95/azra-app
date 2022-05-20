import google_auth_httplib2
import httplib2
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
# SPREADSHEET_ID = "1QlPTiVvfRM82snGN6LELpNkOwVI1_Mp9J9xeJe-QoaA"
# SPREADSHEET_ID = "1SC-4sbuUVG7FEb0gz1ishGk-Uk-7N5zVu1CmgTOqesw"
SHEET_NAME = "Database"
# GSHEET_URL = f"https://docs.google.com/spreadsheets/d/st.secrets["SPREADSHEET_ID"]"
GSHEET_URL = st.secrets["private_gsheets_url"]


@st.experimental_singleton()
def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[SCOPE],
    )

    # Create a new Http() object for every request
    def build_request(http, *args, **kwargs):
        new_http = google_auth_httplib2.AuthorizedHttp(
            credentials, http=httplib2.Http()
        )
        return HttpRequest(new_http, *args, **kwargs)

    authorized_http = google_auth_httplib2.AuthorizedHttp(
        credentials, http=httplib2.Http()
    )
    service = build(
        "sheets",
        "v4",
        requestBuilder=build_request,
        http=authorized_http,
    )
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


def get_data(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=st.secrets["SPREADSHEET_XID"],
            range=f"{SHEET_NAME}!A:E",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def add_row_to_gsheet(gsheet_connector, row) -> None:
    gsheet_connector.values().append(
        spreadsheetId=st.secrets["SPREADSHEET_XID"],
        range=f"{SHEET_NAME}!A:E",
        body=dict(values=row),
        valueInputOption="USER_ENTERED",
    ).execute()


st.set_page_config(page_title="Youngsters of Markaz", page_icon="🌴", layout="centered")

st.title("️🌴 Youngsters Picnic ! 🌳")

gsheet_connector = connect_to_gsheet()

# st.sidebar.write(
    # f"This app is made for Youngsters of Markaz Picnic Program [Google Sheet]({GSHEET_URL}) to register the names of youngsters."
# )

# st.sidebar.write(
    # f"[Read more](https://docs.streamlit.io/knowledge-base/tutorials/databases/public-gsheet) about connecting your Streamlit app to Google Sheets."
# )

form = st.form(key="annotation")

with form:
    cols = st.columns((1, 1))
    y_name = cols[0].text_input("Name:")
    y_address = cols[1].selectbox(
        "Address:", ["Tawakkal Villa", "Back-end", "Data related", "404"], index=2
    )
   
    cols = st.columns(2)
    date = cols[0].date_input("Date of Registration:")
    y_age = cols[1].slider("Age:", 12, 30, 15)
    comment = st.text_area("Comment:")
    submitted = st.form_submit_button(label="Register")


if submitted:
    add_row_to_gsheet(
        gsheet_connector,
        [[y_name, y_address, comment, str(date), y_age]],
    )
    st.success("Thanks! Your data has recorded!")
    st.balloons()

expander = st.expander("See all records")
with expander:
    # st.write(f"Open original [Google Sheet]({GSHEET_URL})")
    st.dataframe(get_data(gsheet_connector))
