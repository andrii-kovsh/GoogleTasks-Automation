from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz
import os
import pickle
import re

# Визначення поточного часу з урахуванням часової зони
timezone = pytz.timezone("Europe/Kyiv")
now = datetime.now(timezone)

# Авторизація та підключення до API
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

# Функція для перенесення задачі в інший список із збереженням дедлайну
def move_task_to_another_list(task_service, task_id, current_task_list_id, new_task_list_id):
    # Отримуємо задачу з поточного списку
    task = task_service.tasks().get(tasklist=current_task_list_id, task=task_id).execute()

    # Зберігаємо дедлайн без часу (отримуємо тільки дату)
    due_date = task.get('due', None)

    # Перетворюємо час з нотаток у формат HH:MM
    task_time = None
    if 'notes' in task:
        task_time = convert_notes_to_due_time(task['notes'])
        print(f"Час з нотаток: {task_time}")
    
    # Видаляємо зайві атрибути для вставки
    for key in ['id', 'etag', 'selfLink', 'position', 'updated']:
        task.pop(key, None)

    # Додаємо дедлайн, якщо він був присутній
    if due_date:
        task['due'] = due_date

    # Додаємо час із нотаток (якщо він є) у новий опис (notes)
    if task_time:
        task['notes'] = f"📅 Час дедлайну: {task_time}"

    # Створюємо завдання в новому списку з дедлайном
    new_task = task_service.tasks().insert(tasklist=new_task_list_id, body=task).execute()
    print(f"Задачу '{new_task['title']}' перенесено в новий список: {new_task_list_id} із дедлайном {new_task.get('due', 'без дедлайну')}")

    # Видаляємо оригінальне завдання з поточного списку
    task_service.tasks().delete(tasklist=current_task_list_id, task=task_id).execute()

# Функція для перетворення часу з нотаток у формат HH:MM на текст
def convert_notes_to_due_time(notes):
    # Шукаємо час у форматі HH:MM в нотатках
    match = re.search(r'(\d{2}):(\d{2})', notes)
    if match:
        return match.group(0)  # Повертаємо знайдений час
    return None  # Якщо час не знайдений

# Функція для перевірки та перенесення задачі, якщо наближається дедлайн
def move_event_if_near_deadline(task_service, task_list_ids, new_task_list_id):
    now = datetime.now(pytz.timezone("Europe/Kyiv"))
    print(f"Перевіряємо задачі на наявність дедлайну до {now}")

    for task_list_id in task_list_ids:
        tasks = task_service.tasks().list(tasklist=task_list_id).execute().get('items', [])

        for task in tasks:
            print(f"Перевіряємо задачу: {task['title']}")
            if 'due' in task:
                due_date_str = task['due']
                due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                due_date = pytz.utc.localize(due_date)

                # Переносимо задачу в новий список, якщо наближається до дедлайну
                if now + timedelta(days=3) >= due_date:
                    print(f"Задача '{task['title']}' наближається до дедлайну: {due_date}")
                    move_task_to_another_list(task_service, task['id'], task_list_id, new_task_list_id)
                else:
                    print(f"Задача '{task['title']}' не переноситься (дедлайн ще не наближається).")

def main():
    try:
        task_service, calendar_service = get_authenticated_service()

        # Перелік ID списків задач, з яких ви хочете переносити задачі
        task_list_ids = ['bkF6Njh0Z0VNR2gtZzloYw', 'UXJkNEhDOFNuVXUwU2JLSg', 'Sl9xOHloVFpFOHg1VTNuUg']
        new_task_list_id = 'MTY0MDIzMzk3NjY5NDgyOTE5NjI6MDow'

        # Перевірка задач на наближення дедлайну
        move_event_if_near_deadline(task_service, task_list_ids, new_task_list_id)
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()