import argparse
import codecs
import os
import shlex
import sys

try:
    import urllib.request as urlrequest
except ImportError:
    import urllib2.urlopen as urlrequest

import zipfile
import tempfile
import tarfile
import shutil

import pickle
import spacy
import subprocess

from tilse.data import corpora

# given original timeline17 dataset directory 

data_root = '/shared/nas/data/m1/wangz3/cs598hj_sp2022/assginment1/baselines/tilse/bin/timeline17_original'
path_raw = os.path.join(data_root,'Data')
path = data_root
corpus = 'timeline17'

# handle special tokens for xml
print('handling special tokens for xml...')

pairs = [("&", "&amp;"), ("<", "\&lt;"), (">", "\&gt;")]

for pair in pairs:
    find_command = "find " + path_raw + " -name '*htm*' -type f -print0"
    sed_command = "xargs -0 sed -i 's/" + pair[0] + "/" + pair[1] + "/g'"

    find_output = subprocess.Popen(
        shlex.split(find_command),
        stdout=subprocess.PIPE
    )

    subprocess.Popen(
        shlex.split(sed_command),
        stdin=find_output.stdout
    )

    find_output.wait()

# tag with heideltime
print('tagging with heideltime...')
heideltime_directory = os.path.dirname(os.path.realpath(__file__)) + \
                       "/../tilse/tools/heideltime/"

apply_heideltime = heideltime_directory + "apply-heideltime.jar"
heideltime_config = heideltime_directory + "config.props"

ending = "txt"
if corpus == "crisis":
    ending = "tokenized"

counter = 0

for topic in os.listdir(path_raw):
    subprocess.run(
        [
            "java",
            "-jar",
            apply_heideltime,
            heideltime_config,
            os.path.join(path_raw, f"{topic}/InputDocs"),
            ending
        ]
    )

    print(f'done topic {topic}')
    counter += 1

# fix some heideltime bugs

replace_pairs = [
    ("T24", "T12"),
    (")TMO", "TMO"),
    (")TAF", "TAF"),
    (")TEV", "TEV"),
    (")TNI", "TNI"),
]

for pair in replace_pairs:
    find_command = "find " + path_raw + " -name '*.timeml' -type f -print0"

    find_output = subprocess.Popen(
        shlex.split(find_command),
        stdout=subprocess.PIPE
    )

    sed_command = "xargs -0 sed -i 's/" + pair[0] + "/" + pair[1] + "/g'"

    subprocess.Popen(
        shlex.split(sed_command),
        stdin=find_output.stdout
    )

    find_output.wait()

print('done heideltime')
# fix issue with mj bbc timeline in timeline 17 corpus

if corpus == "timeline17":
    other_sed_command = "sed -i 's/2011-04-0/2011-04-02/g' " + os.path.join(path_raw,"/mj/timelines/bbc.co.uk.txt")
    subprocess.Popen(shlex.split(other_sed_command))

print('done fixing issue with mj bbc timeline')


#############################################

# linguistic processing and serialization

nlp = spacy.load("en_core_web_sm")

path_dumped = os.path.join(path,"dumped_corpora")

if not os.path.exists(path_dumped):
    os.makedirs(path_dumped)

for topic in os.listdir(path_raw):
    print('create corpora for topic:', topic)
    corpus = corpora.Corpus.from_folder(os.path.join(path_raw, f"{topic}/InputDocs"), nlp)

    with open(os.path.join(path_dumped, f"{topic}.corpus.obj"), "wb") as my_file:
        pickle.dump(corpus, my_file)
