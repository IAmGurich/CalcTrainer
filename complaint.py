import json

def add_complaint(chat_id, complaint):
    try:
        with open('complaints.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        if not data['complaints']:
            data['complaints'].append({chat_id: complaint})
        else:
            data['complaints'] = [{chat_id: complaint}]

    except FileNotFoundError:
        data = {"complaints": []}
        print('Такого файла не существует!')

    with open('complaints.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
