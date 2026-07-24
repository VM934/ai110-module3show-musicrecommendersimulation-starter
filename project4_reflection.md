# Project 4 Reflection: Applied AI System

## Base project and original scope

The base project is VibeCompass 2.0, the Music Recommender Simulation from
Project 3. Its original scope was to rank a small fictional song catalog using
transparent feature weights, selectable strategies, and diversity reranking.

## New reliability feature

Project 4 adds an integrated reliability layer. It validates profile values,
warns when requested genres or moods are absent from the catalog, refuses
malformed or low-confidence requests, reruns ranking to verify deterministic
stability, and checks that every result has a non-negative score and an
explanation. `evaluation.py` exercises normal and adversarial cases and prints a
pass/fail summary.

## AI collaboration

AI helped draft the audit structure and identify boundary cases. A helpful
suggestion was to distinguish a warning about missing catalog coverage from an
abstention for invalid numeric input; those cases represent different risks. A
flawed suggestion would be to generate a confident natural-language explanation
even when no catalog evidence supports the requested genre or mood. I rejected
that behavior and kept explicit warnings and abstention paths that can be tested.

## Verification and responsibility

Correctness was checked with automated tests, the evaluation harness, and a
Mermaid architecture diagram that matches the implemented data flow. The human
remains responsible for reviewing warnings, the catalog, and the score reasons
before treating a result as useful.

## Limitations and future improvements

The guardrails cannot make a 17-song catalog representative, and a score
threshold is only a heuristic. Future work should calibrate confidence on a
larger balanced catalog, add retrieval-grounded explanations from trusted music
metadata, and log evaluation results over time to detect regressions.
