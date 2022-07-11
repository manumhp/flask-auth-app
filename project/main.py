from flask import Blueprint, render_template,redirect, url_for, request, flash
from flask_login import login_required, current_user
from nbformat import read
from . import db
from .models import ImageInfo, Labeller, ResponseInfo
import random

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
    ## get the urls for two random images from the database and display them

    images = read_random_images()
    url1 = images['image_1']['image_url']
    url2 = images['image_2']['image_url']
    

    id1 = images['image_1']['image_id']
    id2 = images['image_2']['image_id']

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

@main.route('/dataset', methods=['POST'])
@login_required
def dataset_post():
    image_1_score = request.form.get('slider1WithValue')
    image_2_score = request.form.get('slider2WithValue')

    user_id = current_user.id
    image_1_id = request.form.get('image_1_id')
    image_2_id = request.form.get('image_2_id')

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

        render_template('dataset4.html', id=current_user.id, image_1_url = image_1_url, image_2_url = image_2_url, image_1_id = image_1_id, image_2_id = image_2_id)
        # return

    response_info = ResponseInfo.query.filter_by(image_1_id=image_1_id, image_2_id= image_2_id,
                                                labeller_id = user_id).first()
    
    if response_info:
        flash('Dataset entry already exists in the database')        
        return redirect(url_for('main.dataset'))

    new_response = ResponseInfo(labeller_id = user_id, image_1_id=image_1_id, image_2_id=image_2_id, image_1_score=image_1_score, image_2_score=image_2_score)

    db.session.add(new_response)
    db.session.commit()

    return redirect(url_for('main.dataset'))