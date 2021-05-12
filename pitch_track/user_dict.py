from flaskr.db import get_db
import random


def is_odd(n):
    if n % 2 == 1:
        return True
    else:
        return False


def sample_remove(x):

    choice = random.choices(x, k=5)
    choice_idx = x.index(choice)
    # Remove choice
    x[choice_idx] = None

    return choice

def get_sentences():

    db = get_db()

    sentences = db.execute(
        'SELECT * FROM chapters'
    ).fetchall()

    print(sentences[0])
    sent_dict_list = list()

    # Randomization code
    for sent in sentences:
        id = sent['id']
        sent_group = sent['sent_group']
        sent_type = sent['sent_type']
        sent_id = sent['sent_id']
        sent_dict_list.append({'id': id, 'sent_group': sent_group, 'sent_type': sent_type, 'sent_id': sent_id})

    print(sent_dict_list)
    sent_dict = dict()
    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    print(group_list)

    for group in group_list:

        sent_dict[group] = dict()

        sent_dict[group]['Q'] = [sent for sent in sent_dict_list if
                               (sent['sent_group'] == group) and (sent['sent_type'] == 'Q')]
        sent_dict[group]['S'] = [sent for sent in sent_dict_list if
                               (sent['sent_group'] == group) and (sent['sent_type'] == 'S')]

    print(sent_dict)
    return sent_dict


def create_user_dict(user_id):

    sentences = get_sentences()



    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    statement_list = list()
    question_list = list()

    for group in sentences.keys():

        statement_list += [sent for sent in sentences[group]['S']]

    for sent in statement_list:

        group, id = (sent['sent_group'], sent['sent_id'])
        gen_id = id[:-3]
        question_list += [question for question in sentences[group]['Q'] if sent['sent_id'][:-3] == gen_id]

    user_dict = dict()

    order_dict = dict()

    if is_odd(user_id):
        user_dict['condition'] = 'a'
    else:
        user_dict['condition'] = 'b'

    # Create dictionary structure
    order_dict['Session 1'] = dict()
    order_dict['Session 2'] = dict()
    order_dict['Session 3'] = dict()
    order_dict['Session 1']['pre_train'] = dict()
    order_dict['Session 2']['pre_train'] = dict()
    order_dict['Session 1']['post_train'] = dict()
    order_dict['Session 2']['post_train'] = dict()
    order_dict['Session 3']['post_train'] = dict()

    # Counter to keep track of order
    i = -1
    # pre_train and post_train dicts
    for group in sentences.keys():

        i += 1

        # First get a statement
        choices = random.choices(sentences[group]['S'], k=5)
        order_dict['Session 1']['pre_train'][i] = choices[0]['sent_id']
        order_dict['Session 1']['post_train'][i] = choices[1]['sent_id']
        order_dict['Session 2']['pre_train'][i] = choices[2]['sent_id']
        order_dict['Session 2']['post_train'][i] = choices[3]['sent_id']
        order_dict['Session 3']['post_train'][i] = choices[4]['sent_id']


        i += 1
        choices = random.choices(sentences[group]['Q'], k=5)
        order_dict['Session 1']['pre_train'][i] = choices[0]['sent_id']
        order_dict['Session 1']['post_train'][i] = choices[1]['sent_id']
        order_dict['Session 2']['pre_train'][i] = choices[2]['sent_id']
        order_dict['Session 2']['post_train'][i] = choices[3]['sent_id']
        order_dict['Session 3']['post_train'][i] = choices[4]['sent_id']


    order_dict['Session 1']['training'] = dict()
    order_dict['Session 2']['training'] = dict()

    for i in range(8):

        group = random.choice(group_list)
        statement = random.choice(sentences[group]['S'])
        print('This is the statement')
        print(statement)
        print()
        for sent in sentences[group]['Q']:
            if sent['sent_id'][:-3] == statement['sent_id'][:-3]:
                question = sent
        print('this is the question')
        print(question)
        print()

        order_dict['Session 1']['training'][i] = statement['sent_id']
        order_dict['Session 1']['training'][i] = question['sent_id']
        order_dict['Session 2']['training'][i] = statement['sent_id']
        order_dict['Session 2']['training'][i] = question['sent_id']

    user_dict['order'] = order_dict

    for session in order_dict.keys():
        session_dict = order_dict[session]
        for trial_type in session_dict.keys():
            orders = session_dict[trial_type]
            for order in orders.keys():
                sent_id = orders[order]
                condition = user_dict['condition']
                print('Order')
                print(
                    order,
                    type(order))
                print('User_id')
                print(
                    user_id,
                    type(user_id))
                print('condition')
                print(
                    condition,
                    type(condition))
                print('session')
                print(
                    session,
                    type(session))
                print('trial_type')
                print(
                    trial_type,
                    type(trial_type))
                print('order')
                print(
                    order,
                    type(order))
                print(sent_id)
                print(
                    sent_id,
                    type(sent_id)
                )
                db = get_db()
                db.execute(
                    'INSERT INTO userdata (user_id, experimental_condition, session_number, trial_type, sent_order, sent_id)'
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (int(user_id), condition, session, trial_type, str(order), sent_id)
                )

def get_current_state(user_id, session, trial_type, order):

    db = get_db()

    condition, sent_id = db.execute(
        'SELECT (condition, sent_id)'
        ' FROM userdata WHERE user_id=?'
        'session=?, trial_type=?, order=?',
        (user_id, session, trial_type, order)
    ).fetchall()[0]

    return condition, sent_id
