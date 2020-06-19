import uuid
import datetime
import pprint

from events.events import *
from use_cases import (
    create_ticket,
    assign_ticket_to_operator,
    operator_need_info_ticket,
    client_add_comment,
    client_returns_ticket_to_operator,
    operator_done,
    client_close
)
from client_ticket.repository import client_tickets
from operator_ticket.repository import operator_tickets
from ticket_queue.repository import ticket_queues


def show_tables():
    pprint.pprint('client_tickets')
    pprint.pprint(client_tickets)
    pprint.pprint('ticket_queues')
    pprint.pprint(ticket_queues)
    pprint.pprint('operator_tickets')
    pprint.pprint(operator_tickets)
    pprint.pprint('*'*80)


def test_use_cases():
    create_ticket(client_id=42, description="FOO")
    show_tables()

    assign_ticket_to_operator(operator_id=228)
    show_tables()

    ticket_id = client_tickets[0]['ticket_id']
    operator_need_info_ticket(ticket_id=ticket_id, comment_text="More info please")
    show_tables()

    client_add_comment(ticket_id=ticket_id, comment_text="Here you get it!")
    show_tables()

    client_returns_ticket_to_operator(ticket_id=ticket_id, comment_text="Yes this pleasse")
    show_tables()

    assign_ticket_to_operator(operator_id=228)
    show_tables()

    operator_done(ticket_id=ticket_id)
    show_tables()

    client_close(ticket_id=ticket_id)
    show_tables()
