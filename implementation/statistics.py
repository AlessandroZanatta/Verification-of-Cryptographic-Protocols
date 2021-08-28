#!/usr/bin/env python

import numpy as np
import json
import logging
from rich.logging import RichHandler

# ------------ #
# Logger setup #
# ------------ #

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

# ------------------- #
# Tweakable variables #
# ------------------- #
INPUT_FILE = './benchmarks.json'

with open(INPUT_FILE) as f:
    data = json.load(f)

for x in data:
    protocol = x['protocol']
    version = x['version']
    tool = x['tool']

    results = x['results']
    peak_size = np.asarray(results['peak_size'])
    time = np.asarray(results['time'])
    cpu_time = np.asarray(results['cpu_time'])

    stats = f'''Protocol: {protocol}
    Version: {version}
    Tool: {tool}

    Statistics:
        Peak size (RSS):
            Mean: {peak_size.mean()} 
            Std: {peak_size.std()}
            Median: {np.median(peak_size)}
            Min: {peak_size.min()}
            Max: {peak_size.max()}
        Time:
            Mean: {time.mean()} 
            Std: {time.std()}
            Median: {np.median(time)}
            Min: {time.min()}
            Max: {time.max()}
        CPU time (%):
            Mean: {cpu_time.mean()} 
            Std: {cpu_time.std()}
            Median: {np.median(cpu_time)}
            Min: {cpu_time.min()}
            Max: {cpu_time.max()}
    '''

    log.info(stats)
    

