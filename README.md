# SiRe
(Si)mply a (Re)search front-end for Text-To-Speech Synthesis.

This is a research front-end for TTS. It is incomplete, inconsistent, badly coded and slow.

But it is useful for me and should slowly develop into something useful to others.

NOTE: I aim to soon add some simple instructions/documentation to show of how to use SiRe. The test script in SiReTest currently can serve as an example for label generation.

If you try it out, here is what it can do (also see some papers further down which has used this tool):

- Load standard HTS (2.3beta for sure, but should work with most) and convert them to several other linguistic feature sets (see below).
- Load an mlf created from alignment using the Festival multisyn tools/HTK and create full-context labels.
- Load txt, if you also have the combilex or cmudict dictionary, files and create full-context labels.
- Output a feature set equivalent to Festival/Flite
- Output feature sets using three positional segment representations: absolute, relational and categorical.
- Output the above feature sets with features added based on PCFG and/or Dependency parsing from the stanford parser. (Paper under review showing effect of parsing features and different positional representations currently uner review - draft available upon request)
- Output labels suitable to work with HMM (HTS 2.3beta) and DNN (HTS NN 2.3alpha and CSTR's Merlin) systems.
- Output a question set consistent with the linguistic features encountered in training data for both HMM and DNN.
- Merge question sets.
- It should be easy to define a new linguistic feature context set allowing for rapid experimentation.
- Create mlfs and slfs suitable for alignment using the Festival multisyn tools or HTK.
- Do some corpus analysis and assorted simple tools including syllabifying cmuDict for use with SiRe.
- Use NGRAM statistics for pronunciation reduction.
- More to come... see TODO

How to make it work:
- You need python 2.7+, lower may work if you have the argparse module installed (developed on 2.7.3 which has it by default)
- Visualisation tools and plots by corporautils need matplotlib in addition.
- The main workhorse is the make_*.py files - run them with -h to see what to specify.
- It SHOULD print lots of warnings or errors if something fishy is going on.
- Any bugs please report to rasmus@dall.dk - I am happy to receive them and provide any support asap.
- Run the script in SiReTest to check that all works (not a complete guarantee).

Directories:
- SiReCore contains the core elements of SiRe.
- SiReData contains scripts to manipulate data and txt files.
- SiReTest contains a script and files to excercise the most important aspects of SiRe.
- SiReUtils contains utility scripts not central to SiRe.

Comments, suggestions, requests:
- Please send to rasmus@dall.dk and I will consider them asap.

Implemented a new module/improved an old?
- Just make a pull request and I will incorporate it.
- Or mail me at rasmus@dall.dk with the code and I will merge it.

Papers published utilising SiRe:
- Dall, R., Hashimoto, K., Oura, K., Nankaku, Y. and Tokuda, K. (2016). Redefining the Linguistic Context Feature Set for HMM and DNN TTS Through Position and Parsing. In Proc. Interspeech, San Francisco, USA. 

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
