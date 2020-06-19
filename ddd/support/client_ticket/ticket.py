import uuid
import datetime
from enum import Enum

from events.events import *

class Status(Enum):
    CREATED = 1
    NEED_INFO = 2
    IN_PROGRESS = 3
    DONE = 4
    CLOSED = 5

class CommentType(Enum):
    CLIENT = 1
    OPERATOR = 2

class Comment:
    def __init__(self, comment_id, comment_type, created_at, text):
        self._id = comment_id
        self._created_at = created_at
        self._type = comment_type
        self._text = text

class ClientTicket:
    def __init__(self, ticket_id, client_id, created_at, status, description, comments=[]):
        self._events = []
        self._id = ticket_id
        self._created_at = created_at
        self._description = description
        self._comments = comments
        self._status = status
        self._client_id = client_id

    def emit_event(self, event):
        self._events.append(event)

    def dispatch_event(self, event):
        if isinstance(event, OperatorDoneTicket):
            self.on_operator_done_ticket(event)
        elif isinstance(event, OperatorNeedMoreInfoForTicket):
            self.on_operator_need_info(event)
        elif isinstance(event, OperatorAddedCommentInTicket):
            self.on_operator_added_comment(event)
        else:
            pass

    @classmethod
    def create(cls, client_id, description):
        ticket = cls(
            ticket_id=uuid.uuid4(),
            client_id=client_id,
            created_at=datetime.datetime.now(),
            status=Status.CREATED,
            description=description
        )
        ticket.emit_event(ClientCreatedTicket(
            ticket_id=ticket.id,
            client_id=client_id,
            ticket_created_at=ticket.created_at,
            ticket_description=ticket.description
        ))
        return ticket

    @property
    def is_closed(self):
        return self._status == Status.CLOSED

    @property
    def id(self):
        return self._id

    @property
    def client_id(self):
        return self._client_id

    @property
    def created_at(self):
        return self._created_at

    @property
    def description(self):
        return self._description

    @property
    def status(self):
        return self._status

    @property
    def comments(self):
        return self._comments

    def close(self):
        self._status = Status.CLOSED

    def return_ticket_to_operator(self, comment):
        if not self.is_closed:
            self._status = Status.IN_PROGRESS
            self.add_client_comment(comment)
            self.emit_event(ClientReturnedTicketToOperator(
                ticket_id=self.id
            ))

    def add_client_comment(self, comment_text):
        if not self.is_closed:
            comment = Comment(
                comment_id=uuid.uuid4(),
                created_at=datetime.datetime.now(),
                text=comment_text,
                comment_type=CommentType.CLIENT
            )
            self.comments.append(comment)
            self.emit_event(ClientAddedCommentToTicket(
                ticket_id=self.id,
                client_id=self.client_id,
                comment_id=comment._id,
                comment_created_at=comment._created_at,
                comment_text=comment._text
            ))

    def on_operator_done_ticket(self, event):
        self._status = Status.DONE

    def on_operator_added_comment(self, event):
        comment = Comment(
            comment_id=event.comment_id,
            created_at=event.comment_created_at,
            text=event.comment_text,
            comment_type=CommentType.OPERATOR
        )
        self.comments.append(comment)

    def on_operator_need_info(self, event):
        self._status = Status.NEED_INFO
