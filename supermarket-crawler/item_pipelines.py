from .models import Session, Product, Price


class PricePipeline(object):

    @staticmethod
    def process_item(item, spider):
        session = Session()
        product = session.query(Product).filter_by(shop=item["shop"], sku=item["sku"]).one_or_none()

        # Price.
        price = Price(
            price=item["price"],
            currency=item["currency"],
            update_time=item["update_time"]
        )

        if product is None:
            # Insert new product.
            product = Product(
                shop=item["shop"],
                sku=item["sku"],
                brand_name=item["brand_name"],
                name=item["name"],
                uom=item["uom"],
                url=item["url"],
                update_time=item["update_time"]
            )
            product.prices.append(price)
            session.add(product)
        else:
            # Update existing product.
            product.shop = item["shop"]
            product.sku = item["sku"]
            product.brand_name = item["brand_name"]
            product.name = item["name"]
            product.uom = item["uom"]
            product.url = item["url"]
            product.update_time = item["update_time"]
            product.prices.append(price)

        session.commit()

        return item
