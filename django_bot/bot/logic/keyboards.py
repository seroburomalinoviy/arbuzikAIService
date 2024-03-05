from telegram import InlineKeyboardButton

check_status = [
    [
        InlineKeyboardButton('Проверить аудио', callback_data='^check_status$')
        ]
]

search_all_voices = [
        InlineKeyboardButton('🔍 Поиск по всем голосам', callback_data='search_all')
    ]

category_menu = [
    InlineKeyboardButton('⏪ Вернуться назад', callback_data='category_menu')
]

check_subscription = [
                        [
                        InlineKeyboardButton("Подписаться", url='https://t.me/arbuzik_smiley_group'),
                        InlineKeyboardButton('Проверить статус подписки', callback_data='subscription')
                    ]
                ]
is_subscribed = [
                    [
                        InlineKeyboardButton("⚡ Подписки", callback_data='step_1'),
                        InlineKeyboardButton("⏩ Перейти к выбору голосов", callback_data='category_menu'),
                    ]
                ]
