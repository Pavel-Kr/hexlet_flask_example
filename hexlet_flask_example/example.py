from flask import Flask, render_template, \
    request, redirect, url_for, flash, get_flashed_messages, make_response, \
    session

from .database import Database


app = Flask(__name__)

app.secret_key = 'secret_key'


@app.route('/')
def hello_world():
    return redirect(url_for('users_get'), 302)


def validate(user):
    errors = {}
    if not user['name']:
        errors['name'] = 'Nickname must contain at least 1 character'
    if not user['email']:
        errors['email'] = 'Email cannot be blank'
    return errors


@app.get('/users')
def users_get():
    db = Database(request.cookies)
    users = db.content()
    messages = get_flashed_messages(with_categories=True)
    search = request.args.get('user', default='', type=str)
    filtered_users = filter(lambda user: search in user['name'], users)
    response = make_response(render_template(
        'users/index.html',
        users=filtered_users,
        search=search,
        messages=messages,
        email=session.get('email')
    ))
    db.set_cookies(response)
    return response


@app.post('/users')
def users_post():
    db = Database(request.cookies)
    user = request.form.to_dict()
    print(user)
    errors = validate(user)
    print(errors)
    if errors:
        response = make_response(render_template(
            'users/new.html',
            user=user,
            errors=errors
        ), 422)
        db.set_cookies(response)
        return response

    new_user = {
        'name': user['name'],
        'email': user['email']
    }
    db.save(new_user)
    flash('User was added', 'success')
    response = make_response(redirect(url_for('users_get'), 302))
    db.set_cookies(response)
    return response


@app.get('/users/new')
def users_new_get():
    db = Database(request.cookies)
    response = make_response(render_template(
        'users/new.html',
        user={},
        errors={}
    ))
    db.set_cookies(response)
    return response


@app.route('/users/<int:id>')
def users_id_get(id):
    db = Database(request.cookies)
    user = db.find('id', id)
    if not user:
        response = make_response('Page not found', 404)
        db.set_cookies(response)
        return response

    response = make_response(render_template(
        'users/show.html',
        user=user
    ))
    db.set_cookies(response)
    return response
    


@app.get('/users/<int:id>/edit')
def edit_user(id):
    db = Database(request.cookies)
    user = db.find('id', id)
    errors = []
    
    response = make_response(render_template(
        'users/edit.html',
        user=user,
        errors=errors
    ))
    db.set_cookies(response)
    return response


@app.post('/users/<int:id>/patch')
def patch_user(id):
    db = Database(request.cookies)
    user = db.find('id', id)
    data = request.form.to_dict()

    errors = validate(data)
    if errors:
        response = make_response(render_template(
            'users/edit.html',
            user=user,
            errors=errors
        ), 422)
        db.set_cookies(response)
        return response
    
    user['name'] = data['name']
    user['email'] = data['email']
    db.save(user)
    flash('User was updated', 'success')
    response = make_response(redirect(url_for('users_get'), 302))
    db.set_cookies(response)
    return response


@app.post('/users/<int:id>/delete')
def delete_user(id):
    db = Database(request.cookies)
    db.delete('id', id)
    flash('User was deleted', 'success')
    response = make_response(redirect(url_for('users_get'), 302))
    db.set_cookies(response)
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template(
            'users/login.html',
            user={},
            errors={}
        )
    elif request.method == 'POST':
        user = request.form.to_dict()
        errors = {}
        if not user['email']:
            errors['email'] = "Can't be blank"
        if errors:
            return render_template(
                'users/login.html',
                user=user,
                errors=errors
            ), 422
        session['email'] = user['email']
        return redirect(url_for('users_get'), 302)
    

@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('users_get'), 302)
