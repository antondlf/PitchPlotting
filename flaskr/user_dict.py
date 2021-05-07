from flaskr.db import get_db


def is_odd(n):
    if n % 2 == 1:
        return True
    else:
        return False

def get_sentences():

    db = get_db()

    sentences = db.execute(
        'SELECT (id, sent_group, sent_type, sent_id)'
        'FROM chapters'
    ).fetchall()

    sent_dict_list = list()

    # Randomization code
    for sent in sentences:
        id, sent_group, sent_type, sent_id = sent
        sent_dict_list.append({'id': id, 'sent_group': sent_group, 'sent_type': sent_type, 'sent_id': sent_id})

    sent_dict = dict()
    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    for group in group_list:
        sent_dict[group] = [sent for sent in sent_dict_list if sent['sent_group'] == group]

    return sent_dict


def create_user_dict(user_id):

    sentences = get_sentences()
    user_dict = dict()

    if is_odd(user_id):
        user_dict['condition'] = 'a'
    else:
        user_dict['condition'] = 'b'




    return user_dict

def get_user_dict(user_id):

    db = get_db()

    user_data= db.execute(
        'SELECT user_dict FROM userdata WHERE user_id=?',
        (user_id,)
    ).fetchall()

    user_dict = user_data[0]['user_dict']

    return user_dict
