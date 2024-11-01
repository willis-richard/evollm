This repository accompanies the paper "Will Systems of LLM Agents Lead to Cooperation: An Investigation into a Social Dilemma", under review at OpenReview.

## Installation

Install the dependencies using conda

```shell
conda create -f environment.yml
```

Activate the environment and add the repo to the PYTHONPATH

```shell
conda activate evollm
export PYTHONPATH="$(pwd)/src"
```

## Experiments

In order to rerun the analysis from the paper, follow these steps. To see the options, use `--help` on any of the scripts.

Create strategies, for example to use Claude 3.5 Sonnet with 10% noise and prose prompts:
```shell
python3 src/evollm/create_strategies.py --strategy_llm anthropic --n 25 --temp 0.7 --algo anthropic_prose_noise --prose --noise 0.1
```

Inspect the stragies and then test they run. Either delete or fix any broken strategies.
```shell
python3 tests/test_create_strategies.py --algo anthropic_prose_noise.py
```

Rank the strategies in Beaufils tournament using
```shell
python3 src/evollm/rank_strategies.py --algo anthropic_prose_noise.py
```

Compare their head-to-head performance with
```shell
python3 src/evollm/head_to_head.py --algo anthropic_prose_noise.py --h2h
```

or the Attiude-Agents performance in the Beaufils tournament with
```shell
python3 src/evollm/head_to_head.py --algo anthropic_prose_noise.py
```


## Strategies

`./save` contains the generated strategies used in the paper

## Results

`./results` contains the results shown in the paper
