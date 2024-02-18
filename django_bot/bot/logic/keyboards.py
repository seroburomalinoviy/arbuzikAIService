from telegram import InlineKeyboardButton

search_all_voices = [
        InlineKeyboardButton('🔍 Поиск по всем голосам', callback_data='search_all')
    ]

back_to_category = [
    InlineKeyboardButton('⏪ Вернуться назад', callback_data='back_category')
]

check_subscription = [
                        [
                        InlineKeyboardButton("Подписаться", url='https://t.me/arbuzik_smiley_group'),
                        InlineKeyboardButton('Проверить статус подписки', callback_data='step_0')
                    ]
                ]
is_subscribed = [
                    [
                        InlineKeyboardButton("⚡ Подписки", callback_data='step_1'),
                        InlineKeyboardButton("⏩ Перейти к выбору голосов", callback_data='step_2'),
                    ]
                ]

