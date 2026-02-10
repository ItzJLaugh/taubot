# TauBot.ai

TauBot.ai is an AI-powered chatbot for the Kappa Sigma chapter of Alpha Tau Omega fraternity. It helps members find information about upcoming events, deadlines, and chapter documents through a conversational interface.

## Features

- **Natural Language Chat**: Ask questions in plain English and get helpful responses
- **Google Calendar Integration**: Access upcoming events, meetings, and deadlines
- **Google Drive Integration**: Find and reference chapter documents
- **Streaming Responses**: Real-time response generation for a smooth experience
- **Web Interface**: Members click a link to access the chatbot

## Tech Stack

- **Frontend/Backend**: Streamlit
- **AI**: OpenAI GPT-4o
- **APIs**: Google Calendar API, Google Drive API

## Setup Instructions

### 1. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new secret key
5. Copy the key (starts with `sk-`)

### 3. Set Up Google Cloud Project

#### Create a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "New Project"
4. Name it `taubot-ai` and click "Create"

#### Enable APIs

1. In the left sidebar, go to "APIs & Services" > "Library"
2. Search for and enable:
   - **Google Calendar API**
   - **Google Drive API**

#### Create a Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name: `taubot-service-account`
4. Click "Create and Continue"
5. Skip the optional role assignment (or add "Viewer")
6. Click "Done"

#### Generate Service Account Key

1. Click on your new service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create" (this downloads the key file)
6. **Keep this file secure - never commit it to git!**

### 4. Share Google Resources with Service Account

#### Share the Fraternity Calendar

1. Open [Google Calendar](https://calendar.google.com/)
2. Find the fraternity calendar in the left sidebar
3. Click the three dots > "Settings and sharing"
4. Scroll to "Share with specific people or groups"
5. Click "Add people and groups"
6. Enter the service account email (looks like: `taubot-service-account@taubot-ai.iam.gserviceaccount.com`)
7. Set permission to "See all event details"
8. Click "Send"

#### Share the Fraternity Drive Folder

1. Open [Google Drive](https://drive.google.com/)
2. Right-click on the fraternity documents folder
3. Click "Share"
4. Enter the service account email
5. Set permission to "Viewer"
6. Click "Send"

### 5. Configure Secrets

1. Copy the example secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` with your actual values:
   - Add your OpenAI API key
   - Copy all values from your Google service account JSON file
   - Add your Google Calendar ID (found in Calendar Settings > Integrate calendar)
   - Add your Google Drive folder ID (from the folder URL)

### 6. Run the App

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push your code to GitHub (without secrets.toml)
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. In the app settings, add your secrets under "Secrets"
5. Deploy!

## Project Structure

```
TauBot.ai/
├── .streamlit/
│   ├── config.toml          # Streamlit theme settings
│   └── secrets.toml         # API keys (DO NOT COMMIT)
├── src/
│   ├── app.py               # Main Streamlit application
│   ├── config.py            # Configuration loading
│   ├── services/
│   │   ├── calendar_service.py   # Google Calendar integration
│   │   ├── drive_service.py      # Google Drive integration
│   │   └── openai_service.py     # OpenAI chat completion
│   ├── utils/
│   │   ├── context_builder.py    # Build AI context
│   │   └── date_utils.py         # Date formatting helpers
│   └── prompts/
│       └── system_prompt.py      # TauBot personality
├── .gitignore
├── requirements.txt
└── README.md
```

## Usage Examples

- "What events are coming up this week?"
- "When is the next chapter meeting?"
- "Do we have any documents about recruitment?"
- "What's happening this month?"
- "Are there any deadlines I should know about?"

## Security Notes

- Never commit `.streamlit/secrets.toml` to version control
- Never share your service account JSON file
- The service account only has read access to calendar and drive
- All API keys should be kept private

## What I Learned

- RAG (Retrieval, Augment, Generation)
- OpenAI integration
- Streamlit Frontend Development
- Google API Integration (Calendar, Drive)
