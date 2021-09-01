#!/usr/bin/env python

import numpy as np
import json
import os
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

CAPTIONS = {
    'DHanonymous': 'Comparison table for anonymous Diffie-Hellman',
    'DHephemeral': 'Comparison table for ephemeral Diffie-Hellman',
    'DHpfs': 'Comparison table for ephemeral Diffie-Hellman with post-compromise',
    'PublicNeedhamSchroederfixed': 'Comparison table for Needham-Schroeder Public Key',
    'PublicNeedhamSchroederflawed': 'Comparison table for Needham-Schroeder-Lowe Public Key'
}


with open(INPUT_FILE) as f:
    data = json.load(f)

def create_table(args, name, caption):
    return r'''
\begin{{table}}[]
\makebox[\textwidth]{{
\begin{{tabular}}{{c|c|c|c|c|c|c|c|c|c|}}
\cline{{2-10}}
\multicolumn{{1}}{{l|}}{{}} & \multicolumn{{3}}{{c|}}{{\textbf{{Peak memory size (kb)}}}} & \multicolumn{{3}}{{c|}}{{\textbf{{Time (s)}}}} & \multicolumn{{3}}{{c|}}{{\textbf{{CPU time (\%)}}}} \\ \cline{{2-10}} 
\multicolumn{{1}}{{l|}}{{}}                    & Tamarin & Verifpal & Proverif & Tamarin & Verifpal & Proverif & Tamarin & Verifpal & Proverif \\ \hline
\multicolumn{{1}}{{|c|}}{{\textbf{{Mean}}}}      & {:.0f}   & {:.0f}    & {:.0f}    & {:.0f}   & {:.0f}    & {:.0f}    & {:.2f}   & {:.2f}    & {:.2f}    \\ \hline
\multicolumn{{1}}{{|c|}}{{\textbf{{Deviation}}}} & {:.0f}   & {:.0f}    & {:.0f}    & {:.0f}   & {:.0f}    & {:.0f}    & {:.2f}   & {:.2f}    & {:.2f}    \\ \hline
\multicolumn{{1}}{{|c|}}{{\textbf{{Median}}}}    & {:.0f}   & {:.0f}    & {:.0f}    & {:.0f}   & {:.0f}    & {:.0f}    & {:.2f}   & {:.2f}    & {:.2f}    \\ \hline
\multicolumn{{1}}{{|c|}}{{\textbf{{Min}}}}       & {:.0f}   & {:.0f}    & {:.0f}    & {:.0f}   & {:.0f}    & {:.0f}    & {:.2f}   & {:.2f}    & {:.2f}    \\ \hline
\multicolumn{{1}}{{|c|}}{{\textbf{{Max}}}}       & {:.0f}   & {:.0f}    & {:.0f}    & {:.0f}   & {:.0f}    & {:.0f}    & {:.2f}   & {:.2f}    & {:.2f}    \\ \hline
\end{{tabular}}
}}
\label{{{}}}
\caption{{{}}}
\end{{table}}'''.format(*args, 'tab:'+name, caption).replace(' -1 ', 'NA').replace('-1.00', 'NA')

def save_table(name, table):
    where = '../paper/tables'
    
    with open(os.path.join(where, name + '.tex',), 'w') as f:
        f.write(table)

stats = {}
for x in data:
    protocol = x['protocol']
    version = x['version']
    tool = x['tool']

    results = x['results']
    peak_size = np.asarray(results['peak_size'])
    time = np.asarray([t * 1000 for t in results['time']])
    cpu_time = np.asarray([t / 100 for t in results['cpu_time']])

    idpv = protocol+version
    if idpv not in stats.keys():
        stats[idpv] = {
            'tamarin-prover': [],
            'verifpal': [],
            'proverif': []
        }

    stats[idpv][tool].append(peak_size.mean())
    stats[idpv][tool].append(peak_size.std())
    stats[idpv][tool].append(np.median(peak_size))
    stats[idpv][tool].append(peak_size.min())
    stats[idpv][tool].append(peak_size.max())

    stats[idpv][tool].append(time.mean())
    stats[idpv][tool].append(time.std())
    stats[idpv][tool].append(np.median(time))
    stats[idpv][tool].append(time.min())
    stats[idpv][tool].append(time.max())

    stats[idpv][tool].append(cpu_time.mean())
    stats[idpv][tool].append(cpu_time.std())
    stats[idpv][tool].append(np.median(cpu_time))
    stats[idpv][tool].append(cpu_time.min())
    stats[idpv][tool].append(cpu_time.max())

for idpv in stats.keys():
    for tool in stats[idpv].keys():
        if len(stats[idpv][tool]) != 15:
            stats[idpv][tool] = [-1] * 15

for idpv, st in stats.items():
    log.info(idpv)

    sort_list = ['tamarin-prover', 'verifpal', 'proverif']
    index_map = {v: i for i, v in enumerate(sort_list)}

    sorted_st = sorted(st.items(), key=lambda pair: index_map[pair[0]])
    args = []

    for i in range(5):
        for j in range(3):
            for tool, data in sorted_st:
                args.append(data[j*5 + i])

    save_table(idpv, create_table(args, idpv, CAPTIONS[idpv]))
