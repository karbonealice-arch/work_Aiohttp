from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage for ads
ads = {}
next_id = 1


@app.route('/ads', methods=['POST'])
def create_ad():
    global next_id

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    required_fields = ['title', 'description', 'owner']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    ad_id = next_id
    next_id += 1

    ad = {
        'id': ad_id,
        'title': data['title'],
        'description': data['description'],
        'creation_date': datetime.now().isoformat(),
        'owner': data['owner']
    }

    ads[ad_id] = ad

    return jsonify(ad), 201


@app.route('/ads', methods=['GET'])
def get_ads():
    ad_id = request.args.get('id')

    if ad_id:
        ad_id = int(ad_id)
        if ad_id not in ads:
            return jsonify({'error': 'Ad not found'}), 404
        return jsonify(ads[ad_id])

    return jsonify(list(ads.values()))


@app.route('/ads/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    if ad_id not in ads:
        return jsonify({'error': 'Ad not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    updatable_fields = ['title', 'description', 'owner']
    for field in updatable_fields:
        if field in data:
            ads[ad_id][field] = data[field]

    return jsonify(ads[ad_id])


@app.route('/ads/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    if ad_id not in ads:
        return jsonify({'error': 'Ad not found'}), 404

    deleted_ad = ads.pop(ad_id)
    return jsonify(deleted_ad)


if __name__ == '__main__':
    app.run(debug=True)
