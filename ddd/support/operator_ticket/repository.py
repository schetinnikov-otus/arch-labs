operator_tickets = []

class OperatorTicketRepository:
    @staticmethod
    def to_dict(ticket):
        return {
            'ticket_id': ticket._id,
            'created_at': ticket._created_at,
            'status': ticket._status,
            'description': ticket._description,
            'client_id': ticket._client_id,
            'operator_id': ticket._operator_id,
            'comments': [{
                'comment_id': c._id,
                'text': c._text,
                'created_at': c._created_at,
                'author_id': c._author_id
                } for c in ticket._comments
            ]
        }

    @staticmethod
    def from_dict(ticket_dict):
        from .ticket import OperatorTicket, Comment
        comments = [Comment(**c) for c in ticket_dict['comments']]
        ticket_dict['comments'] = comments
        return OperatorTicket(**ticket_dict)

    @staticmethod
    def save(operator_ticket):
        ts = [t for t in operator_tickets
            if t['ticket_id'] == operator_ticket._id]

        if ts:
            t = ts[0]
            t.update(OperatorTicketRepository.to_dict(operator_ticket))
        else:
            t = OperatorTicketRepository.to_dict(operator_ticket)
            operator_tickets.append(t)

    @staticmethod
    def get_by_id(ticket_id):
        ticket_dict = [t for t in operator_tickets if t['ticket_id'] == ticket_id][0]
        return OperatorTicketRepository.from_dict(ticket_dict)
