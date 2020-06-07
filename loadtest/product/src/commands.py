from app import app, db
import faker
import click


@app.cli.command('resetdb')
def resetdb_command():
    from models import Product
    Product.query.delete()
    db.session.commit()
    click.echo("Reseted DB")


@click.option('--count', prompt='number of products')
@app.cli.command('add_products')
def add_products_command(count):
    from models import Product

    fake = faker.Faker()

    products = []

    left = int(count)
    while left > 0:
        if left <= 1000:
            chunk_size = left
        else:
            chunk_size = 1000
        products = []
        for i in range(chunk_size):
            name = " ".join(fake.words(nb=3))
            description = "".join(fake.sentences())
            p = {"name": name, "description": description}
            products.append(p)

        db.session.bulk_insert_mappings(
            Product, products
        )
        left = left - chunk_size
        click.echo('Left: {}'.format(left))
    db.session.commit()

@app.cli.command('get_products')
def get_products_command():
    from models import Product
    for p in Product.query.all():
        click.echo("Name: {}, Description: {}".format(p.name, p.description))
