from app.extensions import ma
from app.models import Orders


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model= Orders
        include_fk = True


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
