# 📅Google Tasks Automation

This project automates task management by interacting with the Google Tasks API. It moves tasks between task lists based on their deadlines and transfers relevant information, including the due date and time, if provided in the task notes.

## 🛠️Features
- Automatically moves tasks approaching their deadlines to a new task list.
- Retains the due date information when transferring tasks.
- Parses task notes for any specified time and adds it to the new task as "📅 Deadline time: HH:MM".
- Deletes the original task after it has been moved.

## 📃Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google API Authentication](#google-api-authentication)
3. [How It Works](#how-it-works)
4. [Example Output](#example-output)
5. [Contributing](#contributing)

## 📦Prerequisites

Before you can use this script, make sure you have the following:

1. **Google Account**
   You need a Google account to use Google APIs (Tasks API and Calendar API).

2. **Install Python 3.7 or higher**
   The script is written in Python. You need to have Python 3.7 or above installed.

3. **Required Python Libraries**:
   The following Python libraries are required:
   - `google-auth`
   - `google-auth-oauthlib`
   - `google-auth-httplib2`
   - `google-api-python-client`
   - `pytz`
   - `datetime`
   
   Install these libraries using `pip`:
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz

4. **Google Developer Console Setup**
You need to create credentials for accessing Google APIs:
- Go to [Google Developer Console](https://console.developers.google.com/).
- Create a project and enable the **Google Tasks API** and **Google Calendar API**.
- Download the `credentials.json` file.
- Make sure to store this `credentials.json` in your project folder.

## 🔒Google API Authentication

1. **Create Google API Credentials**
- Go to the [Google Developer Console](https://console.developers.google.com/).
- Create a new project or select an existing one.
- Enable the **Google Tasks API** and **Google Calendar API**.
- In the **Credentials** section, create **OAuth 2.0 credentials** for a desktop app.
- Download the **credentials.json** file and place it in your project directory.

2. **Authenticate API Requests**
- The first time you run the script, it will prompt you to log in to your Google account and allow the necessary permissions.
- The credentials are stored in a `token.pickle` file for subsequent uses, so you don't have to authenticate every time.

## ⚙️How It Works

1. The script checks tasks in your Google Task lists.
2. It scans tasks to identify those that have deadlines and are approaching within 3 days.
3. The script checks the task notes for any time in the `HH:MM` format and moves it as part of the due date information.
4. Tasks are then moved to a specified task list with the updated due date and time, if available.
5. The original task is deleted after being moved.

The key function, `move_event_if_near_deadline`, performs the task scanning and moves the tasks if they meet the deadline criteria.

## 📝Example Output

Checking task: Test Task Task due date: 2024-11-08 Task 'Test Task' is approaching its deadline: 2024-11-08 Task 'Test Task' moved to the new list. Task 'Test Task' deleted from the original list.
1. The script checks all tasks for deadlines up to a specific date and time (`2024-11-07 06:40:13`).
2. It finds the task `Test Task` with a due date of `2024-11-08`.
3. The task is identified as approaching its deadline and is moved to a new task list.
4. After the task is successfully moved, it is deleted from the original list.

If a task is moved, you will see messages confirming both the move and the deletion process. This ensures that your task management is automated smoothly.

## 💡Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository.
2. **Clone** your fork to your local machine.
3. **Create a new branch** for your changes.
4. **Make your changes** and test them.
5. **Commit** your changes and push them to your fork.
6. **Create a pull request**.

That's it! Thanks for helping improve this project!
