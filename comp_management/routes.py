import secrets
import os
from PIL import Image,ImageOps
from flask import Flask,render_template,request,flash,redirect,url_for,abort
from comp_management import app,db,bcrypt
from comp_management.forms import ComplaintForm,LoginForm,RegistrationForm,ResponseForm,ResolveForm,CategoryForm,UpdateAccountForm
from comp_management.models import User, Complaint, Category, Response, Notification
from flask_login import login_user,login_required,logout_user,current_user
from comp_management.models import Notification  # Adjust this import to match your project

@app.context_processor
def inject_notifications_count():
    if current_user.is_authenticated and not current_user.is_admin:
        # Query unread notifications for the currently logged-in user
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        return dict(count=unread_count)
    return dict(count=0)


def get_complaint_counts():
    return {
        'all_count': Complaint.query.count(),
        'pending_count': Complaint.query.filter_by(status='Pending').count(),
        'in_progress_count': Complaint.query.filter_by(status='In Progress').count(),
        'resolved_count': Complaint.query.filter_by(status='Resolved').count()
    }
@app.route("/")
def main():
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    user=User.query.filter_by(username=current_user.username).first()
    complaints=user.complaints
    count=Notification.query.filter_by(is_read=False,user_id=current_user.id).count()
    return render_template("home.html",complaints=complaints,count=count)

@app.route("/register",methods=["GET","POST"])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created. You can now log in.','success')
        return redirect(url_for('main'))
    return render_template('register.html',form=form)
        

@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            if user.is_admin:
                flash(f'Welcome Admin { user.username}','success')
                return redirect(url_for('admin_dashboard'))

            flash(f'Welcome { user.username}','success')
            return redirect(url_for('home'))
        else:
            flash("Unsuccessfull login. Please check your email and password.",'danger')
        
    return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
       current_user.username= form.username.data
       current_user.email= form.email.data
       if form.password.data:
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password=hashed_password
       db.session.commit()
       flash('Your account has been updated','success')
       return redirect(url_for('account'))

    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email

    return render_template('account.html',form=form)


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex + f_ext
    picture_path=os.path.join(app.root_path,'static/images',picture_fn)

    output_size=(125,125)
    image=Image.open(form_picture)
    image=ImageOps.exif_transpose(image)
    image=ImageOps.fit(image,output_size,Image.Resampling.LANCZOS)
    image.save(picture_path)

    return picture_fn

@app.route('/complaint',methods=['GET','POST'])
@login_required
def complaint():
    form = ComplaintForm()
    picture_file = None
    if form.validate_on_submit():
        if form.image.data:
            picture_file=save_picture(form.image.data)
            
        complaint=Complaint(title=form.title.data,content=form.content.data,
                            image_file=picture_file,user_id=current_user.id,
                            category_id=form.category.data.id)
        db.session.add(complaint)
        db.session.commit()
        flash('Complaint created succesfully.','success')
        return redirect(url_for('home'))
 
    return render_template('complaint.html', form=form)

@app.route('/complaint/<int:complaint_id>')
@login_required
def view_complaint(complaint_id):
    complaint=Complaint.query.get_or_404(complaint_id)
    if complaint.author!=current_user and not current_user.is_admin:
        abort(403)
    resolve_form=ResolveForm()

    return render_template('view_complaint.html',complaint=complaint,resolve_form=resolve_form)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status='Pending').count()
    in_progress_complaints = Complaint.query.filter_by(status='In Progress').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    total_users = User.query.count()

    # Precalculate percentages as integers
    if total_complaints > 0:
        pending_pct = int(round((pending_complaints / total_complaints) * 100))
        in_progress_pct = int(round((in_progress_complaints / total_complaints) * 100))
        resolved_pct = int(round((resolved_complaints / total_complaints) * 100))
        resolution_rate = round((resolved_complaints / total_complaints) * 100, 1)
    else:
        pending_pct = 0
        in_progress_pct = 0
        resolved_pct = 0
        resolution_rate = 0.0

    return render_template(
        'admin_dashboard.html',
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        total_users=total_users,
        pending_pct=pending_pct,
        in_progress_pct=in_progress_pct,
        resolved_pct=resolved_pct,
        resolution_rate=resolution_rate
    )


@app.route('/admin/complaints',methods=['GET','POST'])
@login_required
def all_complaints():
    if not current_user.is_admin:
        abort(403)

    complaints=Complaint.query.all()
    counts=get_complaint_counts()

    return render_template('all_complaints.html',complaints=complaints,**counts)

@app.route('/admin/users',methods=['GET','POST'])
@login_required
def all_users():
    if not current_user.is_admin:
        abort(403)
    users=User.query.all()
    return render_template('all_users.html',users=users)


@app.route('/admin/users/<int:user_id>/remove-admin',methods=['POST'])
@login_required
def remove_admin(user_id):
    if not current_user.is_admin:
        abort(403)
    user=User.query.get_or_404(user_id)
    if user.id==current_user.id:
        abort(403)
    if user.is_main_admin:
      abort(403)

    user.is_admin=False
    db.session.commit()
    flash('Admin privileges removed.', 'success')
    return redirect(url_for('all_users'))

@app.route('/admin/users/<int:user_id>/make-admin',methods=['POST'])
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        abort(403)
    user=User.query.get_or_404(user_id)
    user.is_admin=True
    db.session.commit()
    flash('User has been promoted to admin.', 'success')
    return redirect(url_for('all_users'))


@app.route('/admin/pending',methods=['GET','POST'])
@login_required
def pending():
    if not current_user.is_admin:
        abort(403)
    complaints=Complaint.query.filter_by(status='Pending').all()
    counts=get_complaint_counts()
    return render_template('pending.html',complaints=complaints,**counts)

@app.route('/admin/inprogress',methods=['GET','POST'])
@login_required
def in_progress():
    if not current_user.is_admin:
        abort(403)
    complaints=Complaint.query.filter_by(status='In Progress').all()
    counts=get_complaint_counts()
    return render_template('in_progress.html',complaints=complaints,**counts)

@app.route('/admin/resolved',methods=['GET','POST'])
@login_required
def resolved():
    if not current_user.is_admin:
        abort(403)
    complaints=Complaint.query.filter_by(status='Resolved').all()
    counts=get_complaint_counts()
    return render_template('resolved.html',complaints=complaints,**counts)

@app.route('/categories')
@login_required
def categories():
    if not current_user.is_admin:
        abort(403)
    categories=Category.query.all()
    return render_template('categories.html',categories=categories)

@app.route("/admin/category/<int:cat_id>/complaints")
@login_required
def category_complaints(cat_id):
    # Restrict to admins only
    if not current_user.is_admin:
        abort(403)
        
    category = Category.query.get_or_404(cat_id)
    # Fetch complaints under this category, ordered newest first
    complaints = Complaint.query.filter_by(category_id=category.id)\
                                .order_by(Complaint.date_posted.desc())\
                                .all()                        
    return render_template(
        'category_complaints.html', 
        category=category, 
        complaints=complaints
    )

@app.route('/categories/add',methods=['GET','POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        abort(403)
    form=CategoryForm()
    if form.validate_on_submit():
        
        existing_category=Category.query.filter_by(name=form.name.data).first()
        if existing_category:
            flash('The category name provided already exists.','danger')
            return redirect(url_for('add_category'))

        category=Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash(f'Category has been added successfully.','success')
        return redirect(url_for('categories'))
    return render_template('add_category.html',form=form)

@app.route('/categories/edit/<int:cat_id>',methods=['GET','POST'])
@login_required
def edit_category(cat_id):
    if not current_user.is_admin:
        abort(403)
    form=CategoryForm()
    category=Category.query.get_or_404(cat_id)
    if request.method=='GET':
        form.name.data=category.name
    if form.validate_on_submit():
        category.name=form.name.data
        db.session.commit()
        flash(f'Category updated successfully.','success')
        return redirect(url_for('categories'))
    return render_template('edit_category.html',form=form)

@app.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
def delete_category(cat_id):
    if not current_user.is_admin:
        abort(403)
    category = Category.query.get_or_404(cat_id)
    if category.name == 'Other':
        flash('The Other category cannot be deleted.', 'danger')
        return redirect(url_for('categories'))
    other_category = Category.query.filter_by(name='Other').first()
    if not other_category:
        flash('The Other category does not exist.', 'danger')
        return redirect(url_for('categories'))
    complaints = Complaint.query.filter_by(category_id=cat_id).all()
    for complaint in complaints:
        complaint.category_id = other_category.id
    db.session.delete(category)
    db.session.commit()
    flash(f'{category.name} category deleted successfully.', 'success')
    return redirect(url_for('categories'))


@app.route('/response/<int:complaint_id>',methods=['GET','POST'])
@login_required
def response(complaint_id):
    if not current_user.is_admin:
        abort(403)
    form=ResponseForm()
    complaint=Complaint.query.get_or_404(complaint_id)
    if form.validate_on_submit():
       response=Response(content=form.content.data,complaint_id=complaint.id,admin_id=current_user.id)

       complaint.status = 'In Progress'
       db.session.add(response)
       
       flash(f'Your Response has been added successfully.','success')
       user=complaint.author
       notification=Notification(message="An Admin has responded to your complaint.",user_id=user.id,
                                complaint_id=complaint.id)
       db.session.add(notification)
       db.session.commit()
       return redirect(url_for('view_complaint',complaint_id=complaint.id))

    return render_template('response.html',form=form)


@app.route('/complaint/<int:complaint_id>/resolve',methods=['POST'])
@login_required
def resolve_complaint(complaint_id):
    if not current_user.is_admin:
        abort(403)
    complaint=Complaint.query.get_or_404(complaint_id)
    form = ResolveForm()
    if form.validate_on_submit():
        complaint.status='Resolved'
        
        flash('Complaint has been marked as resolved.','success')
        user=complaint.author
        notification=Notification(message="Your Complaint has been resolved.",user_id=user.id,
                                complaint_id=complaint.id)
        db.session.add(notification)
        db.session.commit()
    return redirect(url_for('view_complaint',complaint_id=complaint.id))

@app.route('/notifications')
@login_required
def notifications():
    all_notifications=Notification.query.filter_by(user_id=current_user.id).all()
    return render_template('notifications.html',all_notifications=all_notifications)

@app.route('/notifications/<int:notification_id>')
@login_required
def view_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    # Make sure the notification belongs to the logged-in user
    if notification.user_id != current_user.id:
        abort(403)
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('view_complaint',complaint_id=notification.complaint_id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'),404

@app.errorhandler(403)
def forbidden_action(error):
    return render_template('errors/403.html'),403

@app.errorhandler(500)
def general_error(error):
    return render_template('errors/500.html'),500