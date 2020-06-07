import os
import json

from flask import Flask, request, abort, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/search")
def search():
    from models import Product
    q = request.args.get('q')
    qlike='%' + q + '%'
    products = Product.query.filter(Product.description.like(qlike)|
                                    Product.name.like(qlike)).order_by(Product.id.desc()).limit(20).all()
    count = Product.query.filter(Product.description.like(qlike)|
                                 Product.name.like(qlike)).count()
    return {
        "allCount": count,
        "products": [
            {
                "name": p.name,
                "description": p.description
            }
            for p in products
        ]
    }

@app.route("/products/<int:product_id>")
def product(product_id):
    from models import Product

    product = Product.query.filter(Product.id == product_id).first()

    if product:
        return {"name": product.name, "description": product.description}
    else:
        return {"message": "Not such product"}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
