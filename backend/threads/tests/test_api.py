from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from django.urls import reverse

from threads.models import Thread
from threads.service import MessageService, ThreadService, UserUnreadMessages
from threads.tests.factories import UserFactory


class TestThreadAPI(APITestCase):
    create_retrieve_url = 'threads:thread-create-retrieve'
    list_thread_url_name = 'threads:thread-list'
    delete_thread_url_name = 'threads:thread-delete'
    create_message_url_name = 'threads:create-list-message'
    retrieve_message_url_name = 'threads:retrieve-message'
    retrieve_unread_messages_url_name = 'threads:retrieve-unread-messages'
    thread_service = ThreadService()
    message_service = MessageService()

    def setUp(self):
        self.user_1 = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()
        self.client.force_authenticate(self.user_1)

    def create_thread(self, participants: list[int], creator_id: int) -> Thread:
        return self.thread_service.create_thread_with_participants(
            creator_id=creator_id,
            participants=participants,
        )

    def create_message(self, thread: Thread, sender_id: int, content: str):
        return self.message_service.create_message(
            sender_id=sender_id,
            content=content,
            thread=thread,
        )

    def test_create_thread(self):
        url = reverse(self.create_retrieve_url)
        with CaptureQueriesContext(connection):
            response = self.client.post(
                url,
                data={
                    'participants': [self.user_2.id, self.user_3.id],
                },
            )
        self.assertEqual(response.status_code, 201)

    def test_cant_create_thread_with_more_then_2_participants(self):
        url = reverse(self.create_retrieve_url)
        with CaptureQueriesContext(connection):
            response = self.client.post(
                url,
                data={
                    'participants': [self.user_2.id, self.user_3.id, self.user_1.id],
                },
            )
            self.assertEqual(response.status_code, 400)

    def test_delete_thread(self):
        thread = self.create_thread([self.user_1.id, self.user_2.id], self.user_1.id)
        delete_url = reverse(self.delete_thread_url_name, kwargs={'pk': thread.id})
        with CaptureQueriesContext(connection):
            response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 204)

    def test_delete_forbidden_thread(self):
        thread = self.create_thread([self.user_2.id, self.user_3.id], self.user_2.id)
        delete_url = reverse(self.delete_thread_url_name, kwargs={'pk': thread.id})
        with CaptureQueriesContext(connection):
            response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 403)

    def test_get_list_thread_without_participants(self):
        list_url = reverse(self.list_thread_url_name)
        with CaptureQueriesContext(connection):
            response = self.client.get(list_url)
        self.assertEqual(response.status_code, 400)

    def test_get_list_thread(self):
        self.create_thread([self.user_1.id, self.user_2.id], self.user_1.id)
        self.create_thread([self.user_2.id, self.user_3.id], self.user_2.id)
        list_url = reverse(self.list_thread_url_name)
        with CaptureQueriesContext(connection):
            response = self.client.get(list_url, data={'participants': [self.user_1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        with CaptureQueriesContext(connection):
            response = self.client.get(list_url, data={'participants': [self.user_2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_message(self):
        thread = self.create_thread([self.user_1.id, self.user_2.id], self.user_1.id)
        create_message_url = reverse(self.create_message_url_name, kwargs={'pk': thread.id})
        with CaptureQueriesContext(connection):
            response = self.client.post(
                create_message_url,
                data={
                    'content': 'Test message',
                },
            )
        self.assertEqual(response.status_code, 201)

    def test_create_message_forbidden(self):
        thread = self.create_thread([self.user_2.id, self.user_3.id], self.user_2.id)
        create_message_url = reverse(self.create_message_url_name, kwargs={'pk': thread.id})
        with CaptureQueriesContext(connection):
            response = self.client.post(
                create_message_url,
                data={
                    'content': 'Test message',
                },
            )
        self.assertEqual(response.status_code, 403)

    def test_get_list_messages_for_thread(self):
        thread = self.create_thread([self.user_1.id, self.user_2.id], self.user_1.id)
        self.create_message(thread, self.user_1.id, 'Test message')
        list_message_url = reverse(self.create_message_url_name, kwargs={'pk': thread.id})
        with CaptureQueriesContext(connection):
            response = self.client.get(list_message_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_message(self):
        thread = self.create_thread([self.user_1.id, self.user_2.id], self.user_1.id)
        message = self.create_message(thread, self.user_2.id, 'Test message')
        retrieve_message_url = reverse(self.retrieve_message_url_name, kwargs={'pk': message.id})
        unread_messages = UserUnreadMessages.objects.filter(user_id=self.user_1.id, is_read=False)
        self.assertEqual(unread_messages.count(), 1)
        with CaptureQueriesContext(connection):
            response = self.client.get(retrieve_message_url)
        self.assertEqual(response.status_code, 200)
        unread_messages = UserUnreadMessages.objects.filter(user_id=self.user_1.id, is_read=False)
        self.assertEqual(unread_messages.count(), 0)

    def test_get_unread_messages(self):
        thread = self.create_thread([self.user_1.id, self.user_2.id], self.user_1.id)
        self.create_message(thread, self.user_2.id, 'Test message')
        self.create_message(thread, self.user_1.id, 'Test message') # This message should not be in the response
        self.create_message(thread, self.user_2.id, 'Test message')
        reverse(self.retrieve_unread_messages_url_name)
        url = reverse(self.retrieve_unread_messages_url_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)



