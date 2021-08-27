from flaskr.db import get_db
from flask import g
import pickle
import random
from io import BytesIO


sent_dict_list = [{'id': 1, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Mario_vola(Q)'}, {'id': 2, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Mario_vola(S)'}, {'id': 3, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Delia_guida(Q)'}, {'id': 4, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Delia_guida(S)'}, {'id': 5, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Livia_dorme(Q)'}, {'id': 6, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Livia_dorme(S)'}, {'id': 7, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Barbara_vive(Q)'}, {'id': 8, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Barbara_vive(S)'}, {'id': 9, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Angelo_giunge(Q)'}, {'id': 10, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Angelo_giunge(S)'}, {'id': 11, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Debora_gira(Q)'}, {'id': 12, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Debora_gira(S)'}, {'id': 13, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Daria_brinda(Q)'}, {'id': 14, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Daria_brinda(S)'}, {'id': 15, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Adriana_beve(Q)'}, {'id': 16, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Adriana_beve(S)'}, {'id': 17, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Giuliana_mangia(Q)'}, {'id': 18, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Giuliana_mangia(S)'}, {'id': 19, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Damiano_morde(Q)'}, {'id': 20, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Damiano_morde(S)'}, {'id': 21, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Amedeo_lava(Q)'}, {'id': 22, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Amedeo_lava(S)'}, {'id': 23, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Edoardo_vede(Q)'}, {'id': 24, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Edoardo_vede(S)'}, {'id': 25, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Loredana_vende(Q)'}, {'id': 26, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Loredana_vende(S)'}, {'id': 27, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Gabriele_ama(Q)'}, {'id': 28, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Gabriele_ama(S)'}, {'id': 29, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_lago(Q)'}, {'id': 30, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_lago(S)'}, {'id': 31, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_brodo(Q)'}, {'id': 32, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_brodo(S)'}, {'id': 33, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'La_legna(Q)'}, {'id': 34, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'La_legna(S)'}, {'id': 35, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'La_rana(Q)'}, {'id': 36, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'La_rana(S)'}, {'id': 37, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_ladro(Q)'}, {'id': 38, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_ladro(S)'}, {'id': 39, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'La_via(Q)'}, {'id': 40, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'La_via(S)'}, {'id': 41, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_nome(Q)'}, {'id': 42, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_nome(S)'}, {'id': 43, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'Il_giornale(Q)'}, {'id': 44, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'Il_giornale(S)'}, {'id': 45, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_balena(Q)'}, {'id': 46, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_balena(S)'}, {'id': 47, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'Il_melone(Q)'}, {'id': 48, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'Il_melone(S)'}, {'id': 49, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_bambina(Q)'}, {'id': 50, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_bambina(S)'}, {'id': 51, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_ragione(Q)'}, {'id': 52, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_ragione(S)'}, {'id': 53, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'Il_rumore(Q)'}, {'id': 54, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'Il_rumore(S)'}, {'id': 55, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_bevanda(Q)'}, {'id': 56, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_bevanda(S)'}, {'id': 57, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Anna_lavora(Q)'}, {'id': 58, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Anna_lavora(S)'}, {'id': 59, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Emilia_arriva(Q)'}, {'id': 60, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Emilia_arriva(S)'}, {'id': 61, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Bernardo_viene(Q)'}, {'id': 62, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Bernardo_viene(S)'}, {'id': 63, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Luigi_odia(Q)'}, {'id': 64, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Luigi_odia(S)'}, {'id': 65, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Elena_guarda(Q)'}, {'id': 66, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Elena_guarda(S)'}, {'id': 67, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Giovanni_ruba(Q)'}, {'id': 68, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Giovanni_ruba(S)'}, {'id': 69, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Irene_disegna(Q)'}, {'id': 70, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Irene_disegna(S)'}]


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
    sent_dict_list = [{'id': 1, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Mario_vola(Q)'}, {'id': 2, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Mario_vola(S)'}, {'id': 3, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Delia_guida(Q)'}, {'id': 4, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Delia_guida(S)'}, {'id': 5, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Livia_dorme(Q)'}, {'id': 6, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Livia_dorme(S)'}, {'id': 7, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Barbara_vive(Q)'}, {'id': 8, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Barbara_vive(S)'}, {'id': 9, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Angelo_giunge(Q)'}, {'id': 10, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Angelo_giunge(S)'}, {'id': 11, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Debora_gira(Q)'}, {'id': 12, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Debora_gira(S)'}, {'id': 13, 'sent_group': 'set_1', 'sent_type': 'Q', 'sent_id': 'Daria_brinda(Q)'}, {'id': 14, 'sent_group': 'set_1', 'sent_type': 'S', 'sent_id': 'Daria_brinda(S)'}, {'id': 15, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Adriana_beve(Q)'}, {'id': 16, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Adriana_beve(S)'}, {'id': 17, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Giuliana_mangia(Q)'}, {'id': 18, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Giuliana_mangia(S)'}, {'id': 19, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Damiano_morde(Q)'}, {'id': 20, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Damiano_morde(S)'}, {'id': 21, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Amedeo_lava(Q)'}, {'id': 22, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Amedeo_lava(S)'}, {'id': 23, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Edoardo_vede(Q)'}, {'id': 24, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Edoardo_vede(S)'}, {'id': 25, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Loredana_vende(Q)'}, {'id': 26, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Loredana_vende(S)'}, {'id': 27, 'sent_group': 'set_2', 'sent_type': 'Q', 'sent_id': 'Gabriele_ama(Q)'}, {'id': 28, 'sent_group': 'set_2', 'sent_type': 'S', 'sent_id': 'Gabriele_ama(S)'}, {'id': 29, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_lago(Q)'}, {'id': 30, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_lago(S)'}, {'id': 31, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_brodo(Q)'}, {'id': 32, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_brodo(S)'}, {'id': 33, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'La_legna(Q)'}, {'id': 34, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'La_legna(S)'}, {'id': 35, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'La_rana(Q)'}, {'id': 36, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'La_rana(S)'}, {'id': 37, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_ladro(Q)'}, {'id': 38, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_ladro(S)'}, {'id': 39, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'La_via(Q)'}, {'id': 40, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'La_via(S)'}, {'id': 41, 'sent_group': 'set_3', 'sent_type': 'Q', 'sent_id': 'Il_nome(Q)'}, {'id': 42, 'sent_group': 'set_3', 'sent_type': 'S', 'sent_id': 'Il_nome(S)'}, {'id': 43, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'Il_giornale(Q)'}, {'id': 44, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'Il_giornale(S)'}, {'id': 45, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_balena(Q)'}, {'id': 46, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_balena(S)'}, {'id': 47, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'Il_melone(Q)'}, {'id': 48, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'Il_melone(S)'}, {'id': 49, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_bambina(Q)'}, {'id': 50, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_bambina(S)'}, {'id': 51, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_ragione(Q)'}, {'id': 52, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_ragione(S)'}, {'id': 53, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'Il_rumore(Q)'}, {'id': 54, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'Il_rumore(S)'}, {'id': 55, 'sent_group': 'set_4', 'sent_type': 'Q', 'sent_id': 'La_bevanda(Q)'}, {'id': 56, 'sent_group': 'set_4', 'sent_type': 'S', 'sent_id': 'La_bevanda(S)'}, {'id': 57, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Anna_lavora(Q)'}, {'id': 58, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Anna_lavora(S)'}, {'id': 59, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Emilia_arriva(Q)'}, {'id': 60, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Emilia_arriva(S)'}, {'id': 61, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Bernardo_viene(Q)'}, {'id': 62, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Bernardo_viene(S)'}, {'id': 63, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Luigi_odia(Q)'}, {'id': 64, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Luigi_odia(S)'}, {'id': 65, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Elena_guarda(Q)'}, {'id': 66, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Elena_guarda(S)'}, {'id': 67, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Giovanni_ruba(Q)'}, {'id': 68, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Giovanni_ruba(S)'}, {'id': 69, 'sent_group': 'unmatched', 'sent_type': 'Q', 'sent_id': 'Irene_disegna(Q)'}, {'id': 70, 'sent_group': 'unmatched', 'sent_type': 'S', 'sent_id': 'Irene_disegna(S)'}]

    #print(sent_dict_list)
    sent_dict = dict()
    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    #print(group_list)

    for group in group_list:
        sent_dict[group] = list()

    for sent in sent_dict_list:

        sent_id = sent['sent_id'][:-3]
        group = sent['sent_group']

        if sent_id not in sent_dict[group]:
            sent_dict[group].append(sent_id)

    return sent_dict


def get_user_list(order_dict):

    order_list = str()

    sessions = ['Session 1', 'Session 2', 'Session 3']
    trial_type = ['pre_train', 'training', 'post_train']

    for session in sessions:

        current_sesh = order_dict[session]
        order_list += session + '\n\n\n'
        for trial in current_sesh.keys():
            current_trial = current_sesh[trial]
            order_list += trial + ':' + '\n\n'
            for order in current_trial.keys():

                order_list += current_trial[order] + '\n'
            order_list += '\n'

        order_list += '\n\n\n'

    return order_list


def create_user_dict(user_id, group=None, db=None):

    # Get the sentence dictionary and the list of sentence dictionaries.
    sentences = get_sentences()

    group_list = ['set_1', 'set_2', 'set_3', 'set_4', 'unmatched']

    statement_list = list()
    question_list = list()

    for group in group_list:
        # print('pre_shuffle')
        # print(sentences[group])
        random.shuffle(sentences[group])
        # print('after_shuffle')
        # print(sentences[group])
        # print()

    # Initialize state dictionary
    user_dict = dict()

    # Initialie order dictionary
    order_dict = dict()

    # Give the state dictionary an experimental condition
    if group:
        user_dict['condition'] = group
    else:
        user_dict['condition'] = 'a'

    # Create dictionary structure
    order_dict['Session 1'] = dict()
    order_dict['Session 2'] = dict()
    order_dict['Session 3'] = dict()
    order_dict['Session 1']['pre_train'] = dict()
    order_dict['Session 2']['pre_train'] = dict()
    order_dict['Session 1']['training'] = dict()
    order_dict['Session 2']['training'] = dict()
    order_dict['Session 1']['post_train'] = dict()
    order_dict['Session 2']['post_train'] = dict()
    order_dict['Session 3']['pre_train'] = dict()

    # Counter to keep track of order for pre_train and post_train
    i = 0

    # Another couter to keep track of training order
    n = 0
    # pre_train and post_train dicts
    for group in group_list[:-1]:

        print(n, sentences[group][1], group)
        print()
        order_dict['Session 1']['pre_train'][i] = sentences[group][0] + '(S)'
        order_dict['Session 1']['training'][n] = sentences[group][1] + '(S)'
        order_dict['Session 1']['post_train'][i] = sentences[group][2] + '(S)'
        order_dict['Session 2']['pre_train'][i] = sentences[group][3] + '(S)'
        order_dict['Session 2']['training'][n] = sentences[group][4] + '(S)'
        order_dict['Session 2']['post_train'][i] = sentences[group][5] + '(S)'
        order_dict['Session 3']['pre_train'][i] = sentences[group][6] + '(S)'

        # add 1 to i for question
        i += 1

        # add 1 to n for second statement
        n += 1
        # Get 5 statements and do the same as above
        order_dict['Session 1']['pre_train'][i] = sentences[group][0] + '(Q)'
        order_dict['Session 1']['training'][n] = sentences[group][1] + '(S)'
        order_dict['Session 1']['post_train'][i] = sentences[group][2] + '(Q)'
        order_dict['Session 2']['pre_train'][i] = sentences[group][3] + '(Q)'
        order_dict['Session 2']['training'][n] = sentences[group][4] + '(S)'
        order_dict['Session 2']['post_train'][i] = sentences[group][5] + '(Q)'
        order_dict['Session 3']['pre_train'][i] = sentences[group][6] + '(Q)'
        # Add 1 to i for next iter
        i += 1
        # Add two questions
        n += 1
        for x in range(2):

            order_dict['Session 1']['training'][n] = sentences[group][1] + '(Q)'
            order_dict['Session 2']['training'][n] = sentences[group][4] + '(Q)'
            # for next iter add 1:
            n += 1

    # We start unmatched at 15
    n = len(order_dict['Session 1']['training'])-1
    print('unmatched:')
    for i in range(4):
        print(n, sentences['unmatched'][i])
        print()
        order_dict['Session 1']['training'][n] = sentences['unmatched'][i] + '(S)'
        order_dict['Session 2']['training'][n] = sentences['unmatched'][-(i+1)] + '(S)'

        n += 1

        order_dict['Session 1']['training'][n] = sentences['unmatched'][i] + '(S)'
        order_dict['Session 2']['training'][n] = sentences['unmatched'][-(i+1)] + '(S)'

        n += 1
        order_dict['Session 1']['training'][n] = sentences['unmatched'][i] + '(Q)'
        order_dict['Session 2']['training'][n] = sentences['unmatched'][-(i+1)] + '(Q)'

        n += 1

        order_dict['Session 1']['training'][n] = sentences['unmatched'][i] + '(Q)'
        order_dict['Session 2']['training'][n] = sentences['unmatched'][-(i+1)] + '(Q)'

        n += 1

    print(len(order_dict['Session 1']['training']))

    # input the order_dict into user_dict
    user_dict['order'] = order_dict

    #print(user_dict)

    # serialize the user_dictionary using pickle so that it can be
    # input into the database.
    pdata = pickle.dumps(user_dict)

    if db == None:
        db = get_db()

    db.execute(
        'INSERT INTO userdata (user_id, user_dict) VALUES (?, ?)',
        (user_id, pdata)
    )
    db.commit()

    return user_dict

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

    def get_trial_length(self, session, trial_type):
        orders = self.get_current_order(session, trial_type)
        order_list = list(orders.keys())
        last_order = order_list[-1]
        return int(last_order)


# if __name__ == '__main__':
#     #with open('/users/anton/desktop/example_orders.txt', 'w') as in_file:
#     # for i in range(1):
#     user_id = random.randint(0,100)
#     dictionary = user_state(user_id)
#     print(dictionary.get_trial_length('Session 1', 'pre_train'))
#     print(dictionary.get_trial_length('Session 1', 'training'))
#     print(dictionary.get_trial_length('Session 1', 'post_train'))