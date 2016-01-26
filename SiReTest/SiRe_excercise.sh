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

#Make sure we work in the directory that this script is in.
if [ "${PWD##*/}" != "SiReTest" ]
then
  echo "Not in test directory!"
  exit
fi

#Then one up should be the SiRe directory
cd ..

#Set up
mkdir SiReTest/outputs
mkdir SiReTest/outputs/labs
mkdir SiReTest/outputs/questions

#Excercise SiRe
#From align_mlf
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -HHEd_fix || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -HHEd_fix -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -HHEd_fix -context_type categorical || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix -context_type categorical || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix -target NN || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix -context_type absolute -target NN || { echo "Error at line: ${LINENO}"; exit 1; }

#Parsing - there are more combinations but this should suffice
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_pcfg_parse -parsedir SiReTest/inputs/parse/ || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_dependency_parse -parsedir SiReTest/inputs/parse/ || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_pcfg_parse -parsedir SiReTest/inputs/parse/ -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_dependency_parse -parsedir SiReTest/inputs/parse/ -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_pcfg_parse -parsedir SiReTest/inputs/parse/ -context_type absolute -questions -qpath SiReTest/outputs/questions/test -HHEd_fix || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_dependency_parse -parsedir SiReTest/inputs/parse/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py align_mlf SiReTest/outputs/labs SiReTest/inputs/align.mlf SiReTest/inputs/txt/ -stanford_dependency_parse -stanford_pcfg_parse -parsedir SiReTest/inputs/parse/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix || { echo "Error at line: ${LINENO}"; exit 1; }

#We start assuming things like -HHEd_fix just works to reduce number of runs

#From hts_mlf
python make_full_context_labs.py hts_mlf SiReTest/outputs/labs SiReTest/inputs/hts.mlf SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }

#From hts_labs
python make_full_context_labs.py hts_lab SiReTest/outputs/labs SiReTest/inputs/HTS_Lab SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -HHEd_fix -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }

#THE FOLLOWING EXCERCISES NEED YOU TO HAVE COMBILEX AND SET A THE PATH TO IT YOURSELF!!!
#From txt
if [ "$1" != "all" ]
then
  echo "Skipping final tests..."
  rm -r SiReTest/outputs
  exit
fi
COMBILEXPATH=/Users/RasmusDall/SiRe/combilex
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -combilexpath $COMBILEXPATH || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -combilexpath $COMBILEXPATH -comma_is_pause || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -combilexpath $COMBILEXPATH -comma_is_pause -stanford_dependency_parse -parsedir SiReTest/inputs/parse || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -combilexpath $COMBILEXPATH -comma_is_pause -stanford_pcfg_parse -parsedir SiReTest/inputs/parse || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -combilexpath $COMBILEXPATH -comma_is_pause -stanford_pcfg_parse -stanford_dependency_parse -parsedir SiReTest/inputs/parse || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -combilexpath $COMBILEXPATH -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -combilexpath $COMBILEXPATH || { echo "Error at line: ${LINENO}"; exit 1; }
python make_full_context_labs.py txt SiReTest/outputs/labs SiReTest/inputs/txt SiReTest/inputs/txt/ -questions -qpath SiReTest/outputs/questions/test -combilexpath $COMBILEXPATH -context_type absolute || { echo "Error at line: ${LINENO}"; exit 1; }


#Clean up
rm -r SiReTest/outputs
