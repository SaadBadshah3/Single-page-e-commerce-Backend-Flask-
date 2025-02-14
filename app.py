from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow



app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///saad.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SECRET_KEY"]="SAADBADSHAH"


db=SQLAlchemy(app)
ma=Marshmallow(app)


class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    price=db.Column(db.Float,nullable=False)
    image_url=db.Column(db.String(255))

    def __init__(self,name,price,image_url):
        self.name=name
        self.price=price
        self.image_url=image_url

class Cart(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product_id=db.Column(db.Integer,db.ForeignKey("product.id"),nullable=False)
    quantity=db.Column(db.Integer,default=1)

    product=db.relationship("Product",backref="cart")

    def __init__(self,product_id,quantity):
        self.product_id=product_id
        self.quantity=quantity


class ProductsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Product
        load_instance=True      #When you set load_instance=True in a Marshmallow schema, it means that the schema will load data into an 
                                #existing instance of a model rather than creating a new one. 
                                #This is particularly useful when you want to update an existing database record.


class CartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Cart
        load_instance=True
        include_fk=True


product_schema=ProductsSchema()
cart_schema=CartSchema()
product_schemas=ProductsSchema(many=True)
cart_schemas=CartSchema(many=True)


@app.route("/products",methods=["GET"])
def products():
    products=Product.query.all()
    print(products)
    res=product_schemas.dump(products)
    return jsonify(res)



@app.route("/products",methods=["POST"])
def add():
    data=request.get_json()
    name=data.get("name")
    price=data.get("price")
    image_url=data.get("image_url")

    if not name:
        return jsonify({"error":"Please enter name"})
    if not price:
        return jsonify({"error":"Please add price"})
    
    add=Product(name,price,image_url)
    db.session.add(add)
    db.session.commit()
    return jsonify({"Successfull":"Added"})



@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"})

@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    new_cart_item = Cart(product_id, quantity)
    db.session.add(new_cart_item)
    db.session.commit()
    return cart_schema.jsonify(new_cart_item)

@app.route("/cart", methods=["GET"])
def get_cart():
    cart_items = Cart.query.all()
    return cart_schemas.jsonify(cart_items)

@app.route("/cart/<int:id>", methods=["DELETE"])
def remove_from_cart(id):
    cart_item = Cart.query.get(id)
    if not cart_item:
        return jsonify({"error": "Item not found in cart"}), 404
    
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"})





if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)