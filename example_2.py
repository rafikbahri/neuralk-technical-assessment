"""
Launch 40 `fit` tasks at the same time.
"""
import os
from pathlib import Path

from client import Client

client = Client()

dataset_id = client.upload("train.parquet")

model_ids = []

for _ in range(20):
    model_ids.append(client.fit(dataset_id))
