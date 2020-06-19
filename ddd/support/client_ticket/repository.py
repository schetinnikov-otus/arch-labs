client_tickets = []

class ClientTicketRepository:
    @staticmethod
    def to_dict(ticket):
        return {
            'ticket_id': ticket._id,
            'created_at': ticket._created_at,
            'status': ticket._status,
            'description': ticket._description,
            'client_id': ticket._client_id,
            'comments': [{
                'comment_id': c._id,
                'text': c._text,
                'created_at': c._created_at,
                'comment_type': c._type
                } for c in ticket._comments
            ]
        }

    @staticmethod
    def from_dict(ticket_dict):
        import copy
        from .ticket import ClientTicket, Comment
        ticket_dict = copy.deepcopy(ticket_dict)
        comments = [Comment(**c) for c in ticket_dict['comments']]
        ticket_dict['comments'] = comments
        return ClientTicket(**ticket_dict)

    @staticmethod
    def save(client_ticket):
        ts = [t for t in client_tickets
            if t['ticket_id'] == client_ticket._id]

        if ts:
            t = ts[0]
            t.update(ClientTicketRepository.to_dict(client_ticket))
        else:
            t = ClientTicketRepository.to_dict(client_ticket)
            client_tickets.append(t)

    @staticmethod
    def get_by_id(ticket_id):
        ticket_dict = [t for t in client_tickets if t['ticket_id'] == ticket_id][0]
        return ClientTicketRepository.from_dict(ticket_dict)
