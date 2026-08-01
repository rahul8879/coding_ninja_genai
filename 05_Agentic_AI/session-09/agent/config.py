from dotenv import load_dotenv
import os
load_dotenv()

ORGANIZER_EMAIL = "rtiwarirahul123@gmail.com"
ALLOW_DUPLICATE_EVENTS = True
DATA_DIR = os.path.join("data")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR_CREDENTIALS_PATH = os.path.join(
    PROJECT_ROOT, "calendar-server", "gcp-oauth.keys.json"
)


MCP_SERVERS = {
    "ats": {
        "command" :"python",
        "args": [os.path.join( "server", "server.py")],
         "transport": "stdio",

    },
    "calendar": {
        "command": "npx",
         "args": ["@cocal/google-calendar-mcp"],
          "transport": "stdio",
          "env": {"GOOGLE_OAUTH_CREDENTIALS": CALENDAR_CREDENTIALS_PATH, **os.environ}

    },

     "email": {
        "command": "npx",
        "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
        "transport": "stdio",
    }
}



