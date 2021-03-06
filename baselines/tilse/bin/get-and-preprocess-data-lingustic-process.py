#!/usr/bin/env python

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

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from tilse.data import corpora

# parser = argparse.ArgumentParser(description='Get and preprocess timeline data.')
# parser.add_argument('corpus_name', help='Name of the corpus to download (either timeline17 or crisis).')

# args = parser.parse_args()
# corpus = args.corpus_name

# if corpus not in ["crisis", "timeline17"]:
#     print("Corpus must be either crisis or timeline17. Exiting.")

# # download corpus and extract archive

# to_retrieve = ""

# if corpus == "timeline17":
#     to_retrieve = "http://l3s.de/~gtran/timeline/Timeline17.zip"
# elif corpus == "crisis":
#     to_retrieve = "http://l3s.de/~gtran/timeline/crisis.data.tar.gz"

# filename, _ = urlrequest.urlretrieve(to_retrieve)

# archive_ref = None

# if corpus == "timeline17":
#     archive_ref = zipfile.ZipFile(filename, 'r')
# elif corpus == "crisis":
#     archive_ref = tarfile.open(filename, 'r:gz')

# temp_path = tempfile.mkdtemp() + "/"
# archive_ref.extractall(temp_path)

# # transform directory structure

# path = os.getcwd() + "/" + corpus + "/"

# path_raw = os.getcwd() + "/" + corpus + "/raw/"

# if corpus == "timeline17":
#     topic_mapping = {
#         "bpoil": "bpoil",
#         "EgyptianProtest": "egypt",
#         "Finan": "finan",
#         "H1N1": "h1n1",
#         "haiti": "haiti",
#         "IraqWar": "iraq",
#         "LibyaWar": "libya",
#         "MJ": "mj",
#         "SyrianCrisis": "syria"
#     }

#     # copy articles and timelines
#     for original, mapped in topic_mapping.items():
#         os.makedirs(path_raw + mapped + "/articles/")
#         os.mkdir(path_raw + mapped + "/timelines/")

#         for corpus_dir in sorted(os.listdir(temp_path + "Timeline17/Data/")):
#             if corpus_dir.startswith(original):

#                 # first articles...
#                 for date_dir in os.listdir(temp_path + "Timeline17/Data/" + corpus_dir + "/InputDocs/"):
#                     if not os.path.isdir(temp_path + "Timeline17/Data/" + corpus_dir + "/InputDocs/" + date_dir):
#                         continue

#                     if not os.path.isdir(path_raw + mapped + "/articles/" + date_dir + "/"):
#                         os.mkdir(path_raw + mapped + "/articles/" + date_dir + "/")

#                     for filename in sorted(
#                             os.listdir(temp_path + "Timeline17/Data/" + corpus_dir + "/InputDocs/" + date_dir + "/")):
#                         shutil.copy(
#                             temp_path + "Timeline17/Data/" + corpus_dir + "/InputDocs/" + date_dir + "/" + filename,
#                             path_raw + mapped + "/articles/" + date_dir + "/"
#                         )

#                 # ...and then timelines
#                 for tl_filename in os.listdir(temp_path + "Timeline17/Data/" + corpus_dir + "/timelines/"):
#                     if tl_filename != ".DS_Store":
#                         shutil.copy(
#                             temp_path + "Timeline17/Data/" + corpus_dir + "/timelines/" + tl_filename,
#                             path_raw + mapped + "/timelines/"
#                         )
# elif corpus == "crisis":
#     # copy articles and timelines
#     for topic in os.listdir(temp_path):
#         os.makedirs(path_raw + topic + "/articles/")
#         os.mkdir(path_raw + topic + "/timelines/")

#         # first articles...
#         for date_dir in os.listdir(temp_path + topic + "/public/content/"):
#             if not os.path.isdir(temp_path + topic + "/public/content/" + date_dir):
#                 continue

#             if not len(date_dir.split("-")[-1]) == 2:
#                 print(date_dir)
#                 continue

#             os.mkdir(path_raw + topic + "/articles/" + date_dir + "/")

#             for filename in sorted(os.listdir(temp_path + topic + "/public/content/" + date_dir + "/")):
#                 shutil.copy(
#                     temp_path + topic + "/public/content/" + date_dir + "/" + filename,
#                     path_raw + topic + "/articles/" + date_dir + "/"
#                 )

#         # ...and then timelines
#         for tl_filename in os.listdir(temp_path + topic + "/public/timelines/"):
#             if not tl_filename.startswith("."):
#                 shutil.copy(
#                     temp_path + topic + "/public/timelines/" + tl_filename,
#                     path_raw + topic + "/timelines/"
#                 )

# shutil.rmtree(temp_path)

# # sentence split and tokenize (if neccessary)

# nlp = spacy.load("en_core_web_sm")

# if corpus == "crisis":
#     counter = 0

#     for topic in os.listdir(path_raw):
#         for date in os.listdir("/".join([path_raw, topic, "articles"])):
#             if os.path.isdir("/".join([path_raw, topic, "articles", date])):
#                 for filename in os.listdir("/".join([path_raw, topic, "articles", date])):

#                     filename_to_process = "/".join([path_raw, topic, "articles", date,
#                                                     filename])

#                     sentences = ""
#                     with codecs.open("/".join([path_raw, topic, "articles", date,
#                                                filename]), "r", encoding="utf-8", errors="ignore") as file:
#                         for line in file.readlines():
#                             sentences += line

#                     doc = nlp(sentences)

#                     splitted_and_tokenized = ""

#                     for sent in doc.sents:
#                         splitted_and_tokenized += " ".join(
#                             [tok.text for tok in sent if not tok.text.isspace()]).strip() + "\n"

#                     splitted_and_tokenized = splitted_and_tokenized.strip()

#                     tokenized_filename = "/".join([path_raw, topic, "articles", date,
#                                                    filename]) + ".tokenized"

#                     with open(tokenized_filename, "w") as file:
#                         file.write(splitted_and_tokenized)

#                     print(counter)
#                     counter += 1

# # handle special tokens for xml

# pairs = [("&", "&amp;"), ("<", "\&lt;"), (">", "\&gt;")]

# for pair in pairs:
#     find_command = "find " + path_raw + " -name '*htm*' -type f -print0"
#     sed_command = "xargs -0 sed -i 's/" + pair[0] + "/" + pair[1] + "/g'"

#     find_output = subprocess.Popen(
#         shlex.split(find_command),
#         stdout=subprocess.PIPE
#     )

#     subprocess.Popen(
#         shlex.split(sed_command),
#         stdin=find_output.stdout
#     )

#     find_output.wait()

# # tag with heideltime

# heideltime_directory = os.path.dirname(os.path.realpath(__file__)) + \
#                        "/../tilse/tools/heideltime/"

# apply_heideltime = heideltime_directory + "apply-heideltime.jar"
# heideltime_config = heideltime_directory + "config.props"

# ending = "txt"
# if corpus == "crisis":
#     ending = "tokenized"

# counter = 0

# for topic in os.listdir(path_raw):
#     subprocess.run(
#         [
#             "java",
#             "-jar",
#             apply_heideltime,
#             heideltime_config,
#             "/".join([path_raw, topic, "articles"]),
#             ending
#         ]
#     )

#     print(counter)
#     counter += 1

# # fix some heideltime bugs

# replace_pairs = [
#     ("T24", "T12"),
#     (")TMO", "TMO"),
#     (")TAF", "TAF"),
#     (")TEV", "TEV"),
#     (")TNI", "TNI"),
# ]

# for pair in replace_pairs:
#     find_command = "find " + path_raw + " -name '*.timeml' -type f -print0"

#     find_output = subprocess.Popen(
#         shlex.split(find_command),
#         stdout=subprocess.PIPE
#     )

#     sed_command = "xargs -0 sed -i 's/" + pair[0] + "/" + pair[1] + "/g'"

#     subprocess.Popen(
#         shlex.split(sed_command),
#         stdin=find_output.stdout
#     )

#     find_output.wait()

# # fix issue with mj bbc timeline in timeline 17 corpus

# if corpus == "timeline17":
#     other_sed_command = "sed -i 's/2011-04-0/2011-04-02/g' " + path_raw + "/mj/timelines/bbc.co.uk.txt"
#     subprocess.Popen(shlex.split(other_sed_command))








#############################################

# linguistic processing and serialization
path = './timeline17/'
path_raw = './timeline17/raw/'

nlp = spacy.load("en_core_web_sm")

path_dumped = path + "dumped_corpora/"

# os.mkdir(path_dumped)

for topic in os.listdir(path_raw):
    corpus = corpora.Corpus.from_folder(path_raw + topic + "/articles/", nlp)

    with open(path_dumped + topic + ".corpus.obj", "wb") as my_file:
        pickle.dump(corpus, my_file)
