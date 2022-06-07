import pandas as pd
import numpy as np
import sqlite3


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


def get_recordings(path_to_metadata):
    """From metadata extracts all recordings for a given comparison trial

    """
    comparison_dict = {
        'condition_1': {'pre': 'Session 1', 'post': 'Session 1'},
        'condition_2': {'pre': 'Session 1', 'post': 'Session 2'},
        'condition_3': {'pre': 'Session 1', 'post': 'Session 3'}
    }

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

                if len(trial_id_post) > 1:
                    # print('trial for user', user, 'and group', group, 'and sent_type', sent_type, 'has more than one file.')

                    trial_id_post = trial_id_post.iloc[0]
                # else:
                # print('trial for user', user, 'and group', group, 'and sent_type', sent_type, 'does not have than one file.')
                # print()

                cond_dict[group + sent_type] = (trial_id_pre, trial_id_post)

            user_dict[cond] = cond_dict

        trial_order_dict[user] = user_dict

        return trial_order_dict

def generate_trials(num_raters, num_block, block_len, concurrency=5):
    """Generates randomized order of trials for a set number
    of native speaker raters with a set number of sentences
    rated by all native speakers.
    –––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    num_raters : int
        The number of raters anticipated for the experiment
    num_block : int
        The number of blocks in the trial
    block_len : int
        The number of trials in each block

    keyword arguments:

    concurrency : int -- default 5
        The number of times a given trial is shared by multiple
        raters.

    Function returns the order trials for all raters.
    """