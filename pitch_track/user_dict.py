from flaskr.db import get_db
from flask import g
import pickle
import random
from io import BytesIO


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

    i = 0
    for n in range(8):

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
        for rep in range(2):

            # i+rep = i in first iter, i+1 in second iter
            # rep=0 and i=0 then i+rep = 0, rep=1 and i=2 then i+rep=3
            # This scales as i grows
            order_dict['Session 1']['training'][i+rep] = statement['sent_id']
            order_dict['Session 2']['training'][i+rep] = statement['sent_id']
            i += 1
            # i = 1, i+rep = i in first iter i+1 in second iter
            # i+rep =
            order_dict['Session 1']['training'][i+rep] = question['sent_id']
            order_dict['Session 2']['training'][i+rep] = question['sent_id']
            i += 1
            # i = 2

    user_dict['order'] = order_dict

    print(user_dict)

    pdata = pickle.dumps(user_dict)

    db = get_db()
    db.execute(
        'INSERT INTO userdata (user_id, user_dict) VALUES (?, ?)',
        (user_id, pdata)
    )
    db.commit()


    # for session in order_dict.keys():
    #     session_dict = order_dict[session]
    #     for trial_type in session_dict.keys():
    #         orders = session_dict[trial_type]
    #         for order in orders.keys():
    #             sent_id = orders[order]
    #             condition = user_dict['condition']
    #
    #             db = get_db()
    #             db.execute(
    #                 'INSERT INTO userdata (user_id, experimental_condition, session_number, trial_type, sent_order, sent_id)'
    #                 'VALUES (?, ?, ?, ?, ?, ?)',
    #                 (int(user_id), condition, session, trial_type, str(order), sent_id)
    #             )
    # db.commit()

class user_state:

    def __init__(self, user_id):
        db = get_db()
        user_dict_pickle = db.execute(
            'SELECT user_dict FROM userdata WHERE user_id=?',
            (user_id,)
        ).fetchall()[0]['user_dict']
        self.user_dict = pickle.load(BytesIO(user_dict_pickle))

    def get_condition(self):
        return self.user_dict['condition']

    def get_session_dict(self, session):

        order_dict = self.user_dict['order']

        return order_dict[session]

    def get_current_order(self, session, trial_type):

        session_dict = self.get_session_dict(session)
        return session_dict[trial_type]

    def get_current_state(self, session, trial_type, order):

        current_order_dict = self.get_current_order(session, trial_type)
        current_sent_id = current_order_dict[int(order)]
        return current_sent_id
