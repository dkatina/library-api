from app.blueprints.orders import orders_bp
from app.util.auth import token_required
from .schemas import order_schema, orders_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Orders, db, Items
from app.extensions import limiter



#CREATE ORDER - Brick and mortar shop
@orders_bp.route('', methods=['POST'])
@token_required
def create_order():
    try:
        data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Orders(**data)
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201


#Add item to order

@orders_bp.route('/<int:order_id>/add-item/<int:description_id>', methods=['PUT'])
def add_item(order_id, description_id):
    #Search for an item that         doesnt belong to an order & Fits this item description
    item = db.session.query(Items).where(Items.order_id==None, Items.desc_id==description_id).first()

    if not item:
        return jsonify("Item out of stock"), 404

    item.order_id = order_id #Creating the relationship between this item and this order
    db.session.commit()
    return jsonify({
        "message": f"Successfully added {item.item_description.item_name} to order {order_id}"
    })


@orders_bp.route('/<int:order_id>/checkout', methods=['GET'])
def checkout(order_id):

    order =db.session.get(Orders, order_id)
    items = {}
    total = 0
    for item in order.items: #looping over all items on this order
        name = item.item_description.item_name #looking up item name
        total += item.item_description.price #Adding the price of this item to the description
        if name in items: #checking to see if I already have this item in my items dict
            items[name]['qty'] += 1 #incrementing the quantity
        else: #if not
            items[name] = {'qty': 1, 'price': item.item_description.price}


    return jsonify({
        "order": order_schema.dump(order),
        "items": items,
        'total': total
    })




        
