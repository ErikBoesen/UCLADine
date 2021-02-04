from app import app, db


meals_x_items = db.Table('meals_x_items',
    db.Column('meal_id', db.Integer, db.ForeignKey('meals.id'), nullable=False),
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), nullable=False),
)


class Location(db.Model):
    _to_expand = ()
    _to_exclude = ('managers', 'meals',)
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    open = db.Column(db.Boolean, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)

    meals = db.relationship('Meal', cascade='all,delete', back_populates='location')
