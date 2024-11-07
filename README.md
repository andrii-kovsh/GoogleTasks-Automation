# Google Tasks Automation

This project automates the management of tasks in Google Tasks. It moves tasks that are approaching their deadline to a new list, while preserving the task details (such as due date and description) and updating them accordingly. The task's time, if present in the notes, will be extracted and added to the new task in a custom format.

## Features

- **Move tasks based on deadlines**: Tasks approaching their deadlines will be moved to a new list.
- **Preserve due date**: The task's due date will be retained when it is moved.
- **Extract time from notes**: If a time (HH:MM) is found in the notes of the original task, it will be added to the new task description in the format `📅 Due time: HH:MM`.
- **Delete the original task**: Once the task is moved to the new list, the original task is deleted.

## Prerequisites

1. **Python 3.x**: Make sure Python is installed on your system.
2. **Google API credentials**: You need to enable the Google Tasks API and Google Calendar API, and download the `credentials.json` file. 
3. **Install required Python libraries**:
   - `google-api-python-client`
   - `google-auth-httplib2`
   - `google-auth-oauthlib`
   - `pytz`

You can install the required dependencies by running:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pytz
