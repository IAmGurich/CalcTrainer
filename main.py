import telebot
import random
from complaint import add_complaint
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

token = '8025876405:AAH9pgaZU-447IElBiNM-pwh7bfYoJH6ztU'
bot = telebot.TeleBot(token)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет! 🧠 Я - интерактивный математический тренажёр.\n'
        'Нажми /test для запуска тестирования.'
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        '📌 Список команд:\n'
        '/start - старт\n'
        '/test - начать тест\n'
        '/complaint - пожаловаться на работу бота'
    )

def generate_question(level):
    if level == 'basic':
        a = random.randint(-50, 50)
        b = random.randint(-50, 50)
        znak = random.choice('+-')
        question = f'{a} {znak} {b}'
        answer = eval(f'{a} {znak} {b}')

    elif level == 'medium':
        a = random.randint(-10, 15)
        b = random.randint(-10, 15)
        znak2 = random.choice('+-/')
        if znak2 != '/':
            c = random.randint(-10, 50)
            znak1 = '*'
            question = f'({a} {znak1} {b}) {znak2} {c}'
            answer = eval(f'({a} {znak1} {b}) {znak2} {c}')
        else:
            c = random.choice([-2, 2])
            znak1 = random.choice('+-')
            question = f'({a} {znak1} {b}) {znak2} {c}'
            answer = eval(f'({a} {znak1} {b}) {znak2} {c}')

    else:
        a = random.randint(-20,20)
        b = random.randint(-20, 20)
        d = random.choice([0, 1])
        if d == 1:
            znak2 = random.choice('+-/')
            if znak2 != '/':
                c = random.randint(-10, 50)
                znak1 = '*'
                question = f'({a} {znak1} {b}) {znak2} {c}'
                answer = eval(f'({a} {znak1} {b}) {znak2} {c}')
            else:
                c = random.choice([-2, 2])
                znak1 = random.choice('+-')
                question = f'({a} {znak1} {b}) {znak2} {c}'
                answer = eval(f'({a} {znak1} {b}) {znak2} {c}')
        else:
            c = random.randint(-20, 20)
            znak1 = random.choice('-+*')
            znak2 = random.choice('-+*')
            choice = random.choice([0, 1])
            if choice == 1:
                a = random.randint(2, 20)
                if znak1 != '*':
                    b = random.randint(-50, 50)
                else:
                    b = random.randint(-10, 10)

                question = f'{a}² {znak1} {b} {znak2} {c}'
                answer = eval(f'({a}**2) {znak1} {b} {znak2} {c}')
            else:
                b = random.randint(2, 20)
                if znak1 != '*':
                    a = random.randint(-50, 50)
                else:
                    a = random.randint(-10, 10)

                question = f'{a} {znak1} {b}² {znak2} {c}'
                answer = eval(f'{a} {znak1} ({b}**2) {znak2} {c}')

    return question, answer


def generate_options(correct_answer):
    options = [correct_answer]

    while len(options) < 4:
        fake = correct_answer + random.randint(-10, 10)
        if fake != correct_answer and fake not in options:
            options.append(fake)

    random.shuffle(options)
    return options

@bot.message_handler(commands=['test'])
def quiz(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Базовый')
    markup.add('Средний')
    markup.add('Сложный')

    bot.send_message(
        message.chat.id,
        'Выберите уровень сложности:',
        reply_markup=markup
    )

    bot.register_next_step_handler(message, set_level)


def set_level(message):
    level_map = {
        'Базовый': 'basic',
        'Средний': 'medium',
        'Сложный': 'hard'
    }

    if message.text not in level_map:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, выберите уровень кнопкой.')
        return

    level = level_map[message.text]

    user_data[message.chat.id] = {
        'score': 0,
        'question_count': 0,
        'in_test': True,
        'level': level
    }

    bot.send_message(
        message.chat.id,
        f'Вы выбрали уровень: {message.text}',
        reply_markup=ReplyKeyboardRemove()
    )

    send_question(message.chat.id)


def send_question(chat_id):
    data = user_data[chat_id]

    if data['question_count'] >= 10:
        bot.send_message(
            chat_id,
            f'🎉 Тестирование успешно завершено!\n'
            f'Ваш результат: {data['score']} из 10\n'
            f'Для повторного запуска введите /test',
            reply_markup=ReplyKeyboardRemove()
        )
        data['in_test'] = False
        return

    question_text, correct_answer = generate_question(data['level'])
    options = generate_options(correct_answer)

    data['current_answer'] = str(correct_answer)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(str(option)))

    bot.send_message(
        chat_id,
        f'Вопрос {data['question_count'] + 1}:\n{question_text}',
        reply_markup=markup
    )

@bot.message_handler(commands=['complaint'])
def handle_complaint(message):
    bot.send_message(message.chat.id, 'Введите вашу жалобу:')
    bot.register_next_step_handler(message, save_complaint)


def save_complaint(message):
    chat_id = message.chat.id
    complaint_text = message.text
    add_complaint(chat_id, complaint_text)
    bot.send_message(chat_id, 'Ваша жалоба успешно сохранена!')


@bot.message_handler(func=lambda message: True)
def handle_all(message):
    chat_id = message.chat.id

    if chat_id not in user_data or not user_data[chat_id].get('in_test'):
        bot.send_message(
            chat_id,
            'Вы написали боту не по теме')
        handle_help(message)
        return

    data = user_data[chat_id]

    if message.text == data['current_answer']:
        data['score'] += 1
        bot.send_message(chat_id, '✅ Правильно!')
    else:
        bot.send_message(
            chat_id,
            f'❌ Неправильно! Правильный ответ: {data['current_answer']}'
        )

    data['question_count'] += 1
    send_question(chat_id)

if __name__ == '__main__':
    bot.polling(non_stop=True)
