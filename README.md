# SiRe
(Si)mply a (Re)search front-end for Text-To-Speech Synthesis.

This is a research front-end for TTS. It is incomplete, inconsistent, badly coded and slow.

But it is useful for me and should slowly develop into something useful to others.

If you try it out, here is what it can do:

- Load standard HTS (2.3beta) full-context mlfs and convert them to two other linguistic feature sets.
- Output a relational and parsed linguistic featureset.
- Output a standard absolute linguistic set and a parsed version of this.
- Output labels suitable to work with HMM (HTS 2.3beta) and DNN (HTS NN 2.3alpha) systems.
- Output a question set consistent with the linguistic features encountered in training data for both HMM and DNN.
- Merge question sets.
- It should be easy to define a new linguistic feature context set allowing for rapid experimentation.
- Load an mlf created from alignment using the multisyn tools and create full-context labels.
- Load txt, if you also have the combilex dictionary, files and create full-context labels.
- Create mlfs and slfs suitable for alignment using the CSTR Festival multisyn tools.
- Interface with the Stanford parser to create a parse usable for context labelling.
- Use NGRAM statistics for pronunciation reduction.
- More to come... see TODO

How to make it work:
- You need python 2.7+, lower may work if you have the argparse module installed (developed on 2.7.3 which has it by default)
- The main workhorse is the make_*.py files - run them with -h to see what to specify.
- It SHOULD print lots of warnings or errors if something fishy is going on.
- Any bugs please report to rasmus@dall.dk - I am happy to receive them and provide any support asap.

Comments, suggestions, requests:
- Please send to rasmus@dall.dk and I will consider them asap.

Implemented a new module/improved an old?
- Just make a pull request and I will incorporate it.
- Or mail me at rasmus@dall.dk with the code and I will merge it.


#Copyright 2015 Rasmus Dall

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
