from app.blueprints.items import items_bp
from .schemas import item_schema, items_schema, item_description_schema, item_descriptions_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Items, db, ItemDescriptions
from app.extensions import limiter


@items_bp.route('/descriptions', methods=['POST'])
def create_item_description():
    try:
        data = item_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_description = ItemDescriptions(**data)
    db.session.add(new_description)
    db.session.commit()
    return item_description_schema.jsonify(new_description), 201


@items_bp.route('/descriptions', methods=['GET'])
def get_item_descriptions():
    item_descriptions = db.session.query(ItemDescriptions).all()
    return item_descriptions_schema.jsonify(item_descriptions), 200


@items_bp.route('/<int:description_id>', methods=['POST'])
def create_item(description_id):
    quantity = request.args.get('qty', 1, type=int) #Can also add a query parameter of qty=10
    count = 0
    while count < quantity:
        new_item = Items(desc_id=description_id) #Creating a new item
        db.session.add(new_item)
        count += 1

    db.session.commit()
    return jsonify(f"You have successfully created {quantity} item {description_id}(s)")

#Get all items
@items_bp.route('', methods=['GET'])
def get_items():
    items = db.session.query(Items).all()
    return items_schema.jsonify(items), 200