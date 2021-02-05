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


class Meal(db.Model):
    _to_expand = ()
    _to_exclude = ('location', 'items')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String)
    end_time = db.Column(db.String)

    location_id = db.Column(db.String, db.ForeignKey('location.id'))
    location = db.relationship('Location', back_populates='meals')

    items = db.relationship(
        'Item', secondary=meals_x_items, lazy='subquery',
        backref=db.backref('meals', lazy=True))


class Item(db.Model):
    _to_expand = ()
    _to_exclude = ('meal', 'nutrition')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String)
    course = db.Column(db.String)

    vegetarian = db.Column(db.Boolean, default=False)
    vegan = db.Column(db.Boolean, default=False)
    halal = db.Column(db.Boolean, default=False)

    low_carbon = db.Column(db.Boolean, default=False)
    high_carbon = db.Column(db.Boolean, default=False)

    peanuts = db.Column(db.Boolean, default=False)
    tree_nuts = db.Column(db.Boolean, default=False)
    wheat = db.Column(db.Boolean, default=False)
    gluten = db.Column(db.Boolean, default=False)
    soy = db.Column(db.Boolean, default=False)
    dairy = db.Column(db.Boolean, default=False)
    eggs = db.Column(db.Boolean, default=False)
    crustacean_shellfish = db.Column(db.Boolean, default=False)
    fish = db.Column(db.Boolean, default=False)

    nutrition = db.relationship('Nutrition', cascade='all,delete,delete-orphan', uselist=False, back_populates='item')

