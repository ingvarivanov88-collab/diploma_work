import yaml
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductParameter


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

            # 3. Проходим по товарам
            for prod_data in cat_data.get('products', []):
                product, created = Product.objects.update_or_create(
                    name=prod_data['name'],
                    shop=shop,
                    defaults={
                        'category': category,
                        'description': prod_data.get('description', ''),
                        'price': prod_data['price'],
                        'quantity': prod_data.get('quantity', 0),
                        'is_active': True,
                    }
                )
                self.stdout.write(f"    Товар: {product.name} (создан: {created})")

                # 4. Параметры товара
                for param_data in prod_data.get('parameters', []):
                    ProductParameter.objects.update_or_create(
                        product=product,
                        name=param_data['name'],
                        defaults={'value': param_data['value']}
                    )

        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))