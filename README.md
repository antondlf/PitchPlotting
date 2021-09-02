# Teaching L2 Prosody Through Automatic Pitch Visualization

This repository contains the source code for an online experiment that was designed to test a system of automatic pitch visualization
for the learning of L2 prosody. This experiment specifically is designed with the acquisition of Italian question-statement
discrimination in mind. The repository is divided into two main sections. First, **Site** contains the visualization system under **Pitch_Plotting**
and the source code associated with the experiment website, hosted [here](https://prosody.delafuentealvarez.com), under **flaskr**.
Second, a system of automatic notification associated with the experiment is held under **notify_users**.
Below each part of the project will be introduced.

## The Visualization System **Pitch_Plotting**

This system was developed during a Graduate Seminar on Linguistic Rhythm at UCSB taught by Matthew Gordon and Argyro Katsika (Fall 2020, Winter 2021).
The system is held in the script **Pitch_Plot.py**. This script takes in two recordings, one reference and one input,
extracts the pitch out of both and generates a plot with both traces aligned. The reference recording is meant to be 
a native speaker's production of a sentence that is representative of the target intonation being taught. The input recording 
is meant to be the learner's production of that intonational pattern. The pitch array of the input recording is trimmed to exclude
any silence at the beginning or the end of the recording. Then, the corresponding time array is warped to fit into the same time frame
as the reference recording. Although this is very simple, it seems to robustly align pitch excursions at the level of individual sentences. 
This makes it ideal for applications in phrasal intonation as well as lexical pitch accent or phonemic tone. A version of this system is being 
used for a similar application to teach Mandarin Tone [here](https://pitchperfect.training).

## The Site **flaskr**

This part of the repository contains a Flask web application that hosts a set of sentences in Italian that are either questions or statements.
Each user is alotted a sequence of sentences with a controlled number of syllables and accent placements. The site takes a user through 3 sessions,
two of these have 7 pre-training recordings (baselines for comparison), 31 training recordings where they receive automatic visual feedback,
and 7 post-training recordings to assess their ability to generalize what they learned during training. Finally, a third session with 7 more
recordings is meant to assess delayed generalization. The code for this section was originally based on the [Flask tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/index.html)
and was adapted to fit our individual needs.

## Notification System **notify_users**

In order to make a larger experiment possible, I introduced an automatic notification system. This system notifies users of when they should do each session 
(one week apart), and reminds users if they haven't completed the current session within two days. This system is set apart from the rest of the app in order to 
avoid associating user emails from any part of the active web server. Therefore, the user that runs the web-server has no access to this part of the app, but the 
user that runs these notifications has read access for some important parts of flaskr.
