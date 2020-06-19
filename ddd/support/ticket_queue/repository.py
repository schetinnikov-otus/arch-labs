ticket_queues = []

class TicketQueueRepository:
    @staticmethod
    def to_dict(ticket_queue):
        return {
            'ticket_id': ticket_queue._id,
            'ticket_created_at': ticket_queue._created_at,
            'status': ticket_queue._status
        }

    @staticmethod
    def from_dict(ticket_dict):
        from .ticket_queue import TicketQueue
        return TicketQueue(**ticket_dict)

    @staticmethod
    def save(ticket_queue):
        ts = [t for t in ticket_queues
            if t['ticket_id'] == ticket_queue._id]

        if ts:
            t = ts[0]
            t.update(TicketQueueRepository.to_dict(ticket_queue))
        else:
            t = TicketQueueRepository.to_dict(ticket_queue)
            ticket_queues.append(t)

    @staticmethod
    def get_by_id(ticket_id):
        ticket_dict = [t for t in ticket_queues if t['ticket_id'] == ticket_id][0]
        return TicketQueueRepository.from_dict(ticket_dict)

    @staticmethod
    def get_tickets_in_queue():
        return [TicketQueueRepository.from_dict(t) for t in ticket_queues]
