from telegram import InlineKeyboardButton

back_to_category = [
    InlineKeyboardButton('⏪ Вернуться назад', callback_data='category_back')
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

