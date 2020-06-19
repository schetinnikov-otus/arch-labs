from events.dispatch import raise_event
from events.decorators import on_event
from events.events import *

from .ticket_queue import TicketQueue
from .repository import TicketQueueRepository

@on_event(ClientCreatedTicket)
def on_ticket_created(event, env=None):
    t = TicketQueue.create(
        ticket_id=event.ticket_id,
        ticket_created_at=event.ticket_created_at
    )
    TicketQueueRepository.save(t)


@on_event(ClientReturnedTicketToOperator)
def on_client_returned_ticket_to_operator(event, env=None):
    t = TicketQueueRepository.get_by_id(event.ticket_id)
    t.dispatch_event(event)
    TicketQueueRepository.save(t)
