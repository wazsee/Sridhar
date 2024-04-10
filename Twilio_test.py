from flask import Flask, request, render_template_string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# Replace YOUR_CREDENTIALS_FILE.json with the path to your downloaded credentials file
# Replace YOUR_SHEET_ID with the ID of your Google Sheet
# Replace YOUR_RANGE with the range in A1 notation where mobile numbers are stored
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "C:\\Users\\satishkumar.s\\Downloads\\AutomatedDashboardReports-master - Copy\\wcommerce-415712-fd431bea1f1e.json"
SHEET_ID = '11psEafWUrytdDz-j4ymQ_RqtrNnrCgOUrEPS8XSrUIA'
RANGE_NAME = 'Sheet1!A:C'

credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Number Submission</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #4CAF50; /* A shade of green */
            font-family: 'Arial', sans-serif;
        }
        .container {
            background: #fff;
            padding: 3rem; /* Increased padding for larger form */
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px; /* Increased max-width for a larger form */
            margin-top: 20px;
        }
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 2rem; /* Increased margin for more space around the title */
        }
        form {
            display: flex;
            flex-direction: column;
        }
        label {
            margin-bottom: 0.5rem;
            color: #333;
        }
        input[type="text"], input[type="email"] {
            margin-bottom: 1.5rem; /* Increased margin for more space between fields */
            padding: 1rem; /* Increased padding for larger click area */
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 1.25rem; /* Increased font size */
            height: 50px; /* Increased height of input fields */
        }
        input[type="submit"] {
            padding: 1rem; /* Increased padding for a larger button */
            border: none;
            border-radius: 4px;
            background-color: #007bff;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 1.25rem; /* Increased font size */
            height: 50px; /* Increased height to match input fields */
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .response {
            text-align: center;
            color: #333;
            font-size: 1.2rem; /* Larger text size for the response message */
        }
    </style>
</head>
<body>
    {% if message %}
        <div class="response">{{ message }}</div>
    {% endif %}
    <div class="container">
        <h2>Submit Your Information</h2>
        <form method="post">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
            <label for="mobile_number">Mobile Number:</label>
            <input type="text" id="mobile_number" name="mobile_number" required>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
            <input type="submit" value="Submit">
        </form>
    </div>
</body>
</html>

"""


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        if check_number_exists(mobile_number):
            return "Mobile number already exists."
        else:
            add_info_to_sheet(name, mobile_number, email)
            return "Your submission has been received."
    return render_template_string(FORM_HTML)


def check_number_exists(number):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        return False
    for row in values:
        # Assuming mobile numbers are in the first column
        if number in row:
            return True
    return False

def add_info_to_sheet(name, number, email):
    values = [[name, number, email]]  # Adjust the order and content as needed
    body = {'values': values}
    result = service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID, range="Sheet1",  # Specify the target sheet and a more specific range if necessary
        valueInputOption='RAW', body=body, insertDataOption='INSERT_ROWS').execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")


if __name__ == '__main__':
    app.run(debug=True)
