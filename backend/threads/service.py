import logging
from typing import Iterable, Type

from django.db import transaction

from threads.models import Message, Thread, UserUnreadMessages

logger = logging.getLogger(__name__)


class ParticipantsError(Exception):
    def __init__(self):
        self.message = "Can't add more participants then 2 to a thread"
        super().__init__(self.message)


class ThreadService:
    @staticmethod
    def get_thread_by_participants(
            participants: list[int]
    ) -> Thread | None:
        return Thread.objects.filter(participants__in=set(participants)).first()

    @staticmethod
    def create_thread_with_participants(
            creator_id: int,
            participants: list[int]
    ):
        # Better to add constraint but Sqlite doesn't support it
        if len(participants) > 2:
            raise ParticipantsError
        with transaction.atomic():
            thread = Thread.objects.create(creator_id=creator_id)
            thread.participants.set(set(participants))
        return thread


class MessageService:
    model: Type[Message] = Message

    def create_message(self, sender_id: int, content: str, thread: Thread) -> Message:
        with transaction.atomic():
            message = self.model.objects.create(
                sender_id=sender_id,
                content=content,
                thread=thread
            )
            participant_ids = set(thread.participants.values_list('id', flat=True))
            self.updated_users_unread_messages(participant_ids, message)
        return message

    @staticmethod
    def check_thread_message_permission(thead: Thread, user_id: int) -> bool:
        return thead.participants.filter(id=user_id).exists()

    @staticmethod
    def updated_users_unread_messages(participants: set[id], message: Message):
        participants.remove(message.sender_id)
        UserUnreadMessages.objects.bulk_create([
            UserUnreadMessages(
                user_id=participant_id, message_id=message.id,
            )
            for participant_id in participants
        ])

    @staticmethod
    def mark_message_as_read(user_id: int, message_ids: list[int]):
        UserUnreadMessages.objects.filter(
            user_id=user_id, message_id__in=message_ids
        ).update(is_read=True)
