import pandas as pd
import numpy as np
import random
from random import shuffle
import sqlite3
import os


"""

Constraints:

    Each trial must be heard by 5 raters
    
    A single rater can only be exposed to one sentence/speaker pair
    

Key conditions:

    For every pair, 5 learners must be assigned
    
    (avoid the same speaker appearing consecutively?)
    
Steps for creating trials:

1. Get number of total recordings to show

2. Get the number of total speakers in the experiment
    
    8 pairs per speaker per comparison-condition
        Some speakers may have less
        What to do when they have less?
            Do manual check here and ask Catherine
    
    Compute number of ns raters necessary/trials necessary

3. Get a list of all stimuli pairs

4. Get a list of all pairs grouped by set.

6. Get a list of all raters

7. Multiply the length of the stimuli pair list by concurrency (5).

8. Generate a list of raters that is equal to the length given in 7.
    
    sub 1. divide the length in 7 by the number of raters (remainder rounds up)
    sub 2. Iterate over the result of sub 1.
        iter 1. randomize the list of raters
        iter 2. append it to the master list for output   

5. Iter over len of list of each group of stimuli for user (from step 4).
    
    1. Select the slice of 2 (n_comparison_condtions*concurrency)
     corresponding to the current iteration
        (something like rater_list[start_slice*i:end_slice*i] where 
        end_slice is checked to be no more than the total length of the list)
    2. Give first 5 S/comparison_1 second 5 Q/comparison_1, Next 5 S/comparison_2...
    

"""


leftover_recs = list()

def check_items_match(item1, item2):

    if item1 == item2:

        return True

    else:

        return False


def get_recordings(path_to_metadata):
    """From metadata extracts all recordings for a given comparison trial

    """
    comparison_dict = {
        'condition_1': {'pre': 'Session 1', 'post': 'Session 1'},
        'condition_2': {'pre': 'Session 1', 'post': 'Session 2'},
        'condition_3': {'pre': 'Session 1', 'post': 'Session 3'}
    }

    # A counter to gather how many pairs of stimuli there are in total
    pair_len = 0

    trial_order_dict = dict()

    data = pd.read_csv(path_to_metadata)

    for user in data.user_id.unique():

        user_dict = dict()

        user_data = data.loc[data['user_id'] == user]

        for cond in comparison_dict.keys():

            cond_dict = dict()

            pre_data = user_data.loc[(user_data['session_number'] == comparison_dict[cond]['pre']) &
                                     (user_data['trial_type'] == 'pre_train')]

            if comparison_dict[cond]['post'] == 'Session 3':

                post_data = user_data.loc[(user_data['session_number'] == comparison_dict[cond]['post']) &
                                          (user_data['trial_type'] == 'pre_train')]

            else:
                post_data = user_data.loc[(user_data['session_number'] == comparison_dict[cond]['post']) &
                                          (user_data['trial_type'] == 'post_train')]

            for trial in pre_data.iterrows():

                group = trial[1]['sent_group']
                sent_type = trial[1]['sent_type']

                trial_id_pre = trial[1]['trial_id']

                trial_id_post = post_data.loc[(post_data['sent_group'] == group) &
                                              (post_data['sent_type'] == sent_type)]['trial_id']

                if type(trial_id_post) != str:
                    # print('trial for user', user, 'and group', group, 'and sent_type', sent_type, 'has more than one file.')

                    trial_id_post = post_data.loc[(post_data['sent_group'] == group) &
                                                  (post_data['sent_type'] == sent_type)]['trial_id']
                # else:
                # print('trial for user', user, 'and group', group, 'and sent_type', sent_type, 'does not have than one file.')
                # print()

                cond_dict[group + sent_type] = (trial_id_pre, trial_id_post)
                pair_len += 1

            user_dict[cond] = cond_dict

        trial_order_dict[user] = user_dict

        return trial_order_dict, pair_len


def pairs2list(data):
    """Function takes dataframe of recordings and returns
    a list of tuples that contain both trial_ids to evaluate
    and a metadata set for later comparison with apportioned
    participants."""


    comparison_dict = {
        'condition_1': {'pre': 'Session 1', 'post': 'Session 1'},
        #'condition_2': {'pre': 'Session 1', 'post': 'Session 2'},
        'condition_3': {'pre': 'Session 1', 'post': 'Session 3'}
    }


    trial_order_list = list()

    for user in data.user_id.unique():

        # user_dict = dict()

        user_data = data.loc[data['user_id'] == user]

        for cond in comparison_dict.keys():

            # cond_dict = dict()

            pre_data = user_data.loc[(user_data['session_number'] == comparison_dict[cond]['pre']) &
                                     (user_data['trial_type'] == 'pre_train')]

            if comparison_dict[cond]['post'] == 'Session 3':

                post_data = user_data.loc[(user_data['session_number'] == comparison_dict[cond]['post']) &
                                          (user_data['trial_type'] == 'pre_train')]

            else:
                post_data = user_data.loc[(user_data['session_number'] == comparison_dict[cond]['post']) &
                                          (user_data['trial_type'] == 'post_train')]

            for trial in pre_data.iterrows():

                group = trial[1]['sent_group']
                sent_type = trial[1]['sent_type']

                trial_id_pre = trial[1]['trial_id']

                #print(trial_id_pre)
                trial_id_post = post_data.loc[(post_data['sent_group'] == group) &
                                              (post_data['sent_type'] == sent_type)]['trial_id']

                if len(trial_id_post) == 0:
                    #print(trial_id_post)
                    break


                elif type(trial_id_post) != str:
                    # print('trial for user', user, 'and group', group, 'and sent_type', sent_type, 'has more than one file.')

                    trial_id_post = post_data.loc[(post_data['sent_group'] == group) &
                                                  (post_data['sent_type'] == sent_type)].iloc[0]['trial_id']
                    #print(trial_id_post)
                # else:
                # print('trial for user', user, 'and group', group, 'and sent_type', sent_type, 'does not have than one file.')
                # print()

                trial_order_list.append((trial_id_pre, trial_id_post, sent_type, (user, group)))
                continue
    print(len(trial_order_list))
    return trial_order_list


def pairs2rater(rater_id, trial_list, trial_len):
    """Returns a list of stimuli given to a particular rater
    without breaking constraints. Takes the list of trials and
    the amount of trials each rater gets."""

    conditions_banned = set()

    rater_list_Q = list()
    rater_list_S = list()

    # Randomization step 1
    shuffle(trial_list)

    # To make sure that half are statements and half are questions
    # We initialize an indicator variable.
    current_sent_type = 'S'

    for i in range(trial_len):

        # This function gets the last item and removes it from the
        # list.
        item = trial_list.pop()

        # TO make sure Statements and Questions alternate,
        # reinsert the random item selected to the beginning
        # of the list until the current item type is present
        while item[-2] != current_sent_type:

            trial_list.insert(0, item)
            item = trial_list.pop()

        #print(item[-1])
        #print(conditions_banned)

        if conditions_banned.intersection({item[-1]}) == set():

            conditions_banned.add(item[-1])
            if item[-2] == 'Q':
                rater_list_Q.append(item[:3])
                current_sent_type = 'S'
            elif item[-2] == 'S':
                rater_list_S.append(item[:3])
                current_sent_type = 'Q'

            else:
                print('function breaks')

            if item in leftover_recs:
                leftover_recs.remove(item)

        elif conditions_banned.intersection({item[-1]}) != set():

            leftover_recs.append(item)

            #print(conditions_banned.intersection(item[-1]), conditions_banned, item[-1])
            #print('current user is banned from this user/group combination')
            #print()

            trial_list.insert(0, item)
    print(rater_id, len(trial_list), len(leftover_recs))
    return rater_list_Q, rater_list_S, trial_list


def pairs2data_dict(rater, rater_id, current_pair, trial_order, data):

    #print(current_pair)
    pre_recording = data.loc[data['trial_id'] == current_pair[0]].sample(1)
    post_recording = data.loc[data['trial_id'] == current_pair[1]].sample(1)

    #pre_recording = pre_recording_data
    #post_recording = post_recording_data

    # If 'post_train' or 'training' something is wrong
    #print('Before the check')
    #print(type(pre_recording))
    #print(pre_recording['trial_type'].item())
    #print()
    if pre_recording['trial_type'].item() != 'pre_train':

        print('error! wrong order in tuple')
        return None

    # If last condition passes but this is "Session 3" something is wrong
    elif pre_recording['session_number'].item() != 'Session 3':

        sanity_check_tup = (check_items_match(pre_recording['user_id'].item(), post_recording['user_id'].item()),
                            check_items_match(pre_recording['sent_type'].item(), post_recording['sent_type'].item()),
                            check_items_match(pre_recording['sent_group'].item(), post_recording['sent_group'].item())
                            )

        if all(sanity_check_tup):

            pair_dict = {
                    'username': 'rater_'+str(rater_id),
                    'trial': trial_order,
                    'learner_id': pre_recording['user_id'].item(),
                    'sent_typ': pre_recording['sent_type'].item(),
                    'sent_group':pre_recording['sent_group'].item(),

                    'pre_recording_id': pre_recording['trial_id'].item(),
                    'pre_recording_sent': pre_recording['sent_id'].item(),
                    'post_recording_id': post_recording['trial_id'].item(),
                    'post_recording_sent': post_recording['sent_id'].item(),
                    'display_order': random.choice([0,1])
            }

            return pair_dict

        else:

            raise ValueError('Pre and post recording do not match')

    else:

        print('error! wrong order in tuple')
        return None


def apportion_pairs(num_raters, trial_list, data, output_path, starting_id, concurrency=5, block_len=20):

    all_trials = trial_list*concurrency

    trial_len = len(all_trials)//num_raters

    trials_dict_list = list()

    for rater in range(num_raters):

        rater_list_Q, rater_list_S, all_trials = pairs2rater(rater, all_trials, trial_len)

        # Randomization step 2
        shuffle(rater_list_Q)
        shuffle(rater_list_S)

        trial_order = 0

        rater_list = list()

        shorter_list = rater_list_Q if len(rater_list_Q) <= len(rater_list_S) else rater_list_S


        if len(rater_list_Q) != len(rater_list_S):
            #print('Statements and questions are unbalanced:')
            #print(len(rater_list_Q), len(rater_list_S))
            #print()
            pass

        rater_list = [None] * (len(rater_list_Q) + len(rater_list_S))

        current_list = random.choice(['S', 'Q'])

        for i in range(int(len(rater_list)/block_len)):

            if current_list == 'Q':

                start_idx = i*block_len
                end_idx = (i*block_len) + block_len

                if len(rater_list_Q) > block_len:
                    rater_list[start_idx:end_idx] = [rater_list_Q.pop() for i in range(block_len)]
                else:
                    leftover_items = len(rater_list_S)
                    rater_list[start_idx:end_idx] = [rater_list_S.pop() for i in range(leftover_items)]

                current_list = 'S'

            elif current_list == 'S':

                start_idx = i * block_len
                end_idx = (i * block_len) + block_len
                if len(rater_list_S) > block_len:
                    rater_list[start_idx:end_idx] = [rater_list_S.pop() for i in range(block_len)]
                else:
                    leftover_items = len(rater_list_S)
                    rater_list[start_idx:end_idx] = [rater_list_S.pop() for i in range(leftover_items)]
                current_list = 'Q'


        #if (len(rater_list_S) % 5 != 0) or (len(rater_list_Q) % != 0):



        #rater_list[::block_len] = shuffled_lists[0]
        #rater_list[5::block_len] = shuffled_lists[1]

        # Filter None from list
        rater_list = filter(None, rater_list)

        for pair in rater_list:
            #print(pair)
            # Make sure the rater id is the same as the id for the last user existing
            rater_id = rater + starting_id
            #print(rater_id)
            trials_dict_list.append(pairs2data_dict(rater, rater_id, pair, trial_order, data))
            #print(trials_dict_list)

            trial_order += 1


    trial_frame = pd.DataFrame(trials_dict_list, columns = [
        'username',
        'trial',
        'learner_id',
        'sent_typ',
        'sent_group',
        'pre_recording_id',
        'pre_recording_sent',
        'post_recording_id',
        'post_recording_sent',
        'display_order'
    ])

    trial_frame.to_csv(output_path)

    return trial_frame




def generate_trials(num_raters, path_to_metadata, output_path, concurrency=5):
    """Generates randomized order of trials for a set number
    of native speaker raters with a set number of sentences
    rated by all native speakers.
    –––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    num_raters : int
        The number of raters anticipated for the experiment

    path_to_metadata : str
        The path to a metadata sheet in csv from the production experiment

    output_path : str
        A path to save the apportioned stimuli

    keyword arguments:

    concurrency : int -- default 5
        The number of times a given trial is shared by multiple
        raters.

    Function returns the order trials for all raters.

    _________________________________________________________

    concurrency, num_raters, and the amount of comparisons exist
    in a relation which is a necessary condition for not breaking any
    of the constraints to apportionment. This is the following:

    (num_comparisons*2)*concurrency ≤ num_raters

    For our default settings, 2 comparisons and 5 concurrent raters,
    need a minimum of 20 raters.
    """
    # Read in metadata
    data = pd.read_csv(path_to_metadata)
    print("length of data:", len(data))

    # Get list of all trial pairs
    trial_order_list = pairs2list(data)

    # Get current highest user_id + 1 because 0 indexing
    dir_path = os.path.dirname(os.path.realpath(__file__))
    flaskr_db = sqlite3.connect(dir_path+'/../instance/flaskr.sqlite')
    starting_id = flaskr_db.execute(
        'SELECT id FROM user '
        'ORDER by id DESC'
    ).fetchall()[0][0] + 1
    #starting_id = data.user_id.unique().max() + 1

    # Apportion pairs to num_raters
    trial_frame = apportion_pairs(num_raters, trial_order_list, data,  output_path, starting_id, concurrency=concurrency)

    return trial_frame


"""5. Iter over len of list of each group of stimuli for user (from step 4).
    
    1. Select the slice of 2 (n_comparison_condtions*concurrency)
     corresponding to the current iteration
        (something like rater_list[start_slice*i:end_slice*i] where 
        end_slice is checked to be no more than the total length of the list)
    2. Give first 5 S/comparison_1 second 5 Q/comparison_1, Next 5 S/comparison_2...
    

"""


if __name__ == '__main__':

    generate_trials(20, '~/final_data.csv', '~/apportioned.csv', concurrency=5)
