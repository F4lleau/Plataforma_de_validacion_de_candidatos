from datetime import timedelta
from sqlalchemy import select, func
from app.models.auth_session import MailOutbox, PasswordReset
from app.models.user import User
from app.models.invitation import Invitation
from app.utils.enums import UserRole
from app.repositories.auth_repository import now


class MailRepository:
    def __init__(self, db):
        self.db = db

    def recent(self, uid, kind, seconds):
        return self.db.scalar(
            select(MailOutbox.id).where(
                MailOutbox.user_id == uid,
                MailOutbox.kind == kind,
                MailOutbox.created_at > now() - timedelta(seconds=seconds),
            )
        )

    def claim(self):
        return self.db.scalar(
            select(MailOutbox)
            .where(
                MailOutbox.state.in_(["pending", "processing"]),
                MailOutbox.available_at <= now(),
            )
            .order_by(MailOutbox.available_at)
            .with_for_update(skip_locked=True)
            .limit(1)
        )

    def locked(self, identity):
        return self.db.scalar(
            select(MailOutbox)
            .where(MailOutbox.id == identity)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def valid(self, row):
        if row.expires_at <= now():
            return False
        if row.invitation_id:
            invitation = self.db.get(
                Invitation, row.invitation_id, populate_existing=True
            )
            actor = (
                self.db.get(User, invitation.invited_by, populate_existing=True)
                if invitation
                else None
            )
            return bool(
                invitation
                and invitation.state == "pending"
                and invitation.digest == row.invitation_digest
                and invitation.expires_at > now()
                and actor
                and actor.is_active
                and actor.role == UserRole.ADMIN
            )
        user = self.db.get(User, row.user_id)
        if row.expires_at <= now() or not user:
            return False
        if row.reset_digest:
            reset = self.db.get(PasswordReset, row.reset_digest)
            return bool(
                user.is_active
                and reset
                and not reset.consumed_at
                and reset.expires_at > now()
                and reset.credential_version == user.credential_version
            )
        return True

    def status(self):
        return dict(
            self.db.execute(
                select(MailOutbox.state, func.count()).group_by(MailOutbox.state)
            ).all()
        )
