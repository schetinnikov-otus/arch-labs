from events.events import *
import uuid
import datetime


def test_client_ticket():
    from client_ticket.ticket import ClientTicket, Status
    client_id = 1

    # client created ticket
    t1 = ClientTicket.create(client_id=client_id, description="I'm unhappy")
    t1.add_client_comment("waiting for you!")

    assert t1.status == Status.CREATED
    assert len(t1.comments) == 1

    # operator returned and added comment
    e1 = OperatorAddedCommentInTicket(
        ticket_id=t1.id,
        comment_id=uuid.uuid4(),
        comment_created_at=datetime.datetime.now(),
        comment_text="You are wrong!"
    )

    e2 = OperatorNeedMoreInfoForTicket(
        ticket_id=t1.id
    )
    t1.dispatch_event(e1)
    t1.dispatch_event(e2)

    # client reopened ticket
    t1.return_ticket_to_operator(comment="Not you was wrong!")

    # operator returned with excuses
    e3 = OperatorAddedCommentInTicket(
        ticket_id=t1.id,
        comment_id=uuid.uuid4(),
        comment_created_at=datetime.datetime.now(),
        comment_text="We have fixed!"
    )
    # operator done ticket
    e4 = OperatorDoneTicket(
        ticket_id=t1.id
    )
    t1.dispatch_event(e3)
    t1.dispatch_event(e4)
