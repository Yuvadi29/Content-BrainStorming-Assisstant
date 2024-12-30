import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fetch import get_trending_videos


# Google Sheets API Setup
def connect_to_google_sheets(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )
    client = gspread.authorize(credentials)
    return client.open(sheet_name).sheet1


def save_to_google_sheets(data, sheet_name="Content Ideas"):
    sheet = connect_to_google_sheets(sheet_name)
    for row in data:
        sheet.append_row([row["title"], row["channel"], row["views"], row["url"], row["description"]])


# Save Data
save_to_google_sheets(get_trending_videos)