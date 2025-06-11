# AILabTools

## Overview

This repository contains two complementary tools for use when analyzing log file data.
The intent is to demonstrate a methodology for security related log file analysis
with large language models (LLMs).

## The Challenge

All LLMs have a maximum token context window. As of this writing, it is pretty common for
most frontier model LLMs to have a context window of up to approx 128,000 tokens.

* What is a token? Well a token can be a word, or part of a word and is created in the
process of tokenizing textual data for LLMs to be able to understand the context
of the text being analyzed by their embedded Natual Language Processing neural networks.

* Why do we tokenize data for LLM consumption? LLMs do NOT actually understand language
directly. LLMs and all neural network technology process data in the form of mathematical
vectors, which are just lists of numbers. So when we tokenize data, we are actually breaking
the words down into individual tokens, and then building a vocabulary that assigns each
unique word or sub-word a number.

### Log Files are very large!

While from an LLM perspective, you could argue that log files have a lot of repeated words
which certainly will limit the vocabulary size, the actual number of tokenized vectors
produced from most log files will be huge and likely exceed the token context window of an LLM.

* Wait, what is a token context window?  A token context window is
the number of tokens that a large language model can consider at one time.  When you
provide both a prompt, and some log data to an LLM, the token context window consists
of all of that data plus whatever output might have been generated so far.

* Why is the token context window limited? The limitation exists due to computational and
architectural constraints. Specifically the LLM transformer architecture have a quadratic
computational complexity of ($$ O(n^2) $$). There exists additional LLM training cost
and complexity in the form of much larger input data sizes when the context window is expanded.

## Solution/Approach

In order to approach the task of log analysis as a Cyber Security professional using an LLM,
we have to break the overall task down into sub-tasks as follows:

* We need to break the logging data down into smaller consumable chunks.
* A well engineered prompt will be prepended to each logging chunk for analysis.
* The LLM must analyze the data in parts without exceeding the context window size.
* The LLM must remember the results of each smaller task as it moves through all of the data.
* When all of the data has been analyzed, the LLM must summarize the entire result and give high quality conclusions.

### Choices!

There are some possible variations on how we approach the problem, specifically surrounding the idea
of having the LLM *remember* each chunk of analysis as it passes through the data. We could for example
decide to pass the analysis result from a prior log chunk analysis along to the next analysis as a part
of the next prompt. Perhaps label it as "prior analysis results" for example.  Alternatively, we could
decide to just save the results of each phase in a text file summary, and then provide an alternate
prompt to analyze all of the accumulated summaries.

I chose the latter approach which is an analysis of all of the resulting summaries in one final LLM summary
prompt and response. One advantage of doing this is that we can make the choice of perhaps using a different
more powerful model for that **final pass** so to speak.

### Scripting Details

Regardless of the choices we make, we do need a programmatic solution which will interact with the LLM
models using a prompting API, and proceed through the methodology to a conclusion.
Thus, I decided to write two Python scripts to accomplish the stated challenges.

1. llm_logchunker.py: a Python script to break a log file down into LLM consume bite size chunks and write them
to a sqlite database.
2. llm_loganalyzer.py: a Python script to read each log chunk, and a well engineered prompt and feed it all sequentially
into an OpenAI model using their API. The analyzer will save each interim response, and then has a **final pass** option
to read all of the summaries for the final result.

### Installation

#### Requirements

* Python 3.13.0 or higher
* openai python module
* An OpenAI API Key
* Optionally: a dedicated conda environment

Before running either script, do the following from the command line:

    pip install -r requirements.txt
    export OPEN_API_KEY="<insert your key text here...>"

