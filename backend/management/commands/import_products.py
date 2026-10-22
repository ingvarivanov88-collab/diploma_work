import yaml
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class Command(BaseCommand):
    help = 'Импорт товаров из YAML-файла'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', type=str, help='Путь к YAML-файлу')

    def handle(self, *args, **options):
        file_path = options['yaml_file']
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        shop_name = data.get('shop')
        categories = data.get('categories', [])

        # 1. Создаём магазин
        shop, _ = Shop.objects.get_or_create(name=shop_name)
        self.stdout.write(f"Магазин: {shop.name}")

        # 2. Проходим по категориям
        for cat_data in categories:
            cat_name = cat_data.get('name')
            category, _ = Category.objects.get_or_create(name=cat_name)
            category.shops.add(shop)
            self.stdout.write(f"  Категория: {category.name}")

            # 3. Проходим по товарам внутри категории
            products = cat_data.get('products', [])
            for prod_data in products:
                # Создаём Product
                product, _ = Product.objects.get_or_create(
                    name=prod_data['name'],
                    category=category
                )

                # Создаём ProductInfo (или обновляем, если уже есть)
                # Используем счётчик для external_id, если его нет
                external_id = prod_data.get('id', 0)
                if not external_id:
                    # Если id нет, генерируем его на основе названия (чтобы было уникально)
                    external_id = abs(hash(prod_data['name'])) % 1000000

                product_info, created = ProductInfo.objects.update_or_create(
                    external_id=external_id,
                    product=product,
                    shop=shop,
                    defaults={
                        'model': prod_data.get('model', ''),
                        'price': prod_data['price'],
                        'price_rrc': prod_data.get('price_rrc', prod_data['price']),
                        'quantity': prod_data.get('quantity', 0),
                    }
                )
                self.stdout.write(f"    Товар: {product.name} (создан: {created})")

                # 4. Параметры
                parameters = prod_data.get('parameters', [])
                for param in parameters:
                    parameter, _ = Parameter.objects.get_or_create(name=param['name'])
                    ProductParameter.objects.update_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={'value': str(param['value'])}
                    )

        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))