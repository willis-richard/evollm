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

## Prompts
[prompts](./src/evollm/prompts.py) contains the prompts used to generate the strategies.

## Strategies

[strategies](./strategies) contains the generated strategies used in the paper, except for the ChatGPT-4o strategies using the Refine prompt with noise, which have been accidentally lost. Each strategy includes both the natural language descriptions and the implemented algorithm. For the 'prose' prompt, we include both the high-level scenario strategy and the subsequent iterated normal-form game specific strategy.

## Results

[results](./results) contains the results shown in the paper

## Experiments

In order to rerun the analysis from the paper, follow these steps. To see the options, use `--help` on any of the scripts. You will need to configure the openai or anthropic API, and set the corresponding environmental variable `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

Create strategies, for example to use Claude 3.5 Sonnet with 10% noise and prose prompts to create 25 strategies for each attitude (75 in total):
```shell
python3 src/evollm/create_strategies.py --strategy_llm anthropic --n 25 --temp 0.7 --algo my_strategies --prose --noise 0.1
```

Inspect the strategies and then test they run. Either fix any broken strategies, or delete them and re-run create_strategies.py with the same algo name to regenerate the deleted strategies
```shell
python3 tests/test_create_strategies.py --algo my_strategies
```

Rank the strategies in Beaufils tournament using
```shell
python3 src/evollm/rank_strategies.py --algo my_strategies
```

Compare the head-to-head performance of the Attitude-Agents with
```shell
python3 src/evollm/head_to_head.py --algo my_strategies --h2h
```

and assess the Attiude-Agents' performance in the Beaufils tournament with
```shell
python3 src/evollm/head_to_head.py --algo my_strategies
```
