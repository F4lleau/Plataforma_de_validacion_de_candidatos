from sqlalchemy import select, func, update
from app.models.invitation import Invitation
from app.models.user import User
from app.db.functions import normalized_trim
from app.models.auth_session import MailOutbox


class InvitationRepository:
    def __init__(self, db):
        self.db = db

    def get(self, identity):
        return self.db.scalar(
            select(Invitation)
            .where(Invitation.id == identity)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def by_email(self, email):
        return self.db.scalar(
            select(Invitation)
            .where(Invitation.email == email)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def by_digest(self, value):
        return self.db.scalar(select(Invitation).where(Invitation.digest == value))

    def email_exists(self, email):
        return (
            self.db.scalar(
                select(User.id).where(func.lower(normalized_trim(User.email)) == email)
            )
            is not None
        )

    def listing(self, offset, limit):
        return list(
            self.db.scalars(
                select(Invitation)
                .order_by(Invitation.id.desc())
                .offset(offset)
                .limit(limit)
            )
        )

    def mail_state(self, invitation):
        return self.db.scalar(
            select(MailOutbox.state)
            .where(MailOutbox.invitation_id == invitation.id)
            .order_by(MailOutbox.created_at.desc())
            .limit(1)
        )

    def cancel_mail(self, identity):
        self.db.execute(
            update(MailOutbox)
            .where(
                MailOutbox.invitation_id == identity,
                MailOutbox.state.in_(["pending", "processing"]),
            )
            .values(state="cancelled", payload=None, last_error=None)
        )
