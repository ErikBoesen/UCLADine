from app import app, db


meals_x_items = db.Table('meals_x_items',
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), nullable=False),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), nullable=False),
)


class Location(db.Model):
    _to_expand = ()
    _to_exclude = ('managers', 'meals',)
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    open = db.Column(db.Boolean, nullable=False)
    #latitude = db.Column(db.Float, nullable=False)
    #longitude = db.Column(db.Float, nullable=False)
    #address = db.Column(db.String, nullable=False)
    #phone = db.Column(db.String, nullable=False)

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


addons = db.Table('addons',
    db.Column('parent_item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('child_item_id', db.Integer, db.ForeignKey('item.id'))
)


class Item(db.Model):
    _to_expand = ('addons')
    _to_exclude = ('meal', 'nutrition', 'parent')
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    ingredients = db.Column(db.String)
    course = db.Column(db.String)
    image_url = db.Column(db.String)

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

    addons = db.relationship(
        'Item', secondary=addons,
        primaryjoin=(addons.c.parent_item_id == id),
        secondaryjoin=(addons.c.child_item_id == id),
        backref=db.backref('parent', lazy='dynamic'), lazy='dynamic')
    nutrition = db.relationship('Nutrition', cascade='all,delete,delete-orphan', uselist=False, back_populates='item')


class Nutrition(db.Model):
    _to_expand = ()
    _to_exclude = ('item',)
    serving_size = db.Column(db.String)
    calories = db.Column(db.Integer)
    fat_calories = db.Column(db.Integer)

    total_fat = db.Column(db.String)
    saturated_fat = db.Column(db.String)
    trans_fat = db.Column(db.String)
    cholesterol = db.Column(db.String)
    sodium = db.Column(db.String)
    total_carbohydrate = db.Column(db.String)
    dietary_fiber = db.Column(db.String)
    total_sugars = db.Column(db.String)
    protein = db.Column(db.String)
    #vitamin_a = db.Column(db.String)
    #vitamin_c = db.Column(db.String)
    #calcium = db.Column(db.String)
    #iron = db.Column(db.String)

    # Percent Daily Value
    total_fat_pdv = db.Column(db.Integer)
    saturated_fat_pdv = db.Column(db.Integer)
    #trans_fat_pdv = db.Column(db.Integer)
    cholesterol_pdv = db.Column(db.Integer)
    sodium_pdv = db.Column(db.Integer)
    total_carbohydrate_pdv = db.Column(db.Integer)
    dietary_fiber_pdv = db.Column(db.Integer)
    #total_sugars_pdv = db.Column(db.Integer)
    #protein_pdv = db.Column(db.Integer)
    vitamin_a_pdv = db.Column(db.Integer)
    vitamin_c_pdv = db.Column(db.Integer)
    calcium_pdv = db.Column(db.Integer)
    iron_pdv = db.Column(db.Integer)

    item_id = db.Column(db.String, db.ForeignKey('item.id'), primary_key=True)
    item = db.relationship('Item', back_populates='nutrition')
