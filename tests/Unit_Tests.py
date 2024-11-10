import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pytz
from Google_Tasks_Bot import (
    get_authenticated_service,
    get_task_list_ids,
    move_task_to_another_list,
    convert_notes_to_due_time,
    move_event_if_near_deadline,
    clear_all_tasks
)

class TestGoogleTasksFunctions(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Authenticate and set up the service."""
        cls.task_service, _ = get_authenticated_service()
        cls.task_list_ids = get_task_list_ids(cls.task_service)
    
    def setUp(self):
        """Clear tasks before each test to start with a clean slate."""
        clear_all_tasks(self.task_service, self.task_list_ids)

    @patch('Google_Tasks_Bot.get_task_list_ids')
    def test_get_task_list_ids(self, mock_task_service):
        mock_task_service.tasklists().list().execute.return_value = {
            'items': [{'id': 'tasklist1'}, {'id': 'tasklist2'}]
        }
        task_service = MagicMock()
        task_list_ids = get_task_list_ids(task_service)
        self.assertEqual(task_list_ids, ['tasklist1', 'tasklist2'])

    @patch('Google_Tasks_Bot.move_task_to_another_list')
    def test_move_task_to_another_list(self, mock_task_service):
        mock_task_service.tasks().get().execute.return_value = {
            'title': 'Test Task',
            'due': '2024-11-10T12:00:00.000Z',
            'notes': 'Due by 12:00',
        }
        mock_task_service.tasks().insert().execute.return_value = {
            'title': 'Test Task'
        }
        move_task_to_another_list(
            mock_task_service,
            task_id='test_id',
            current_task_list_id='list1',
            new_task_list_id='list2'
        )
        mock_task_service.tasks().insert.assert_called_once()
        mock_task_service.tasks().delete.assert_called_once()

    def test_convert_notes_to_due_time(self):
        notes_with_time = "This task is due at 15:30."
        self.assertEqual(convert_notes_to_due_time(notes_with_time), '15:30')
        
        notes_without_time = "No time specified here."
        self.assertIsNone(convert_notes_to_due_time(notes_without_time))

    @patch('Google_Tasks_Bot.move_task_to_another_list')
    def test_move_event_if_near_deadline(self, mock_move_task_to_another_list):
        task_service = MagicMock()
        task_service.tasks().list().execute.return_value = {
            'items': [
                {'id': 'task1', 'title': 'Urgent Task', 'due': '2024-11-11T12:00:00.000Z'},
                {'id': 'task2', 'title': 'Later Task', 'due': '2024-12-01T12:00:00.000Z'}
            ]
        }
        timezone = pytz.timezone("Europe/Kyiv")
        now = datetime.now(timezone)
        move_event_if_near_deadline(task_service, ['list1'], 'new_list')
        mock_move_task_to_another_list.assert_called_once_with(
            task_service, 'task1', 'list1', 'new_list'
        )

    def tearDown(self):
        """Clean up tasks after each test."""
        clear_all_tasks(self.task_service, self.task_list_ids)

if __name__ == '__main__':
    unittest.main()