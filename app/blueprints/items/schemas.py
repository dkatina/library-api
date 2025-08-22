from app.extensions import ma
from app.models import Items, ItemDescriptions


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Items
        include_fk = True

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


class ItemDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
         model = ItemDescriptions

item_description_schema = ItemDescriptionSchema()
item_descriptions_schema = ItemDescriptionSchema(many=True)