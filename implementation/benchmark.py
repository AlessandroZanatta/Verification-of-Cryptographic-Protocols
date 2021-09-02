#!/usr/bin/env python

import os
import shutil
import logging
import subprocess
import progressbar
import re
import json
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

# Output folder
OUTPUT_FILE = 'benchmarks.json'
BASE_DIR = '.'
PROTOCOLS_WHITELIST = ['DH', 'PublicNeedhamSchroeder']
PROOF_FILENAME = 'protocol'
GLOBAL_RESULTS = []

# List of languages/tools used. Must use the same key as the name used to invoke the tool.
LANGUAGES = {
    'proverif': {
        'cmdline': 'proverif %s',
        'executions': 1000,
        'extension': '.pv'
    },
    'verifpal': {
        'cmdline': 'verifpal verify %s',
        'executions': 1000,
        'extension': '.vp'
    },
    'tamarin-prover': {
        'cmdline': 'tamarin-prover %s --prove',
        'executions': 50,
        'extension': '.spthy'
    }
}


# External dependencies
DEPENDENCIES = ['/usr/bin/time', 'hyperfine']

# External deps configurations
TIME_CMDLINE = '/usr/bin/time -v -- %s 1> /dev/null'
HYPERFINE_CMDLINE = "hyperfine --min-runs %d --warmup 5 --export-json %s '%s'"
HYPERFINE_TMPFILE = '/tmp/hyperfine-tmp'

# --------- #
# Functions #
# --------- #

def check_dependencies():
    err = False
    for progname in DEPENDENCIES:
        if not shutil.which(progname):
            log.fatal(f'Missing dependency: {progname}')
            err = True

    for progname in LANGUAGES.keys():
        if not shutil.which(progname):
            log.fatal(f'Missing tool dependency: {progname}')
            err = True


    if err:
        log.fatal('Requirements check failed. Please install missing dependencies.')
        exit(1)

def elaborate_and_save_results(results, protocol, version, tool):
    global GLOBAL_RESULTS
    peak_sizes = []
    cpu_times  = []
    for res in results:
        peak_size = re.search(r'Maximum resident set size \(kbytes\): ([0-9]+)', res).group(1)
        log.debug(f'Peak size: {peak_size}')

        cpu_time = re.search(r'Percent of CPU this job got: ([0-9]+)%', res).group(1)
        log.debug(f'CPU time: {cpu_time}')

        peak_sizes.append(int(peak_size))
        cpu_times.append(int(cpu_time))

    with open(HYPERFINE_TMPFILE) as f:
        times = json.load(f)['results'][0]['times']

    GLOBAL_RESULTS.append({'protocol': protocol, 'version': version, 'tool': tool, 'results': {'peak_size': peak_sizes, 'time': times, 'cpu_time': cpu_times}})

def serialize_results():
    global GLOBAL_RESULTS
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(GLOBAL_RESULTS, f, indent=4) 

def run_benchmarks():
    for protocol in os.listdir(BASE_DIR):
        if protocol not in PROTOCOLS_WHITELIST:
            continue
            
        log.info(f'Starting benchmarks for protocol: {protocol}')
        for version in os.listdir(os.path.join(BASE_DIR, protocol)):
            for tool, configs in LANGUAGES.items():
                model_dir = os.path.join(BASE_DIR, protocol, version, tool)
                benchmark_command = configs['cmdline'] % os.path.join(model_dir, PROOF_FILENAME + configs['extension'])


                results = []
                command = TIME_CMDLINE % benchmark_command
                log.debug(f'Running "{command}"')

                for _ in progressbar.progressbar(range(configs['executions'])):
                    results.append(subprocess.Popen(command, shell=True, stderr=subprocess.PIPE).stderr.read().decode())
               
                is_error = re.search(r'Command exited with non-zero status [0-9]*', results[0])
                if is_error:
                    log.warning(f'Benchmark failed for tool {tool}, protocol {protocol} and version {version}')
                    continue

                command = HYPERFINE_CMDLINE % (configs['executions'], HYPERFINE_TMPFILE, benchmark_command)
                subprocess.Popen(command, shell=True).wait()

                elaborate_and_save_results(results, protocol, version, tool)
                

def main():
    check_dependencies()
    run_benchmarks()
    serialize_results()




if __name__ == '__main__':
    main()
