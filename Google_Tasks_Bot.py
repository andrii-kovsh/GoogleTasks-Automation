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

# Function to dynamically fetch primary and secondary task lists
def get_primary_and_secondary_lists(task_service):
    try:
        task_lists = task_service.tasklists().list().execute().get('items', [])
        if not task_lists:
            print("No task lists found.")
            return None, None

        primary_list_id = task_lists[0]['id']  # First list as primary
        secondary_list_ids = [(task_list['id'], task_list['title']) for task_list in task_lists[1:]]  # All others as secondary

        return primary_list_id, secondary_list_ids
    except HttpError as error:
        print(f"An error occurred while fetching task lists: {error}")
        return None, None

# Function to move a task to the primary list and preserve its deadline
def move_task_to_primary_list(task_service, task_id, current_task_list_id, primary_task_list_id, current_task_list_name):
    task = task_service.tasks().get(tasklist=current_task_list_id, task=task_id).execute()
    due_date = task.get('due', None)

    # Extract due time from notes, if present
    task_time = None
    if 'notes' in task:
        task_time = convert_notes_to_due_time(task['notes'])

    # Remove unnecessary fields for insertion
    for key in ['id', 'etag', 'selfLink', 'position', 'updated']:
        task.pop(key, None)

    # Set the due date and add notes with time if applicable
    if due_date:
        task['due'] = due_date
    if task_time:
        task['notes'] = f"📅 Deadline time: {task_time}"

    # Insert task in the primary list
    new_task = task_service.tasks().insert(tasklist=primary_task_list_id, body=task).execute()
    print(f"Moved task '{new_task['title']}' with deadline {new_task.get('due', 'no deadline')} from '{current_task_list_name}' to the primary list.")

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


    # Додаємо повідомлення, якщо немає завдань для переносу
    if not tasks_moved:
        print("Ніяких завдань не перенесено, насолоджуйся днем ☀️")

# Main function to authenticate and run the task moving logic
def main():
    try:
        task_service, _ = get_authenticated_service()

        # Dynamically fetch primary and secondary task list IDs
        primary_task_list_id, secondary_task_list_ids = get_primary_and_secondary_lists(task_service)

        # Ensure that we have a primary list and at least one secondary list
        if primary_task_list_id and secondary_task_list_ids:
            # Check for deadlines and move tasks as necessary
            move_tasks_nearing_deadline(task_service, primary_task_list_id, secondary_task_list_ids)
        else:
            print("Unable to proceed without both primary and secondary task lists.")
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()