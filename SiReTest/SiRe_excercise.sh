#!/bin/bash
##########################################################################
#Copyright 2015 Rasmus Dall                                              #
#                                                                        #
#Licensed under the Apache License, Version 2.0 (the "License");         #
#you may not use this file except in compliance with the License.        #
#You may obtain a copy of the License at                                 #
#                                                                        #
#http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                        #
#Unless required by applicable law or agreed to in writing, software     #
#distributed under the License is distributed on an "AS IS" BASIS,       #
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
#See the License for the specific language governing permissions and     #
#limitations under the License.                                          #
##########################################################################

#This script excercises the most common parts of SiRe.
#If it runs fine there is a high likelihood that SiRe works as intended.
#IT IS NO GUARANTEE HOWEVER!!!
#A number of tests at the end requires manual setting of a few paths - they do not run as standard.
#To run them pass "all" as the first argument when running this script.

#Make sure we work in the directory that this script is in. We expect this to be a subdir in the SiRe folder structure.
cd "$(dirname $(readlink -f $0))"

#Set up
mkdir outputs
mkdir outputs/labs
mkdir outputs/questions

#Excercise SiRe
#From align_mlf
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -HHEd_fix
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -HHEd_fix -context_type absolute
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -questions -qpath outputs/questions/test -HHEd_fix
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -questions -qpath outputs/questions/test -HHEd_fix -context_type absolute
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -questions -qpath outputs/questions/test -HHEd_fix -target NN
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -questions -qpath outputs/questions/test -HHEd_fix -context_type absolute -target NN

#Parsing - there are more combinations but this should suffice
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -txtdir inputs/txt/ -stanford_pcfg_parse -parsedir inputs/parse/
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -txtdir inputs/txt/ -stanford_dependency_parse -parsedir inputs/parse/
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -txtdir inputs/txt/ -stanford_pcfg_parse -parsedir inputs/parse/ -context_type absolute
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -txtdir inputs/txt/ -stanford_dependency_parse -parsedir inputs/parse/ -context_type absolute
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -txtdir inputs/txt/ -stanford_pcfg_parse -parsedir inputs/parse/ -context_type absolute -questions -qpath outputs/questions/test -HHEd_fix
python ../make_full_context_labs.py align_mlf outputs/labs inputs/align.mlf -txtdir inputs/txt/ -stanford_dependency_parse -parsedir inputs/parse/ -questions -qpath outputs/questions/test -HHEd_fix

#We start assuming things like -HHEd_fix just works to reduce number of runs

#From hts_mlf
python ../make_full_context_labs.py hts_mlf outputs/labs inputs/hts.mlf -questions -qpath outputs/questions/test -HHEd_fix -context_type absolute

#From hts_labs
python ../make_full_context_labs.py hts_lab outputs/labs inputs/HTS_Lab -questions -qpath outputs/questions/test -HHEd_fix -context_type absolute

#THE FOLLOWING EXCERCISES NEED YOU TO HAVE COMBILEX AND SET A THE PATH TO IT YOURSELF!!!
#From txt
if [ "$1" != "all" ]
then
  echo "Skipping final tests..."
  rm -r outputs
  exit
fi
COMBILEXPATH=/work/rasmus/SiRe/combilex
python ../make_full_context_labs.py txt outputs/labs inputs/txt -combilexpath $COMBILEXPATH
python ../make_full_context_labs.py txt outputs/labs inputs/txt -combilexpath $COMBILEXPATH -comma_is_pause
python ../make_full_context_labs.py txt outputs/labs inputs/txt -combilexpath $COMBILEXPATH -context_type absolute
python ../make_full_context_labs.py txt outputs/labs inputs/txt -questions -qpath outputs/questions/test -combilexpath $COMBILEXPATH
python ../make_full_context_labs.py txt outputs/labs inputs/txt -questions -qpath outputs/questions/test -combilexpath $COMBILEXPATH -context_type absolute

#Clean up
rm -r outputs
