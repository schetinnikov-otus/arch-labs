import uuid
import datetime
from events.events import TicketAssignedToOperator, ClientAddedCommentToTicket, OperatorAddedCommentInTicket, OperatorNeedMoreInfoForTicket, OperatorDoneTicket
from enum import Enum


class TicketStatus(Enum):
    NOT_ASSIGNED = -1
    ASSIGNED = 0
    NEED_INFO_FROM_CLIENT = 1
    DONE = 2

class Comment:
    def __init__(self, comment_id, author_id, created_at, text):
        self._id = comment_id
        self._created_at = created_at
        self._author_id = author_id
        self._text = text

class OperatorTicket:
    def __init__(self, ticket_id, client_id, created_at, description, status, operator_id = None, comments=[]):
        self._id = ticket_id
        self._client_id = client_id
        self._created_at = created_at
        self._status = status
        self._description = description
        self._operator_id = operator_id
        self._comments = comments
        self._events = []

    def emit_event(self, event):
        self._events.append(event)

    def dispatch_event(self, event):
        if isinstance(event, TicketAssignedToOperator):
            self.on_ticket_assigned_to_operator(event)
        elif isinstance(event, ClientAddedCommentToTicket):
            self.on_client_added_comment(event)
        else:
            pass

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
    def status(self):
        return self._status

    @property
    def comments(self):
        return self._comments

    @classmethod
    def create(cls, client_id, ticket_id, description, created_at):
        ticket = cls(
            ticket_id=ticket_id,
            client_id=client_id,
            created_at=created_at,
            status=TicketStatus.NOT_ASSIGNED,
            description=description
        )
        return ticket

    def operator_add_comment(self, comment_text):
        comment = Comment(
            comment_id=uuid.uuid4(),
            created_at=datetime.datetime.now(),
            author_id=self._operator_id,
            text=comment_text
        )
        self.comments.append(comment)
        self.emit_event(OperatorAddedCommentInTicket(
            ticket_id=self.id,
            comment_id=comment._id,
            comment_created_at=comment._created_at,
            comment_text=comment._text
        ))

    def operator_need_info(self, comment_text):
        self.operator_add_comment(comment_text)
        self._status = TicketStatus.NOT_ASSIGNED
        self._operator_id = None
        self.emit_event(OperatorNeedMoreInfoForTicket(ticket_id=self.id))

    def operator_done(self):
        self._status = TicketStatus.NOT_ASSIGNED
        self._operator_id = None
        self.emit_event(OperatorDoneTicket(ticket_id=self.id))

    def on_client_added_comment(self, event):
        comment = Comment(
            comment_id=event.comment_id,
            created_at=event.comment_created_at,
            text=event.comment_text,
            author_id=event.client_id
        )
        self.comments.append(comment)

    def on_ticket_assigned_to_operator(self, event):
        self._status = TicketStatus.ASSIGNED
        self._operator_id = event.operator_id
