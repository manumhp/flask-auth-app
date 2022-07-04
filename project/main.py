from flask import Blueprint, render_template,redirect, url_for, request
from flask_login import login_required, current_user
# from requests import request
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/dataset')
@login_required
def dataset():
    ## code from display random images
    return render_template('dataset.html', id=current_user.id)


@main.route('/dataset', methods=['POST'])
@login_required
def dataset_post():
    image_1_score = request.form.get('slider1WithValue')
    image_2_score = request.form.get('slider2WithValue')


    user_id = current_user.id
    image_1_url = request.form.get('image_1_id')
    image_2_url = request.form.get('image_2_id')

    print("Image 1: ", float(image_1_score))
    print("Image 2: ", float(image_2_score))

    # print("Image 1: ", image_11_score)
    # print("Image 2: ", image_22_score)
    

    ## get image_1_id and image_2_id from the image model
    # image_1_id = 
    # image_2_id = 


    # dataset_entry = DataSetEntry.query.filter_by(image_1_id=image_1_id, image_2_id = image_2_id, 
    #                                             image_1_score=image_1_score, image_2_score=image_2_score, user_id=user_id).first()

    
    # new_entry = DataSetEntry(user_id=user_id,image_1_id=image_1_id, image_2_id=image_2_id,  
    #                         image_1_score=image_1_score, image_2_score=image_2_score)                                                

    # check if the entry exists
    
    # if not dataset_entry:
        ## add it to the database....... REVIEW THE CODE FOR ADDING ENTRY TO A DIFFERENT TABLE
        # db.session.add(new_user)
        # db.session.commit()
        # pass
    
    # login_user(user, remember=remember)
    return redirect(url_for('main.dataset'))    