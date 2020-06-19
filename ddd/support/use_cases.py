from events.dispatch import raise_events

from client_ticket.on_events import *
from operator_ticket.on_events import *
from ticket_queue.on_events import *

from client_ticket.ticket import ClientTicket
from client_ticket.repository import ClientTicketRepository

from ticket_queue.repository import TicketQueueRepository
from ticket_queue.ticket_queue import TicketQueue, TicketQueueService

from operator_ticket.ticket import OperatorTicket
from operator_ticket.repository import OperatorTicketRepository


def create_ticket(client_id, description):
    ticket = ClientTicket.create(client_id, description)
    ClientTicketRepository.save(ticket)
    raise_events(ticket._events)

def assign_ticket_to_operator(operator_id):
    tickets = TicketQueueRepository.get_tickets_in_queue()
    ticket = TicketQueueService.get_ticket_for_operator(tickets, operator_id)
    ticket.assign(operator_id)
    TicketQueueRepository.save(ticket)
    raise_events(ticket._events)

def operator_need_info_ticket(ticket_id, comment_text):
    ticket = OperatorTicketRepository.get_by_id(ticket_id)
    ticket.operator_need_info(comment_text)
    OperatorTicketRepository.save(ticket)
    raise_events(ticket._events)

def client_add_comment(ticket_id, comment_text):
    ticket = ClientTicketRepository.get_by_id(ticket_id)
    ticket.add_client_comment("Here you get it")
    ClientTicketRepository.save(ticket)
    raise_events(ticket._events)

def client_returns_ticket_to_operator(ticket_id, comment_text):
    ticket = ClientTicketRepository.get_by_id(ticket_id)
    ticket.return_ticket_to_operator("I've returned it to you!")
    ClientTicketRepository.save(ticket)
    raise_events(ticket._events)

def operator_done(ticket_id):
    ticket = OperatorTicketRepository.get_by_id(ticket_id)
    ticket.operator_done()
    OperatorTicketRepository.save(ticket)
    raise_events(ticket._events)

def client_close(ticket_id):
    ticket = ClientTicketRepository.get_by_id(ticket_id)
    ticket.close()
    ClientTicketRepository.save(ticket)
    raise_events(ticket._events)
