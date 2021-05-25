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
    """Get the sentences from the database and return a dictionary with
    all the sentence dictionaries as well as a list of all the sentence
    dictionaries.
    """
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
    return sent_dict, sent_dict_list

def get_pair_tuples(sent_dict_list):
    """use the list of dictionaries to get a list of Question-Statement pairs"""

    statement_list = list()
    question_list = list()
    for sent in sent_dict_list:
        if sent['sent_type'] == 'S':
            statement_list.append(sent)
        elif sent['sent_type'] == 'Q':
            question_list.append(sent)

    sentence_pairs = list()
    for statement in statement_list:
        for question in question_list:
            if statement['sent_id'][:-3] == question['sent_id'][:-3]:
                sentence_pairs.append((statement, question))
    return sentence_pairs

def get_user_list(order_dict):

    order_list = list()

    sessions = ['Session 1', 'Session 2', 'Session 3']
    trial_type = ['pre_train', 'training', 'post_train']

    for session in sessions:

        current_sesh = order_dict[session]
        for trial in trial_type:
            current_trial = current_sesh[trial]
            for order in current_trial.keys():

                order_list.append(current_trial[order])

    return order_list

def create_user_dict(user_id):

    # Get the sentence dictionary and the list of sentence dictionaries.
    sentences, sent_dict_list = get_sentences()

    # Get the sentence pair list
    sentence_pairs = get_pair_tuples(sent_dict_list)

    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    statement_list = list()
    question_list = list()

    for group in sentences.keys():

        statement_list += [sent for sent in sentences[group]['S']]

    for sent in statement_list:

        group, id = (sent['sent_group'], sent['sent_id'])
        gen_id = id[:-3]
        question_list += [question for question in sentences[group]['Q'] if sent['sent_id'][:-3] == gen_id]
    # Initialize state dictionary
    user_dict = dict()

    # Initialie order dictionary
    order_dict = dict()

    # Give the state dictionary an experimental condition
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
    order_dict['Session 3']['pre_train'] = dict()

    # Counter to keep track of order
    i = -1
    # pre_train and post_train dicts
    for group in sentences.keys():


        # First get 5 statements for this group and distribute them
        # to all of the non-training conditions.
        choices = random.choices(sentences[group]['S'], k=5)
        order_dict['Session 1']['pre_train'][i] = choices[0]['sent_id']
        order_dict['Session 1']['post_train'][i] = choices[1]['sent_id']
        order_dict['Session 2']['pre_train'][i] = choices[2]['sent_id']
        order_dict['Session 2']['post_train'][i] = choices[3]['sent_id']
        order_dict['Session 3']['pre_train'][i] = choices[4]['sent_id']

        # add 1 to i for question
        i += 1
        # Get 5 statements and do the same as above
        choices = random.choices(sentences[group]['Q'], k=5)
        order_dict['Session 1']['pre_train'][i] = choices[0]['sent_id']
        order_dict['Session 1']['post_train'][i] = choices[1]['sent_id']
        order_dict['Session 2']['pre_train'][i] = choices[2]['sent_id']
        order_dict['Session 2']['post_train'][i] = choices[3]['sent_id']
        order_dict['Session 3']['pre_train'][i] = choices[4]['sent_id']
        # Add 1 to i for next iter
        i += 1

    # Initialize the dictionary for training
    order_dict['Session 1']['training'] = dict()
    order_dict['Session 2']['training'] = dict()


    # For the training order we want to do it in Question-statement pairs
    # That we can pick from a specific group.
    # We need 8 sentence pairs that repeat once.

    # Duplicate group list so that we can iterate 8 times.
    group_list_iter = group_list*2
    for n in range(8):

        # Get the group
        group = group_list_iter[n]
        # Pick pair for session 1
        sent_pair1 = random.choice(sentence_pairs)
        # Make sure its from the right group
        while sent_pair1[0]['sent_group'] != group:
            sent_pair1 = random.choice(sentence_pairs)

        # Pick pair for session 2
        sent_pair2 = random.choice(sentence_pairs)
        # Make sure its from the right group
        while sent_pair2[0]['sent_group'] != group:
            sent_pair2 = random.choice(sentence_pairs)

        # We want the index 'i' here to be relative to what numbered pair
        # we are at (e.g. i should be 4 for our second pair of sentences
        # because it will range from the 5th to the 8th spot in the order).
        i = n*4
        for rep in range(2):

            # i is n*4 in the first iteration and (n*4)+2 in the second iteration
            order_dict['Session 1']['training'][i] = sent_pair1[rep]['sent_id']
            order_dict['Session 2']['training'][i] = sent_pair2[rep]['sent_id']
            i += 1
            order_dict['Session 1']['training'][i] = sent_pair1[rep]['sent_id']
            order_dict['Session 2']['training'][i] = sent_pair2[rep]['sent_id']
            i += 1

    # input the order_dict into user_dict
    user_dict['order'] = order_dict

    print(user_dict)

    # serialize the user_dictionary using pickle so that it can be
    # input into the database.
    pdata = pickle.dumps(user_dict)

    db = get_db()
    db.execute(
        'INSERT INTO userdata (user_id, user_dict) VALUES (?, ?)',
        (user_id, pdata)
    )
    db.commit()

    return get_user_list(order_dict)


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
        ).fetchall()
        if len(user_dict_pickle) == 0:
            error = 'Error, user not properly registered. Contact the support email to get a new account.'
            return error
        else:
            self.user_dict = pickle.load(BytesIO(user_dict_pickle[0]['user_dict']))

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
