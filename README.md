# Cloud Conundrum Challenge
The code solving the Cloud Conundrum challenge.

We are given a set of stacks, with their dependencies, and then a set of environments with
required stacks.

This program parses everything and, for every environment, finds the missing stack dependencies,
and creates an initialization order for the stacks of every environment, respecting dependencies.

Just run `python etheras.py`. "environments" and "stacks" folders are hardcoded, as
containing environment and stack files, respectively. It will perform a complete run based on
these files.

Dictionaries are used even in intensive graph-specific computations, so performance is not ideal,
but the algorithm complexity remains the same.