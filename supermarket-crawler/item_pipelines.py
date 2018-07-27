from .models import Session, Product, Price


class PricePipeline(object):

    def process_item(self, item, spider):
        session = Session()

        product = session.query(Product).filter_by(shop=item["shop"], sku=item["sku"]).one_or_none()

        product_is_updated = any([
            product.shop == item["shop"],
            product.sku == item["sku"],
            product.brand_name == item["brand_name"],
            product.name == item["name"],
            product.uom == item["uom"],
            product.url == item["url"]
        ]) if product is not None else False

        if product is None or product_is_updated:
            product = Product(
                shop=item["shop"],
                sku=item["sku"],
                brand_name=item["brand_name"],
                name=item["name"],
                uom=item["uom"],
                url=item["url"],
                update_time=item["update_time"]
            )

        product.prices.append(Price(
            price=item["price"],
            currency=item["currency"],
            update_time=item["update_time"]
        ))

        session.add(product)
        session.commit()
