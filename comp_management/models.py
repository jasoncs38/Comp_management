from comp_management import db,login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)
    is_main_admin=db.Column(db.Boolean,nullable=False,default=False)
    complaints=db.relationship('Complaint',backref='author',lazy=True)
    responses_given = db.relationship('Response',foreign_keys='Response.admin_id',
                                      backref='admin',lazy=True)
    notifications = db.relationship('Notification',backref='user',lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Complaint(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    content=db.Column(db.Text,nullable=False)
    image_file=db.Column(db.String(100))
    status = db.Column(db.String(20),nullable=False,default='Pending')
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    responses=db.relationship('Response',backref='complaint',lazy=True)

    def __repr__(self):
        return f"Complaint('{self.title}')"

class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False,unique=True)
    complaints = db.relationship('Complaint', backref='category', lazy=True)

class Response(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    content=db.Column(db.Text,nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    complaint_id=db.Column(db.Integer,db.ForeignKey('complaint.id'),nullable=False)
    admin_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer,db.ForeignKey('complaint.id'),nullable=True)