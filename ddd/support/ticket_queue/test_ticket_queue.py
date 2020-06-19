from events.events import *
import uuid
import datetime
from ticket_queue.ticket_queue import TicketQueue, TicketQueueService, TicketStatus


def test_ticket_queue():
    operator_id = 42
    client_id = 1488
    ticket_id = uuid.uuid4()
    t1 = TicketQueue.create(ticket_id=ticket_id, ticket_created_at=datetime.datetime.now())
    t2 = TicketQueueService.get_ticket_for_operator(
        [t1],
        operator_id
    )
    assert len(t1._events) == 0
    t1.assign(operator_id)
    assert len(t1._events) == 1
    assert t1._status == TicketStatus.ASSIGNED

    e2 = ClientReturnedTicketToOperator(ticket_id=ticket_id)
    t1.dispatch_event(e2)
    t1._status == TicketStatus.IN_QUEUE
