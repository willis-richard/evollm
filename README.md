This repository accompanies the paper "Will Systems of LLM Agents Lead to Cooperation: An Investigation into a Social Dilemma", under review at OpenReview.

## Installation

Install the dependencies using conda

```shell
conda create -f environment.yml
```

Activate the environment and add the repo to the PYTHONPATH

```shell
conda activate XXX
export PYTHONPATH="$(pwd)/src"
```

## Experiments

In order to rerun the analysis from the paper, call

```shell
python3 XXX.py
```

To see the options, use `--help` on any of the scripts

## Strategies

`./save` contains the generated staregies used in the paper

## Results

`./results` contains the results shown in the paper
