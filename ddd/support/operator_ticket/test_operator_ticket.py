import uuid
import datetime

from operator_ticket.ticket import OperatorTicket, TicketStatus
from events.events import *


def test_operator_ticket():
    operator_id = 42
    client_id = 1488
    ticket_id = uuid.uuid4()
    ticket_created_at=datetime.datetime.now()

    t1 = OperatorTicket.create(
        client_id=client_id,
        ticket_id=ticket_id,
        description="Everything is good, but some have some issues",
        created_at=ticket_created_at
    )

    e1 = TicketAssignedToOperator(ticket_id=ticket_id, operator_id=operator_id)
    t1.dispatch_event(e1)
    assert t1._status == TicketStatus.ASSIGNED

    assert len(t1._events) == 0
    t1.operator_add_comment("Foo")
    assert len(t1._events) == 1

    t1.operator_need_info("Bar")
    assert len(t1._events) == 3
    assert t1._status == TicketStatus.NOT_ASSIGNED

    e2 = ClientAddedCommentToTicket(
        comment_id=uuid.uuid4(),
        client_id=client_id,
        ticket_id=ticket_id,
        comment_created_at=datetime.datetime.now(),
        comment_text="BAZZZ"
    )
    t1.dispatch_event(e2)
