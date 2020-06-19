from events.dispatch import raise_event
from events.decorators import on_event
from events.events import *

from .ticket import ClientTicket
from .repository import ClientTicketRepository

@on_event(OperatorNeedMoreInfoForTicket, OperatorDoneTicket, OperatorAddedCommentInTicket)
def on_ticket_need_info(event, env=None):
    t = ClientTicketRepository.get_by_id(event.ticket_id)
    t.dispatch_event(event)
    ClientTicketRepository.save(t)
