from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _utcnow():
    return datetime.now(timezone.utc)


class Url(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)
    click_count = db.Column(db.Integer, default=0, nullable=False)

    clicks = db.relationship(
        "Click", backref="url", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_stats(self, recent_limit=10):
        recent = (
            self.clicks.order_by(Click.clicked_at.desc()).limit(recent_limit).all()
        )
        return {
            "code": self.code,
            "original_url": self.original_url,
            "created_at": self.created_at.isoformat(),
            "click_count": self.click_count,
            "recent_clicks": [c.clicked_at.isoformat() for c in recent],
        }


class Click(db.Model):
    __tablename__ = "clicks"

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(
        db.Integer, db.ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clicked_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)
