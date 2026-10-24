from django.db import migrations


PUER_PRODUCTS = [
    {
        'name': 'Смола шу пуэра',
        'slug': 'smola-shu-puera',
        'description': (
            'Порционный формат шу пуэра в виде плотной чайной пасты. Небольшую порцию удобно '
            'растворить в горячей воде дома или в дороге. На упаковке указано, что продукт '
            'изготовлен из сырья древних чайных деревьев.\n\n'
            'Для приготовления добавьте порцию в чашку или чайник и залейте горячей водой. '
            'Количество воды и насыщенность настоя регулируйте по вкусу. Состав и способ '
            'заваривания перед продажей сверьте с маркировкой поставщика.'
        ),
        'price': '320.00',
        'weight': '',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
    {
        'name': 'Шу пуэр Иу Гуафэн Чжай',
        'slug': 'shu-puer-yiwu-guafeng-zhai',
        'description': (
            'Прессованный шу пуэр из серии Иу Гуафэн Чжай. На упаковке указан вес 357 г. '
            'Формат блина удобно хранить, делить на порции и заваривать проливами. Шу пуэр '
            'подойдёт тем, кто предпочитает тёмный настой и мягкий, согревающий характер чая.\n\n'
            'Для проливного заваривания возьмите около 5–7 г на небольшую гайвань, промойте '
            'листья горячей водой и заваривайте короткими проливами. Температуру воды '
            'подбирайте в диапазоне 90–100 °C.'
        ),
        'price': '890.00',
        'weight': '357',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
    {
        'name': 'Шу пуэр «Блестящее процветание»',
        'slug': 'shu-puer-blestyashchee-protsvetanie',
        'description': (
            'Прессованный шу пуэр «Блестящее процветание» от чайной фабрики Мэнхай. На '
            'упаковке указаны Юньнань и вес 357 г. Плотный блин удобно разделить на порции '
            'для неспешного домашнего чаепития или подарка.\n\n'
            'Заваривайте горячей водой температурой 90–100 °C. Для гайвани начните с 5–7 г '
            'чая и коротких проливов, постепенно увеличивая время настаивания.'
        ),
        'price': '760.00',
        'weight': '357',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
    {
        'name': 'Шу пуэр «Впечатление от Иу»',
        'slug': 'shu-puer-vpechatlenie-yiwu',
        'description': (
            'Шу пуэр «Впечатление от Иу» — прессованный чай в блине весом 357 г. Название '
            'и оформление упаковки отсылают к чайной традиции Иу. Блин можно разламывать '
            'на небольшие порции и заваривать несколько раз, постепенно меняя крепость настоя.\n\n'
            'Рекомендуем начать с 5–7 г на гайвань и воды температурой 90–100 °C. '
            'Для первого пролива достаточно нескольких секунд.'
        ),
        'price': '820.00',
        'weight': '357',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
    {
        'name': 'Шу пуэр «Снежная гора»',
        'slug': 'shu-puer-snezhnaya-gora',
        'description': (
            'Шу пуэр «Снежная гора» от Фухай — компактный прессованный блин весом 100 г, '
            'указанным на упаковке. Небольшой формат подходит для знакомства с чаем или '
            'для того, чтобы взять его с собой.\n\n'
            'Заваривайте водой температурой 90–100 °C. Для чайника или гайвани используйте '
            '5–7 г и короткие проливы; при настаивании в кружке уменьшите количество чая '
            'и подберите время по вкусу.'
        ),
        'price': '390.00',
        'weight': '100',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
    {
        'name': 'Шу пуэр Менку «Му Е Чунь»',
        'slug': 'shu-puer-mengku-muye-chun',
        'description': (
            'Прессованный шу пуэр Менку «Му Е Чунь». На упаковке указан вес 400 г. '
            'Крупный блин удобно хранить и отламывать от него порции для ежедневного '
            'заваривания. Подойдёт для чаепития проливами или в чайнике.\n\n'
            'Используйте воду температурой 90–100 °C. Начните с 5–7 г на небольшую '
            'посуду и коротких проливов, регулируя крепость количеством листа и временем.'
        ),
        'price': '790.00',
        'weight': '400',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
    {
        'name': 'Шу пуэр Мэнхай «Первозданный вкус древних деревьев», 2017',
        'slug': 'shu-puer-menghai-drevnie-derevya-2017',
        'description': (
            'Шу пуэр Мэнхай «Первозданный вкус древних деревьев», 2017 года. На упаковке '
            'указан вес 357 г. Прессованный блин удобно хранить и заваривать порциями. '
            'Год и название приведены по маркировке исходной упаковки.\n\n'
            'Для проливного заваривания возьмите 5–7 г на гайвань, используйте воду '
            'температурой 90–100 °C и начинайте с коротких проливов.'
        ),
        'price': '950.00',
        'weight': '357',
        'images': [
            'image_01.png', 'image_02.png', 'image_03.png', 'image_04.png',
        ],
    },
]


def seed_puer_products(apps, schema_editor):
    Category = apps.get_model('main', 'Category')
    Product = apps.get_model('main', 'Product')
    ProductImage = apps.get_model('main', 'ProductImage')

    category, _ = Category.objects.get_or_create(
        slug='puer',
        defaults={'name': 'Пуэр'},
    )

    # Обновляем существующую карточку Менку на русское описание и добавляем
    # первое фото в миниатюры. Основное фото уже является самым ранним снимком.
    sheng, created = Product.objects.get_or_create(
        slug='menku-shentaj-shen-z-ekosadiv-menku-2010',
        defaults={
            'category': category,
            'name': 'Менку Шентай «Шэн из экосадов Менку», 2010',
            'description': (
                'Выдержанный шэн пуэр Менку Шентай 2010 года. На упаковке указан вес 880 г. '
                'Прессованный блин можно хранить и разламывать на порции для заваривания. '
                'Год, производитель и вес приведены по маркировке упаковки.\n\n'
                'Для проливного заваривания возьмите 5–7 г на гайвань и используйте воду '
                'температурой 90–100 °C. Начните с коротких проливов и увеличивайте время '
                'по вкусу.'
            ),
            'price': '934.00',
            'weight': '880',
            'image': 'products/Менку_Шентай_Шен_з_екосадів_Менку_2010.png',
            'available': True,
            'attr_type': 'Пуэр',
            'attr_origin': 'Китай, Юньнань',
            'attr_temperature': '90–100°C',
            'attr_time': '1–3 минуты',
        },
    )
    if not created:
        sheng.name = 'Менку Шентай «Шэн из экосадов Менку», 2010'
        sheng.description = (
            'Выдержанный шэн пуэр Менку Шентай 2010 года. На упаковке указан вес 880 г. '
            'Прессованный блин можно хранить и разламывать на порции для заваривания. '
            'Год, производитель и вес приведены по маркировке упаковки.\n\n'
            'Для проливного заваривания возьмите 5–7 г на гайвань и используйте воду '
            'температурой 90–100 °C. Начните с коротких проливов и увеличивайте время '
            'по вкусу.'
        )
        sheng.attr_type = 'Пуэр'
        sheng.attr_origin = 'Китай, Юньнань'
        sheng.attr_temperature = '90–100°C'
        sheng.attr_time = '1–3 минуты'
        sheng.save(update_fields=[
            'name', 'description', 'attr_type', 'attr_origin',
            'attr_temperature', 'attr_time',
        ])

    sheng_gallery = [
        (0, sheng.image.name),
        (1, 'products/Менку_Шентай_Шен_з_екосадів_Ме1.png'),
        (2, 'products/Менку_Шентай_Шен_з_екосадів_Менку3.png'),
        (3, 'products/Знімок_екрана_2026-10-23_192825.png'),
    ]
    for order, image_name in sheng_gallery:
        image, _ = ProductImage.objects.get_or_create(
            product=sheng,
            image=image_name,
            defaults={'order': order},
        )
        if image.order != order:
            image.order = order
            image.save(update_fields=['order'])

    for item in PUER_PRODUCTS:
        product, _ = Product.objects.get_or_create(
            slug=item['slug'],
            defaults={
                'category': category,
                'name': item['name'],
                'description': item['description'],
                'price': item['price'],
                'weight': item['weight'],
                'image': f"products/puer/{item['slug']}/{item['images'][0]}",
                'available': True,
                'attr_type': 'Пуэр',
                'attr_origin': 'Китай, Юньнань',
                'attr_temperature': '90–100°C',
                'attr_time': '1–3 минуты',
            },
        )

        for order, filename in enumerate(item['images']):
            image, _ = ProductImage.objects.get_or_create(
                product=product,
                image=f"products/puer/{item['slug']}/{filename}",
                defaults={'order': order},
            )
            if image.order != order:
                image.order = order
                image.save(update_fields=['order'])

    # Скрываем явно тестовые позиции с пустыми описаниями и изображениями-заглушками.
    Product.objects.filter(
        category=category,
        slug__in=['krasnyj-halat3', 'krasnyj-halat4', 'krasnyj-halat5'],
    ).update(available=False)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_favorite'),
    ]

    operations = [
        migrations.RunPython(seed_puer_products, migrations.RunPython.noop),
    ]
