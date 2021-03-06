#!/usr/bin/env python

import argparse
import codecs
import json
import logging
import os
import pickle
import pprint
import sys
from collections import defaultdict

import spacy

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from tilse.models.regression import regression
from tilse.models.submodular import submodular, upper_bounds
from tilse.models.chieu import chieu
from tilse.models.random import random
from tilse.data import timelines
from tilse.evaluation import rouge

parser = argparse.ArgumentParser(description='Predict timelines from a corpus.')
parser.add_argument('config_file', help='config JSON file containing parameters.')

args = parser.parse_args()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(''message)s')

config = json.load(open(args.config_file))

temp_reference_timelines = defaultdict(list)

news_corpora = {}
reference_timelines = {}

nlp = spacy.load("en_core_web_sm")

# read corpora and timelines
corpus = config["corpus"]
raw_directory = config["corpus"] + "/raw/"
dumped_corpora_directrory = config["corpus"] + "/dumped_corpora/"

keyword_mapping = config["keyword_mapping"]

restrict_topics_to = config["restrict_topics_to"]

for topic in sorted(os.listdir(raw_directory)):
    if restrict_topics_to is not None and topic not in restrict_topics_to:
        continue

    logging.info(topic)

    news_corpora[topic] = pickle.load(open(dumped_corpora_directrory + topic + ".corpus.obj", "rb"))
    # print(news_corpora[topic].name,news_corpora[topic].docs[0].publication_date, news_corpora[topic].docs[0].sentences)
    # print()
    # quit()

    if keyword_mapping is not None and keyword_mapping[topic] is not None:
        news_corpora[topic] = news_corpora[topic].filter_by_keywords_contained(keyword_mapping[topic])

    for filename in sorted(list(os.listdir(raw_directory + "/" + topic + "/timelines/"))):
        full_path = raw_directory + "/" + topic + "/timelines/" + filename

        temp_reference_timelines[topic].append(
            timelines.Timeline.from_file(codecs.open(full_path, "r", "utf-8", "replace"))
        )

for topic in temp_reference_timelines:
    reference_timelines[topic] = timelines.GroundTruth(temp_reference_timelines[topic])

evaluator = rouge.TimelineRougeEvaluator(measures=["rouge_1", "rouge_2"],
                                         beta=1, rouge_computation=config["rouge_computation"])

algorithm = None

if config["algorithm"] == "chieu":
    algorithm = chieu.Chieu(config, evaluator)
elif config["algorithm"] == "regression":
    algorithm = regression.Regression(config, evaluator)
elif config["algorithm"] == "random":
    algorithm = random.Random(config, evaluator)
elif config["algorithm"] == "submodular":
    algorithm = submodular.Submodular(config, evaluator)
elif config["algorithm"] == "upper_bound":
    algorithm = upper_bounds.UpperBounds(config, evaluator)

returned_timelines, scores = algorithm.run(news_corpora, reference_timelines)

groundtruths = {}

print("")

pprint.pprint(config)
scores_to_print = "\t".join(("\n" + str(scores)).splitlines(True))
print(scores_to_print)

for topic in reference_timelines:
    for i, tl in enumerate(reference_timelines[topic].timelines):
        groundtruths[topic + "_" + str(i)] = tl

pickle.dump((returned_timelines, groundtruths, scores), open(config["name"] + ".obj", "wb"))
