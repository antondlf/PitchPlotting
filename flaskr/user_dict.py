from flaskr.db import get_db
import random


def is_odd(n):
    if n % 2 == 1:
        return True
    else:
        return False


def sample_remove(x):

    choice = random.choice(x)
    choice_idx = x.index(choice)
    # Remove choice
    x[choice_idx] = None

    return choice

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
        Q = 'Q'
        S = 'S'
        sent_dict[group][Q] = [sent for sent in sent_dict_list if
                               sent['sent_group'] == group and sent['sent_type'] == Q]
        sent_dict[group][S] = [sent for sent in sent_dict_list if
                               sent['sent_group'] == group and sent['sent_type'] == S]

    return sent_dict


def create_user_dict(user_id):

    #sentences = get_sentences()



    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    statement_list = list()
    question_list = list()

    for group in sentences.keys():

        statement_list += [sent for sent in sentences[group]['S']]

    for sent in statement_list:

        group, id = (sent['sent_group'], sent['sent_id'])
        question_list.append(question for question in sentences[group]['Q'] if sent['sent_id'] == id)

    user_dict = dict()

    order_dict = dict()

    if is_odd(user_id):
        user_dict['condition'] = 'a'
    else:
        user_dict['condition'] = 'b'

    # Counter to keep track of order
    i = -1
    # pre_train and post_train dicts
    for group in sentences.keys():

        i += 1
        # First get a statement
        choice = sample_remove(sentences[group]['S'])
        order_dict['Session 1']['pre_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['S'])
        order_dict['Session 1']['post_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['S'])
        order_dict['Session 2']['pre_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['S'])
        order_dict['Session 2']['post_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['S'])
        order_dict['Session 3']['post_train'][i] = choice['sent_id']


        i += 1
        choice = sample_remove(sentences[group]['Q'])
        order_dict['Session 1']['pre_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['Q'])
        order_dict['Session 1']['post_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['Q'])
        order_dict['Session 2']['pre_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['Q'])
        order_dict['Session 2']['post_train'][i] = choice['sent_id']
        choice = sample_remove(sentences[group]['Q'])
        order_dict['Session 3']['post_train'][i] = choice['sent_id']



    for i in range(8):

        group = random.choice(group_list)
        statement = random.choice(sentences[group]['S']),
        question = (
            sent for sent in sentences[group]['Q'] if\
            sent['sent_id'] == statement['sent_id'])

        order_dict['Session 1']['training'][i] = statement
        order_dict['Session 1']['training'][i] = question
        order_dict['Session 2']['training'][i] = statement
        order_dict['Session 2']['training'][i] = question

    user_dict['order'] = order_dict

    return user_dict

def get_user_dict(user_id):

    db = get_db()

    user_data= db.execute(
        'SELECT user_dict FROM userdata WHERE user_id=?',
        (user_id,)
    ).fetchall()

    user_dict = user_data[0]['user_dict']

    return user_dict
