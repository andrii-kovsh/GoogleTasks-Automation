from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pytz
import os
import pickle
import re

# Define timezone
timezone = pytz.timezone("Europe/Kyiv")
now = datetime.now(timezone)

# Authenticate and connect to the Google API
def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/tasks', 'https://www.googleapis.com/auth/calendar']
            )
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('tasks', 'v1', credentials=creds), build('calendar', 'v3', credentials=creds)

# Function to dynamically fetch all task list IDs
def get_task_list_ids(task_service):
    task_lists = task_service.tasklists().list().execute().get('items', [])
    return [task_list['id'] for task_list in task_lists]

# Function to move a task to a new list and preserve its deadline
def move_task_to_another_list(task_service, task_id, current_task_list_id, new_task_list_id):
    task = task_service.tasks().get(tasklist=current_task_list_id, task=task_id).execute()
    due_date = task.get('due', None)

    # Extract due time from notes, if present
    task_time = None
    if 'notes' in task:
        task_time = convert_notes_to_due_time(task['notes'])
        print(f"Time from notes: {task_time}")

    # Remove unnecessary fields for insertion
    for key in ['id', 'etag', 'selfLink', 'position', 'updated']:
        task.pop(key, None)

    # Set the due date and add notes with time if applicable
    if due_date:
        task['due'] = due_date
    if task_time:
        task['notes'] = f"📅 Deadline time: {task_time}"

    # Insert task in the new list
    new_task = task_service.tasks().insert(tasklist=new_task_list_id, body=task).execute()
    print(f"Task '{new_task['title']}' moved to new list: {new_task_list_id} with deadline {new_task.get('due', 'no deadline')}")

    # Delete the original task from the old list
    task_service.tasks().delete(tasklist=current_task_list_id, task=task_id).execute()

# Function to convert time from notes to HH:MM format
def convert_notes_to_due_time(notes):
    match = re.search(r'(\d{2}):(\d{2})', notes)
    if match:
        return match.group(0)
    return None

# Function to check and move tasks nearing deadline
def move_tasks_nearing_deadline(task_service, primary_task_list_id, secondary_task_list_ids):
    now = datetime.now(pytz.timezone("Europe/Kyiv"))
    tasks_moved = False  # Прапорець для перевірки, чи є перенесені завдання

    for task_list_id, task_list_name in secondary_task_list_ids:
        tasks = task_service.tasks().list(tasklist=task_list_id).execute().get('items', [])

        for task in tasks:
            if 'due' in task:
                due_date_str = task['due']
                due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                due_date = pytz.utc.localize(due_date)

                # Перевіряємо, чи наближається дедлайн, і переміщуємо завдання
                if now + timedelta(days=3) >= due_date:
                    move_task_to_primary_list(task_service, task['id'], task_list_id, primary_task_list_id, task_list_name)
                    tasks_moved = True  # Позначаємо, що хоча б одне завдання було перенесене

    # Додаємо повідомлення, якщо немає завдань для переносу
    if not tasks_moved:
        print("Ніяких завдань не перенесено, насолоджуйся днем ☀️")

# Clear all the test data before running script

def clear_all_tasks(task_service, task_list_ids):
    """Clear all tasks from the provided task list IDs."""
    for task_list_id in task_list_ids:
        tasks = task_service.tasks().list(tasklist=task_list_id).execute().get('items', [])
        for task in tasks:
            task_service.tasks().delete(tasklist=task_list_id, task=task['id']).execute()
        print(f"Cleared all tasks from list: {task_list_id}")

# Main function to authenticate and run the task moving logic
def main():
    try:
        task_service, calendar_service = get_authenticated_service()

        # Dynamically fetch task list IDs
        task_list_ids = get_task_list_ids(task_service)
        new_task_list_id = 'YOUR_NEW_TASK_LIST_ID'  # Replace with the actual ID of the destination list

        # Check for deadlines and move tasks
        move_event_if_near_deadline(task_service, task_list_ids, new_task_list_id)
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()