from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkedin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import LinkedInUser, LinkedInLiker

@app.route('/')
def home():
    return "LinkedIn Data Scraper API"

@app.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    data = request.get_json()
    
    for user in data['users']:
        linkedin_user = LinkedInUser(
            name=user['name'], 
            linkedin_id=user['linkedin_id'], 
            title=user['title']
        )
        db.session.add(linkedin_user)
        
        for liker in user['likers']:
            linkedin_liker = LinkedInLiker(
                linkedin_user_id=user['linkedin_id'],
                liker_user_name=liker['liker_user_name'],
                liker_user_id=liker['liker_user_id'],
                post_id=liker['post_id'],
                likers_title=liker['likers_title']
            )
            db.session.add(linkedin_liker)
    
    db.session.commit()
    return jsonify({"message": "Data uploaded successfully"}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = LinkedInUser.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/user/<linkedin_id>', methods=['GET'])
def get_user(linkedin_id):
    user = LinkedInUser.query.filter_by(linkedin_id=linkedin_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@app.route('/user/<linkedin_id>', methods=['PUT'])
def update_user(linkedin_id):
    data = request.get_json()
    user = LinkedInUser.query.filter_by(linkedin_id=linkedin_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.name = data.get('name', user.name)
    user.title = data.get('title', user.title)
    db.session.commit()
    return jsonify({"message": "User updated successfully"})

@app.route('/user/<linkedin_id>', methods=['DELETE'])
def delete_user(linkedin_id):
    user = LinkedInUser.query.filter_by(linkedin_id=linkedin_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    LinkedInLiker.query.filter_by(linkedin_user_id=linkedin_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})

@app.route('/likers', methods=['GET'])
def get_likers():
    likers = LinkedInLiker.query.all()
    return jsonify([liker.to_dict() for liker in likers])

@app.route('/liker/<int:liker_id>', methods=['GET'])
def get_liker(liker_id):
    liker = LinkedInLiker.query.get(liker_id)
    if not liker:
        return jsonify({"error": "Liker not found"}), 404
    return jsonify(liker.to_dict())

@app.route('/liker/<int:liker_id>', methods=['PUT'])
def update_liker(liker_id):
    data = request.get_json()
    liker = LinkedInLiker.query.get(liker_id)
    if not liker:
        return jsonify({"error": "Liker not found"}), 404

    liker.liker_user_name = data.get('liker_user_name', liker.liker_user_name)
    liker.liker_user_id = data.get('liker_user_id', liker.liker_user_id)
    liker.post_id = data.get('post_id', liker.post_id)
    liker.likers_title = data.get('likers_title', liker.likers_title)
    db.session.commit()
    return jsonify({"message": "Liker updated successfully"})

@app.route('/liker/<int:liker_id>', methods=['DELETE'])
def delete_liker(liker_id):
    liker = LinkedInLiker.query.get(liker_id)
    if not liker:
        return jsonify({"error": "Liker not found"}), 404

    db.session.delete(liker)
    db.session.commit()
    return jsonify({"message": "Liker deleted successfully"})

@app.route('/user/<linkedin_id>/likers', methods=['GET'])
def get_likers_by_user(linkedin_id):
    user = LinkedInUser.query.filter_by(linkedin_id=linkedin_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    likers = LinkedInLiker.query.filter_by(linkedin_user_id=linkedin_id).all()
    return jsonify([liker.to_dict() for liker in likers])

if __name__ == '__main__':
    app.run(debug=True)
