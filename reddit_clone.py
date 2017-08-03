from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Sub, User, Post, Comment
import sqlalchemy.orm.exc

engine = create_engine('sqlite:///reddit.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def main():
	return 'Hello World'


@app.route('/signup', methods=['GET','POST'])
def new_user():
	if request.method == 'POST':
		print ' On post method'
		print ' will create new user'
		newUser = User(username=request.form['username'], password=request.form['password'], email=request.form['email'])
		print 'new user created'
		print 'adding to session'
		session.add(newUser)
		print 'added to session'
		print 'updating session'
		session.commit()
		print 'done'
		return redirect(url_for('show_users'))
	else:
		return render_template('signup.html')

@app.route('/login/', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		try:
			user = session.query(User).filter_by(username=request.form['username']).one()
		except sqlalchemy.orm.exc.NoResultFound:
			return "<html> <body>Wrong username or password <br/><br/> <a href=%s>back</a></body></html>"%url_for('login')
		if user.verify_password(request.form['password']):
			return '<html> <body>%s logged in!</body></html>'%user.username
		else:
			return "<html> <body>Wrong username or password <br/><br/> <a href=%s>back</a></body></html>"%url_for('login')
	else:
		return render_template('login.html')

@app.route('/admin/allusers')
def show_users():
	users = session.query(User).all()
	return render_template('show_users.html',users=users)

@app.route('/admin/user/delete/<int:user_id>/')
def delete_user(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	session.delete(user)
	session.commit()
	return redirect(url_for('show_users'))

@app.route('/admin/user/edit/<int:user_id>/', methods=['GET','POST'])
def edit_user(user_id,msg=''):
	user = session.query(User).filter_by(id=user_id).one()
	return render_template('edit_user.html',user=user)

@app.route('/admin/user/update_email/<int:user_id>/', methods=['POST'])
def update_email(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	if not user.verify_password(request.form['password']):
		return redirect(url_for('edit_user',user_id=user.id,msg='Wrong password'))
	user.email = request.form['email']
	session.add(user)
	session.commit()
	return "<html><body>Email updated <br/><br/> <a href=%s>back</a></body></html>"%url_for('edit_user',user_id=user.id)

@app.route('/admin/user/update_pass/<int:user_id>/', methods=['POST'])
def update_password(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	if request.form['newpass']!=request.form['newpass2']:
		return redirect(url_for('edit_user',user_id=user.id,msg="Passwords don't match"))
	if not user.update_password(request.form['password'],request.form['newpass']):
		return redirect(url_for('edit_user',user_id=user.id,msg='Wrong password'))	 
	session.add(user)
	session.commit()
	return "<html><body>Password updated <br/><br/> <a href=%s>back</a></body></html>"%url_for('edit_user',user_id=user.id)

@app.route('/admin/user/show/<int:user_id>/', methods=['GET','POST'])
def show_user(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	if request.method == 'POST':
		return redirect(url_for('show_users'))
	else:
		return render_template('user_details.html',user=user)
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=8080)