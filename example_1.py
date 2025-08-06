"""
Fit a model and later use it to make a prediction.
"""
import argparse
import os
import sys
from pathlib import Path

from client import Client

parser = argparse.ArgumentParser()
parser.add_argument("--train", default="train.parquet")
parser.add_argument("--test", default="test.parquet")
args = parser.parse_args()

client = Client()

dataset_id = client.upload(args.train)

print("\nfit\n---")
model_id = client.fit(dataset_id, timeout=120)

test_dataset_id = client.upload(args.test)

print("\npredict\n-------")

prediction_id = client.predict(test_dataset_id, model_id, timeout=120)
prediction = client.download(prediction_id)

print("\nGot prediction:\n---------------")
print(prediction)
