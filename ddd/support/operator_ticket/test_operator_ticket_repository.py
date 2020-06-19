import uuid
import datetime

from events.events import *
from operator_ticket.repository import OperatorTicketRepository, operator_tickets
from operator_ticket.ticket import OperatorTicket


def test_operator_ticket_repository():
    client_id = 42
    # ticket_id, operator_id, created_at, status, description, comments=[]):
    ticket_id = uuid.uuid4()
    ticket_id2 = uuid.uuid4()
    ticket_created_at = datetime.datetime.now()
    t1 = OperatorTicket.create(
        ticket_id=ticket_id,
        client_id=client_id,
        created_at=ticket_created_at,
        description="FOO OPERATOR T1"
    )
    t2 = OperatorTicket.create(
        ticket_id=ticket_id2,
        client_id=client_id,
        created_at=ticket_created_at,
        description="BAR OPERATOR T1"
    )

    t1.operator_add_comment("Comment 1")

    assert len(operator_tickets) == 0
    OperatorTicketRepository.save(t1)

    assert len(operator_tickets) == 1
    OperatorTicketRepository.save(t2)
    assert len(operator_tickets) == 2

    t3 = OperatorTicketRepository.get_by_id(t1._id)
    assert t3._id == t1._id
    OperatorTicketRepository.save(t3)
    assert len(operator_tickets) == 2
