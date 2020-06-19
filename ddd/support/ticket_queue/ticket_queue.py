import uuid
import datetime
from enum import Enum

from events.events import *


class TicketStatus(Enum):
    ASSIGNED = 1
    IN_QUEUE = 2
    CLOSED = 3

class TicketQueue:
    def __init__(self, ticket_id, status, ticket_created_at, operator_id=None):
        self._id = ticket_id
        self._created_at = ticket_created_at
        self._status = status
        self._operator_id = operator_id
        self._events = []

    def emit_event(self, event):
        self._events.append(event)

    def dispatch_event(self, event):
        if isinstance(event, ClientReturnedTicketToOperator):
            self.on_client_returned_ticket_to_operator(event)
        else:
            pass

    @classmethod
    def create(cls, ticket_id, ticket_created_at):
        ticket_queue = cls(
            ticket_id=ticket_id,
            status=TicketStatus.IN_QUEUE,
            ticket_created_at=ticket_created_at
        )
        return ticket_queue

    def assign(self, operator_id):
        self._status = TicketStatus.ASSIGNED
        self.emit_event(TicketAssignedToOperator(
            ticket_id=self._id,
            operator_id=operator_id
        ))

    # DO we need it?
    def close(self):
        self._status = TicketStatus.CLOSED

    def in_queue(self):
        self._status = TicketStatus.IN_QUEUE

    def on_client_returned_ticket_to_operator(self, event):
        self.in_queue()


class TicketQueueService:
    @staticmethod
    def get_ticket_for_operator(tickets_in_queue, operator_id):
        # TODO: complex algorithm!
        ticket = tickets_in_queue[0]
        return ticket
