from extensions import db


class LinkedInUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "linkedin_id": self.linkedin_id,
            "title": self.title,
        }

class LinkedInLiker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedin_user_id = db.Column(
        db.String(120), db.ForeignKey("linked_in_user.linkedin_id"), nullable=False
    )
    liker_user_name = db.Column(db.String(120), nullable=False)
    liker_user_id = db.Column(db.String(120), nullable=False)
    post_id = db.Column(db.String(200), nullable=False)
    likers_title = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "linkedin_user_id": self.linkedin_user_id,
            "liker_user_name": self.liker_user_name,
            "liker_user_id": self.liker_user_id,
            "post_id": self.post_id,
            "likers_title": self.likers_title,
        }
