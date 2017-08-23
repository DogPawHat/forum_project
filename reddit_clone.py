from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = 'teste'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Sub, User, Post, Comment
import sqlalchemy.orm.exc



engine = create_engine('sqlite:///reddit.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

@app.route('/')
def main():
	subs = dbsession.query(Sub).all()
	return render_template('index.html',subs=subs)
	

@app.route('/dashboard')
def dashboard():
	if 'uid' not in session:
		return 'Login required to access this feature'
	uid = session['uid']
	user = dbsession.query(User).filter_by(id=uid).one()
	return redirect(url_for('show_user',user_id=user.id))


@app.route('/signup', methods=['GET','POST'])
def new_user():
	if request.method == 'POST':
		print ' On post method'
		print ' will create new user'
		newUser = User(username=request.form['username'], password=request.form['password'], email=request.form['email'])
		print 'new user created'
		print 'adding to dbsession'
		dbsession.add(newUser)
		print 'added to dvsession'
		print 'updating dbsession'
		dbsession.commit()
		print 'done'
		return redirect(url_for('show_users'))
	else:
		return render_template('signup.html')

@app.route('/login/', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		try:
			user = dbsession.query(User).filter_by(username=request.form['username']).one()
		except sqlalchemy.orm.exc.NoResultFound:
			return "<html> <body>Wrong username or password <br/><br/> <a href=%s>back</a></body></html>"%url_for('login')
		if user.verify_password(request.form['password']):
			session['uid'] = user.id
			session['loggedin'] = True
			return redirect(url_for('main'))
		else:
			return "<html> <body>Wrong username or password <br/><br/> <a href=%s>back</a></body></html>"%url_for('login')
	else:
		if 'loggedin' in session:
			return 'User already logged in'
		return render_template('login.html')

@app.route('/logout/')
def logout():
	#if 'username' in session:
	session.pop('uid',None)
	session.pop('loggedin',None)
	return redirect(url_for('login'))



@app.route('/createsub/',methods=['GET','POST'])
def create_sub():
	if 'uid' not in session:
		return redirect(url_for('login'))

	if request.method == 'POST':
		newSub = Sub(name=request.form['subname'], descr=request.form['desc'],admin_id=int(session['uid']))
		dbsession.add(newSub)
		dbsession.commit()
		return redirect(url_for('show_sub',sid=newSub.id))
	return render_template('create_sub.html')


@app.route('/sub/<int:sid>')
def show_sub(sid):
	sub = dbsession.query(Sub).filter_by(id=sid).one()
	posts = dbsession.query(Post).filter_by(sub_id=sid)	
	return render_template('show_sub.html', posts=posts, sub=sub)

@app.route('/sub/<int:sid>/create_post',methods=['GET','POST'])
def create_post(sid):
	if 'uid' not in session:
		return redirect(url_for('login'))
	
	sub = dbsession.query(Sub).filter_by(id=sid).one()
	if request.method == 'POST':
		newPost = Post(title=request.form['title'], message=request.form['message'], sub_id=sid, user_id=int(session['uid']))
		dbsession.add(newPost)
		dbsession.commit()
		return redirect(url_for('show_post',sid=sub.id,pid=newPost.id))
	return render_template('create_post.html', sub=sub)	


@app.route('/sub/<int:sid>/post/<int:pid>')
def show_post(sid,pid):
	sub = dbsession.query(Sub).filter_by(id=sid).one()
	post = dbsession.query(Post).filter_by(id=pid).one()
	comments = dbsession.query(Comment).filter_by(post_id=post.id)
	return render_template('show_post.html', sub=sub, post=post, comments=comments)








@app.route('/admin/allusers')
def show_users():
	users = dbsession.query(User).all()
	return render_template('show_users.html',users=users)

@app.route('/admin/user/delete/<int:user_id>/')
def delete_user(user_id):
	user = dbsession.query(User).filter_by(id=user_id).one()
	dbsession.delete(user)
	dbsession.commit()
	return redirect(url_for('show_users'))

@app.route('/admin/user/edit/<int:user_id>/', methods=['GET','POST'])
def edit_user(user_id,msg=''):
	user = dbsession.query(User).filter_by(id=user_id).one()
	return render_template('edit_user.html',user=user)

@app.route('/admin/user/update_email/<int:user_id>/', methods=['POST'])
def update_email(user_id):
	user = dbsession.query(User).filter_by(id=user_id).one()
	if not user.verify_password(request.form['password']):
		return redirect(url_for('edit_user',user_id=user.id,msg='Wrong password'))
	user.email = request.form['email']
	dbsession.add(user)
	dbsession.commit()
	return "<html><body>Email updated <br/><br/> <a href=%s>back</a></body></html>"%url_for('edit_user',user_id=user.id)

@app.route('/admin/user/update_pass/<int:user_id>/', methods=['POST'])
def update_password(user_id):
	user = dbsession.query(User).filter_by(id=user_id).one()
	if request.form['newpass']!=request.form['newpass2']:
		return redirect(url_for('edit_user',user_id=user.id,msg="Passwords don't match"))
	if not user.update_password(request.form['password'],request.form['newpass']):
		return redirect(url_for('edit_user',user_id=user.id,msg='Wrong password'))	 
	dbsession.add(user)
	dbsession.commit()
	return "<html><body>Password updated <br/><br/> <a href=%s>back</a></body></html>"%url_for('edit_user',user_id=user.id)

@app.route('/admin/user/show/<int:user_id>/', methods=['GET','POST'])
def show_user(user_id):
	user = dbsession.query(User).filter_by(id=user_id).one()
	if request.method == 'POST':
		return redirect(url_for('show_users'))
	else:
		return render_template('user_details.html',user=user)
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=8080)
