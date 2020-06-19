from events.dispatch import raise_event
from events.decorators import on_event
from events.events import *

from .ticket import OperatorTicket
from .repository import OperatorTicketRepository


@on_event(ClientCreatedTicket)
def on_ticket_created(event, env=None):
    t = OperatorTicket.create(
        client_id=event.client_id,
        ticket_id=event.ticket_id,
        description=event.ticket_description,
        created_at=event.ticket_created_at
    )
    OperatorTicketRepository.save(t)


@on_event(TicketAssignedToOperator, ClientAddedCommentToTicket)
def on_ticket_assigned_to_operator(event, env=None):
    t = OperatorTicketRepository.get_by_id(event.ticket_id)
    t.dispatch_event(event)
    OperatorTicketRepository.save(t)
