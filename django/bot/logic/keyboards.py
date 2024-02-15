from telegram import InlineKeyboardButton

categories = [
    [
        InlineKeyboardButton('1. Аниме', callback_data='category_1'),
        InlineKeyboardButton('9. Ютуберы', callback_data='category_9'),
    ],
    [
        InlineKeyboardButton('2. Фильмы', callback_data='category_2'),
        InlineKeyboardButton('11. BTS(KR)', callback_data='category_11'),
    ],
    [
        InlineKeyboardButton('3. Мультфильмы', callback_data='category_3'),
        InlineKeyboardButton('10. Тиктокеры', callback_data='category_10'),
    ],
    [
        InlineKeyboardButton('4. Сериалы', callback_data='category_4'),
        InlineKeyboardButton('12. Актеры дубляжа и дикторы', callback_data='category_12'),
    ],
    [
        InlineKeyboardButton('5. Игры', callback_data='category_5'),
        InlineKeyboardButton('13. Известные личности', callback_data='category_13'),
    ],
    [
        InlineKeyboardButton('6. Певцы', callback_data='category_6'),
        InlineKeyboardButton('14. Бытовые голоса', callback_data='category_14'),
    ],
    [
        InlineKeyboardButton('7. Мемы', callback_data='category_7'),
        InlineKeyboardButton('15. VIP голоса', callback_data='category_15'),
    ],
    [
        InlineKeyboardButton('16. Стриммеры', callback_data='category_16')
    ]
]
subscription = [
    [
    InlineKeyboardButton("Подписаться", url='https://t.me/arbuzik_smiley_group'),
    InlineKeyboardButton('Проверить статус подписки', callback_data='sub_0')
]
]