# Touch Grass Planner

[![Verification](https://github.com/Parteek-yadav/touch-grass-planner/actions/workflows/verify.yml/badge.svg)](https://github.com/Parteek-yadav/touch-grass-planner/actions/workflows/verify.yml)

Live browser demo: **https://parteek-yadav.github.io/touch-grass-planner/**

The hosted version computes entirely in your browser after its static assets load. No account or Python installation is needed to use it; no prediction API, analytics or third-party scripts. Initial page/asset loads still require an internet connection; fresh offline loads are not promised.

A tiny, genuinely trainable local AI that recommends a gentle outdoor pause, nature noticing, accessible wander, or park loop. Built October 10, 2026 as a Hacktoberfest Week 1 Touch Grass challenge prototype. Free, offline, Python standard library only, MIT licensed. No account, API key, paid inference, external model download or telemetry. The browser downloads only this site's own static assets.

## Quick start

Install/use Python 3.10 or newer. Open a terminal in this folder. Windows examples use `python`; macOS/Linux may use `python3` instead for every command.

```text
python planner.py train
python -m unittest -v
python verify.py
python build_site.py
python planner.py predict --time 15 --energy medium --setting street
python planner.py predict --time 30 --energy high --setting park
python planner.py predict --time 30 --energy high --setting park --stationary-only
python planner.py predict --time 30 --energy high --setting park --unsafe
python app.py
```

For the optional web interface, open http://127.0.0.1:8765 after the last command. Ctrl+C stops it. Server binds only to loopback; do not expose it publicly. Opening index.html directly does not run predictions: it needs this server. The local server uses the same saved Python model as the CLI. A trained model.json is included; training overwrites only that local file.

## How the AI actually works

Categorical Naive Bayes learns class priors and conditional frequencies from data/synthetic.csv. Input features are available minutes (5/15/30), energy (low/medium/high), and surroundings (doorstep/street/park). Laplace smoothing handles sparse categories; log-space scoring avoids numerical underflow. Training writes inspectable parameters to model.json. Inference normalizes scores over all trained classes. The highest-scoring *eligible* label becomes the plan. Tests explicitly retrain with changed labels and verify the actual recommendation changes: this is not a hard-coded advice picker with an AI badge.

Hard safety/access/time filters are intentionally separate from learned ranking. The unsafe toggle bypasses the model; stationary-only removes movement plans; park loops require a park; activities cannot exceed the selected time. Scores shown remain scores over all trained labels, not conditional probabilities after filtering. A low-score winner is still uncertain; no calibrated probability or measured success rate is claimed.

## Synthetic data and limitations

81 deliberately synthetic designer preference votes, three per each of 27 contexts. Repeated votes express a design preference rather than independent observations. Dataset and model are illustrative, not validated on humans. No real outdoor field test, real-user study, health benefit, recommendation accuracy, or weather lookup is claimed. Naive Bayes assumes feature independence and can learn biases from these labels. It cannot judge weather, air quality, route accessibility, location, wildlife, daylight, traffic, or personal medical needs. Check those yourself. If outdoors is unsafe or inaccessible, skip it.

The tiny model can prefer stationary observation even when more time is available; this is intentional, not an obligation to exercise. Stationary-only is an explicit user constraint rather than an inferred disability judgment. The energy categories are subjective and not a medical assessment.

## Reproduce and improve

Edit synthetic CSV labels, keep provenance explicit, run training and tests. Custom labels must be defined with constraints in ACTIVITIES first. Test output is in docs/test-output.txt; reproducible sample predictions are in docs/sample-predictions.json; docs/demo.html displays those real outputs as a static demo, not a second AI implementation. No contest entry has been published.

## Open innovation

Source, learned parameters, synthetic data and safety rules are inspectable and modifiable under MIT. Python and its standard library provide the runtime; no third-party ML model or library is bundled. AI assistance was used to build this prototype; the algorithm implementation, examples and prose must be reviewed before publication. Contributions should retain transparent provenance, privacy and accessible alternatives. See CONTRIBUTING.md.

## Credits and license

Generated with assistance from Strawberry's Pupil Pete for Parteek Yadav. Python standard library: https://docs.python.org/3/library/ . Naive Bayes is a conventional public algorithm, implemented here from scratch; there is no pretrained external model to attribute. Entire project including synthetic dataset: MIT (LICENSE). Author/copyright wording can be revised by the owner before public release.

## Improved transparency and CI

Run `python evaluate.py` to reproduce the context-disjoint synthetic baseline diagnostic. Current synthetic-label matches: 16/27 model vs 12/27 majority baseline; this is NOT real-world accuracy. All identical input contexts are confined to one split. Same designer-generated distribution and repeated votes limit interpretation. No parameters were tuned on the holdout.

The single-result browser UI hides inputs once a plan is shown and encourages closing the tab. Optional explanation shows synthetic feature counts, an uncalibrated score and ranking margin. Printable offline prompts: docs/OFFLINE-CARDS.md.

.github/workflows/verify.yml prepares free public-repository GitHub Actions training, tests, synthetic evaluation, reproducibility check and evidence upload. Browser-aware verification succeeded: https://github.com/Parteek-yadav/touch-grass-planner/actions/runs/38038778132 . Training, 16 unit tests (including 112 actual Node/Python parity cases), five CLI scenarios, five loopback HTTP checks, synthetic evaluation, exact model reproducibility and evidence artifact upload passed on Ubuntu. Deployment succeeded after the same tests and exact bundle reproducibility gate: https://github.com/Parteek-yadav/touch-grass-planner/actions/runs/38038778111 . The browser adaptation is deployed separately to the live demo link above.

## Browser equivalence and testing

Python remains stdlib-only. To run the full verification suite (which now includes real browser-model parity), also have Node.js 18+ on PATH. No npm dependencies are used. `python build_site.py` bundles the actual saved Python parameters and activity definitions into `site/model-data.mjs`; the browser implementation is `site/planner.mjs`. `python -m unittest test_browser_parity -v` executes JavaScript under Node, comparing all fields and raw scores across 27 input contexts × unsafe/stationary modifiers: 108 valid cases plus four invalid inputs, numeric tolerance 1e-12. This proves implemented behavior matches the Python model; it does not validate synthetic recommendations in the real world.

The web app provides the same hard safety/stationary/time/park constraints, explicit model limitations and one-plan exit. The root index.html remains the optional Python-server UI; site/index.html is the functional static app. No service worker or claim of offline first-load support.

The Pages workflow runs the complete suite and checks exact model/bundle reproducibility before uploading only site/. Repository contents permission defaults to read; only the deployment job has pages:write and id-token:write. No credentials are embedded in site assets.

Live browser smoke checks verified ordinary, stationary-only and unsafe override scenarios on October 10, 2026. The observed browser resource list did not add inference requests after planner.mjs and model-data.mjs loaded. No outdoor field testing or fresh-load offline availability is claimed.
