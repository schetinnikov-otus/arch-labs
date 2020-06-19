import datetime


class OperatorAddedCommentInTicket:
    def __init__(self, ticket_id, comment_id, comment_created_at, comment_text=''):
        self.ticket_id = ticket_id
        self._created_at = datetime.datetime.now()
        self.comment_id = comment_id
        self.comment_created_at = comment_created_at
        self.comment_text = comment_text


class ClientAddedCommentToTicket:
    def __init__(self, ticket_id, client_id, comment_id, comment_created_at, comment_text):
        self.ticket_id = ticket_id
        self.client_id = client_id
        self.comment_id = comment_id
        self.comment_created_at = comment_created_at
        self.comment_text = comment_text


class ClientCreatedTicket:
    def __init__(self, ticket_id, client_id, ticket_created_at, ticket_description):
        self.ticket_id = ticket_id
        self.client_id = client_id
        self.ticket_created_at = ticket_created_at
        self.ticket_description = ticket_description


class OperatorDoneTicket:
    def __init__(self, ticket_id, created_at=None):
        self.ticket_id = ticket_id
        self.created_at = datetime.datetime.now() if created_at is None else created_at


class OperatorNeedMoreInfoForTicket:
    def __init__(self, ticket_id, created_at=None):
        self.ticket_id = ticket_id
        self.created_at = datetime.datetime.now() if created_at is None else created_at


class ClientReturnedTicketToOperator:
    def __init__(self, ticket_id, created_at=None):
        self.ticket_id = ticket_id


class TicketAssignedToOperator:
    def __init__(self, ticket_id, operator_id):
        self.ticket_id = ticket_id
        self.operator_id = operator_id
