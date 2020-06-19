import uuid
import datetime

from events.events import *
from client_ticket.repository import ClientTicketRepository, client_tickets
from client_ticket.ticket import ClientTicket


def test_client_ticket_repository():
    client_id = 42
    t1 = ClientTicket.create(client_id, "FOO T1")
    t2 = ClientTicket.create(client_id, "BAR T2")

    t1.add_client_comment("Comment 1")

    assert len(client_tickets) == 0
    ClientTicketRepository.save(t1)

    assert len(client_tickets) == 1
    ClientTicketRepository.save(t2)
    assert len(client_tickets) == 2

    t3 = ClientTicketRepository.get_by_id(t1._id)
    assert t3._id == t1._id
    ClientTicketRepository.save(t3)
    assert len(client_tickets) == 2
