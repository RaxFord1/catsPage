from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import select

app = Flask(__name__, template_folder="./resources/html")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    class_type = db.Column(db.String(1), nullable=False)
    gender = db.Column(db.Boolean, nullable=False)  # 0 - мальчик 1 - девочка TODO: сделать проверку, что 0 или 1
    available = db.Column(db.Boolean)  # бронь 0 - забронирован 1 - свободно TODO: сделать проверку, что 0 или 1

    image = db.Column(db.BLOB)

    color = db.Column(db.String(50), nullable=False)  # Окрас

    birthday = db.Column(db.DateTime, nullable=False)  # День рождения
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'class_type': self.class_type,
            'gender': 'Male' if self.gender == False else 'Female',
            'available': 'Not available' if self.available == False else 'Available',
            'color': self.color,
            'birthday': self.birthday.strftime('%Y-%m-%d')
        }

    @property
    def serialize_many2many(self):
        """
        Return object's relations in easily serializable format.
        NB! Calls many2many's serialize property.
        """
        return [item.serialize for item in self.many2many]

    def __repr__(self):
        return '<Cat %r>' % self.id


class Kitty(db.Model):
    # маленькое животное
    # id = db.Column(db.Integer, primary_key = True)

    cat_id = db.Column(db.Integer, db.ForeignKey('cat.id', ondelete="CASCADE"), primary_key=True)
    mom = db.Column(db.Integer, db.ForeignKey('cat.id', ondelete="CASCADE"))
    dad = db.Column(db.Integer, db.ForeignKey('cat.id', ondelete="CASCADE"))

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Kitty %r>' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)

    gender = db.Column(db.Boolean)  # TODO: сделать проверку, что 0 или 1

    birthday = db.Column(db.DateTime)

    city = db.Column(db.String(50), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


class Booking(db.Model):
    # маленькое животное
    id = db.Column(db.Integer, primary_key=True)

    cat_id = db.Column(db.Integer, db.ForeignKey('cat.id', ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    comment = db.Column(db.String(200))

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Kitty %r>' % self.id


@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        gender = request.form['gender']  # TODO: сделать проверку, что 0 или 1
        if gender == 'male':
            gender = 0
        else:
            gender = 1
        birthday = datetime.strptime(request.form['birthday'], "%Y-%m-%d")
        city = request.form['city']

        user = User(first_name=first_name, last_name=last_name, email=email,
                    phone_number=phone_number, gender=gender, birthday=birthday, city=city
                    )

        print(user)
        print(first_name, last_name, email, phone_number, gender, birthday, city)
        try:
            # TODO: навешать логики, если юзер уже создан
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'Couldnt insert {e}'

    return render_template('index.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    return render_template('index.html', registered="asd")

    # name = db.Column(db.String(), nullable=False)
    # description = db.Column(db.String(200), nullable=False)

    # class_type = db.Column(db.String(1), nullable=False)
    # gender = db.Column(db.Boolean, nullable=False) # 0 - мальчик 1 - девочка TODO: сделать проверку, что 0 или 1
    # available = db.Column(db.Boolean) # бронь 0 - забронирован 1 - свободно TODO: сделать проверку, что 0 или 1

    # image = db.Column(db.BLOB)

    # color = db.Column(db.String(50), nullable=False) # Окрас

    # birthday = db.Column(db.DateTime, nullable=False) # День рождения


@app.route("/cats", methods=['GET'])
def cats():
    cats = Cat.query.order_by(Cat.class_type).all()
    return render_template('cat.html', cats=cats)


@app.route("/cats.json", methods=['GET'])
def cats_json():
    cats = Cat.query.order_by(Cat.class_type).all()
    allpets = [cat.serialize for cat in cats]
    return jsonify(allpets)


@app.route("/cat/<int:id>", methods=['GET'])
def cat(id):
    cat = Cat.query.filter_by(id=id).first()
    return jsonify(cat.serialize)


@app.route("/admin/cat", methods=['POST'])
def admin_cat_post():
    form = request.form
    name = form['name']
    description = form['description']
    class_type = form['class_type']
    available = form['available']  # 0/1
    gender = form['gender']  # 0/1
    color = form['color']
    birthday = form['birthday']
    # image = form['image']

    if gender.lower() == 'male':
        gender = 0
    else:
        gender = 1

    if available.lower() == 'available':
        available = 1
    else:
        available = 0

    birthday = datetime.strptime(birthday, "%Y-%m-%d")

    cat = Cat(name=name, description=description, class_type=class_type,
              available=available, image=bytes([]), gender=gender, color=color,
              birthday=birthday
              )

    print(cat)
    try:
        db.session.add(cat)
        db.session.commit()
        return {"result": "Ok", "id": cat.id}
    except Exception as e:
        return {"result": f'Couldnt insert {e}'}


@app.route("/admin/cat/<int:id>", methods=['GET', 'DELETE', 'UPDATE'])
def admin_cat_change(id):
    if request.method == 'GET':
        cat = Cat.query.filter_by(id=id).first()
        return jsonify(cat.serialize)
    elif request.method == 'DELETE':
        cat = Cat.query.filter_by(id=id).delete()
        try:
            db.session.commit()
            return {"result": "Ok"}
        except Exception as e:
            return {"result": f'Couldnt delete {e}'}
    else:
        # Update
        cat = Cat.query.filter_by(id=id).first()
        form = request.get_json()
        name = form['name']
        description = form['description']
        class_type = form['class_type']
        available = form['available']  # 0/1
        gender = form['gender']  # 0/1
        color = form['color']
        birthday = form['birthday']

        if gender.lower() == 'male':
            gender = 0
        else:
            gender = 1

        if available.lower() == 'available':
            available = 1
        else:
            available = 0

        birthday = datetime.strptime(birthday, "%Y-%m-%d")

        cat.name = name
        cat.description = description
        cat.class_type = class_type
        cat.available = available
        cat.gender = gender
        cat.color = color
        cat.birthday = birthday

        try:
            db.session.commit()
            return {"result": "Ok", "id": cat.id}
        except Exception as e:
            return {"result": f'Couldnt insert {e}'}


@app.route("/kitty", methods=['GET'])
def kitty():
    kitties = Kitty.query.join(Cat, Cat.id == Kitty.cat_id).add_columns(
        Cat.name, Cat.gender, Cat.available, Cat.birthday,
        Cat.description, Cat.class_type, Cat.color
    ).all()

    return render_template('cat.html', cats=kitties)


@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/")
def landing():
    return render_template('landing.html')


@app.route("/gallery")
def gallery():
    return render_template('gallery.html')


@app.route("/admin")
def admin_cat():
    return render_template('admin_cat.html')


def fillbd():
    # todo: добавить картинку
    cat1 = Cat(name="Кузя", description="Первый счастливчик в нашей маленькой воображаемой семье",
               class_type="A", gender=0, available=0, color="red",
               birthday=date(2002, 2, 17)
               )

    cat2 = Cat(name="Ася",
               description="Второй счастливчик в нашей уже не очень маленькой но всё ещё воображаемой семье",
               class_type="A", gender=1, available=1, color="white",
               birthday=date(2003, 12, 17)
               )

    cat3 = Cat(name="Руся", description="Маленькая девочка, родившаяся у наших самопровозглашённых Адама и Евы",
               class_type="B", gender=1, available=1, color="white",
               birthday=date(2004, 12, 17)
               )

    cat4 = Cat(name="Арчи",
               description="Большой мальчик, который чуть не разрушил вселенную своим появлением. Аж на столько дрожали стены от криков Аси",
               class_type="B", gender=0, available=1, color="white",
               birthday=date(2004, 12, 17)
               )

    cat_has_parents1 = Kitty(cat_id=3, mom=2, dad=1)
    cat_has_parents2 = Kitty(cat_id=4, mom=2, dad=1)

    user = User(first_name="Dima", last_name="Dzundza", email="dzun@gm",
                phone_number="+38073354236", gender=0, birthday=date(2002, 2, 17), city="Mykolaiv")

    try:
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.add(cat3)
        db.session.add(cat4)
        db.session.add(cat_has_parents1)
        db.session.add(cat_has_parents2)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'Couldnt insert {e}'


if __name__ == "__main__":
    #fillbd()

    app.run(debug=True)