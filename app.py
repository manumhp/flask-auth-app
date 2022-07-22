from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


from flask import Blueprint, render_template,redirect, url_for, request, flash
from flask_login import login_required, current_user
# from nbformat import read
from . import db
from .models import ImageInfo, Labeller, ResponseInfo
import random

from cProfile import label
from click import password_option
from flask import Blueprint, flash, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Labeller
from flask_login import login_user, login_required, logout_user


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


app = Flask(__name__)

if __name__ == '__main__':
    
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://oewvcycclwahny:65a2e3da4a52c1c2b26565ec9f41c9a94c5b7264a8f0c9c34c2f456c068e85ca@ec2-3-248-121-12.eu-west-1.compute.amazonaws.com:5432/daf2075s071c3c'
    # app.config['SERVER_NAME'] = '127.0.0.1:5001'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import Labeller
    @login_manager.user_loader

    def load_user(user_id):
        return Labeller.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    app.run(debug=True, host='localhost', port=int(os.env.get('PORT', 5000)))

    
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/dataset', methods=['GET'])
@login_required
def dataset():
    ## code from display random images
    ## get the urls for two random images from the database and display them
    image_1_url = request.args.get('image_1_url')
    image_2_url = request.args.get('image_2_url')
    image_1_id = request.args.get('image_1_id')
    image_2_id = request.args.get('image_2_id')


    if not image_1_url:
        images = read_random_images()
        url1 = images['image_1']['image_url']
        url2 = images['image_2']['image_url']        
        id1 = images['image_1']['image_id']
        id2 = images['image_2']['image_id']
    
    else:
        url1 = image_1_url
        url2 = image_2_url
        id1 = image_1_id
        id2 = image_2_id



    return render_template('dataset4.html', id=current_user.id, image_1_url = url1, image_2_url = url2, image_1_id = id1, image_2_id = id2)

def read_random_images():
    print("Random images generated")
    images = ImageInfo.query.all()
    results = [
        {
            "image_id": image.image_id,
            "image_url": image.image_url,
            "labelled": image.labelled
        } for image in images
    ]
    counts = int(len(results)/3)
    random_indices = random.sample(range(0, counts), 2)
    
    result_first = results[random_indices[0]]
    result_second = results[random_indices[1]]

    result = {"image_1": result_first, "image_2": result_second}
    return result

# @main.route('/dataset_entry_reshow', methods=['GET'])
# @login_required
# def dataset_entry_reshow(url1, url2, id1, id2):
#     return render_template('dataset4.html', id=current_user.id, image_1_url = url1, image_2_url = url2, image_1_id = id1, image_2_id = id2)

@main.route('/dataset', methods=['POST'])
@login_required
def dataset_post():
    image_1_score = request.form.get('slider1WithValue')
    image_2_score = request.form.get('slider2WithValue')

    user_id = current_user.id
    image_1_id = request.form.get('image_1_id')
    image_2_id = request.form.get('image_2_id')
    images = {}
    if image_1_score == '0' or image_2_score == '0':
        flash('No zeroes please')   
        print("Here")
        image_1 = ImageInfo.query.filter_by(image_id=image_1_id).first()
        image_1_url = image_1.image_url

        image_2 = ImageInfo.query.filter_by(image_id=image_2_id).first()
        image_2_url = image_2.image_url

        print("Image1 ")
        print(image_1)

        print("Image2")
        print(image_2)


        print("Image1 url ")
        print(image_1_url)

        print("Image2 url")
        print(image_2_url)
        images = {
            "image_1": {
                "image_url": image_1_url,
                "image_id": image_1_id,
            },
            "image_2": {
                "image_url": image_2_url,
                "image_id": image_2_id,
            }

        }
        # print(images['image_1']['image_url'])
        # print(images['image_2']['image_url'])
        # print(images['image_1']['image_id'])
        # print(images['image_2']['image_id'])

        # render_template('dataset4.html', id=current_user.id, image_1_url = image_1_url, image_2_url = image_2_url, image_1_id = image_1_id, image_2_id = image_2_id)
        # return
        # return redirect(url_for('main.dataset', images=images))
        return redirect(url_for('main.dataset', image_1_url=image_1_url, image_2_url=image_2_url, image_1_id=image_1_id, image_2_id= image_2_id))
    else:
        response_info = ResponseInfo.query.filter_by(image_1_id=image_1_id, image_2_id= image_2_id,
                                                    labeller_id = user_id).first()
        
        if response_info:
            flash('Dataset entry already exists in the database')        
            return redirect(url_for('main.dataset'))

        new_response = ResponseInfo(labeller_id = user_id, image_1_id=image_1_id, image_2_id=image_2_id, image_1_score=image_1_score, image_2_score=image_2_score)

        db.session.add(new_response)
        db.session.commit()

        return redirect(url_for('main.dataset'))
    
   

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    labeller = Labeller.query.filter_by(email=email).first()

    # check if the user exists
    # take the user supplied password, hash it and compare it against the hashed password stored in the database
    if not labeller or not check_password_hash(labeller.password, password):
        flash('Please check your login details and try again')
        return redirect(url_for('auth.login'))
    
    login_user(labeller, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    labeller = Labeller.query.filter_by(email=email).first()  ## if this returns a user,  the user already exists in the database

    if labeller:
        flash('Labeller already exists in the database')
        return redirect(url_for('auth.signup'))

    new_labeller = Labeller(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_labeller)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    # return render_template('logout.html')
