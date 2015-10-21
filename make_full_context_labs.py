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

import argparse, sys, os, utterance, contexts, copy, context_skeletons, utterance_load, dictionary, io, phoneme_features
from datetime import datetime

#Parse an mlf into the lines of containing labels.
def parse_mlf(mlf, intype):
  if intype == "align_mlf":
    ext = ".rec"
  elif intype == "hts_mlf":
    ext = ".lab"
  else:
    print "Don't know what to do with mlf of type - {0}".format(intype)
  #Remove mlf header
  mlf.pop(0)
  labs = []
  tmp = []
  for l in mlf:
    tmp.append(l.split())
    if l == ".\n":
      if ext not in tmp[0][0]:
        print "Error: Something wrong with lab:\n"
        print tmp
        sys.exit()
      else:
        tmp[0] = tmp[0][0].split("*/")[1].split(".")[0]
        tmp.pop(-1)
      labs.append(tmp)
      tmp = []
  return labs

def read_stanford_parses(dirpath):
  files = [[x, open(os.path.join(dirpath, x), "r").read()] for x in os.listdir(dirpath) if ".parse" in x]
  pdct = {}
  for f in os.listdir(dirpath):
    if ".parse" in f:
      pdct[f[:-6]] = open(os.path.join(dirpath, f), "r").read().strip()
  return pdct

#Writes out a label context.
#If args.questions is true it returns a list of
#contexts for each phoneme to make questions about.
def write_context_utt(utt, args):
  wf = open(os.path.join(args.labdir, utt.id+".lab"), "w")
  if args.questions == True:
    cs = []
  for phone in utt.phonemes:
    if args.stanfordparse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanford(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanford(phone)
    else:
      if args.context_type == "relational":
        context = contexts.Relational(phone)
      elif args.context_type == "absolute":
        context = contexts.Absolute(phone)
    if args.questions == True:
      cs.append(context)
    wf.write(context.get_context_string(args.HHEd_fix))
    wf.write("\n")
  wf.close()
  #This is an odd way of doing it but it works.
  if args.questions == True:
    write_questions(cs, args)

def write_questions(context_set, args):
  if args.stanfordparse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanford(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanford(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  else:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.Relational(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
    elif args.context_type == "aboslute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.Absolute(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  for q in qs:
    args.qfile.write(q+"\n")
  for q in q_utt:
    args.qfileutt.write(q+"\n")

def finalise_questions(qpath):
  f = open(qpath, "r").readlines()
  f = list(set(f))
  f.sort()
  wf = open(qpath, "w")
  for x in f:
    wf.write(x)
  wf.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create full context labels from a variety of input.')
  parser.add_argument('intype', type=str, help='The type of input.', choices=['align_mlf', 'hts_mlf', 'hts_lab', 'txt'])
  parser.add_argument('-pron_reduced', type=str, nargs=2, help='Produce labels with a reduced pronunciation based on LM scores. REDUTCION_LEVEL should be a float between 1.0 (fully pronunced) and 0.0 (fully reduced).', metavar=('REDUCTION_LEVEL', 'LM_SCORE_DIR_PATH'))
  parser.add_argument('-inpath', type=str, help='The input path. The path to the mlf if that is the input. A dir path if labs as input.', default=None)
  parser.add_argument('-labdir', type=str, help="The output lab dir.", default="lab")
  parser.add_argument('-txtdir', type=str, help="The directory containing the original txt files.", default="txt")
  parser.add_argument('-combilexpath', type=str, help="The path to the combilex dictionary directory. It will look for two files - combilex.dict and combilex.add - and retrieve all entries from these.", default=None)
  parser.add_argument('-questions', action="store_true", help="Write out a question set fitting the input dataset.")
  parser.add_argument('-qpath', type=str, help="The directory to write the question set to.", default=os.path.join("questions", str(datetime.now())+".hed"))
  parser.add_argument('-target', type=str, help="The target type of the output labs and questions.", choices=['HMM', 'NN'], default='HMM')
  parser.add_argument('-stanfordparse', action="store_true", help="Add stanford parse information from parses in provided dirpath. Note this assumes you have already run txt2parse to create a parse.")
  parser.add_argument('-context_type', type=str, choices=['absolute', 'relational'], help="The type of positional contexts to add.", default='relational')
  parser.add_argument('-parsedir', type=str, help="The path to the parses.", default="parse")
  parser.add_argument('-HHEd_fix', action="store_true", help="Applies a fix to the contexts around the current phoneme to be compatible with hardcoded delimiters in HHEd.")
  args = parser.parse_args()
  
  #The phoneme set used - hardcoded as currently only combilex is possible
  args.phoneme_features = phoneme_features.CombilexPhonemes()
  
  #Check if this is well-formed
  if args.pron_reduced:
    if args.intype != "txt":
      print "Cannot make reduced pronunciation from non-textual input!"
      sys.exit()
    try:
      args.pron_reduced[0] = float(args.pron_reduced[0])
      if args.pron_reduced[0] > 1.0 or args.pron_reduced < 0.0:
        print "REDUCTION_LEVEL must be between 1.0 and 0.0! Was {0}".format(args.pron_reduced[0])
        sys.exit()
    except ValueError:
      print "REDUCTION_LEVEL must be a float value! Was {0}!".format(args.pron_reduced[0])
      sys.exit()
  
  
  if args.stanfordparse:
    args.parsedict = read_stanford_parses(args.parsedir)
  
  if args.intype == "txt":
    labs = io.load_txt_dir(args.txtdir)
    if args.combilexpath == None:
      print "No path to combilex. Please use -combilexpath option."
      sys.exit()
    args.dictionary = dictionary.Dictionary(args.combilexpath)
  elif args.intype == "hts_lab":
    labs = io.open_line_by_line(args.inpath)
    args.intype = "hts_mlf"
  else:
    if args.inpath == None:
      print "Input is mlf type but no mlf path has been set! Please use -inpath option."
      sys.exit()
    mlf = open(args.inpath, "r").readlines()
    labs = parse_mlf(mlf, args.intype)
  
  #Used if we make questions fitted to a dataset
  #We use qfile as the path to the file later.
  if args.questions == True:
    parser.add_argument('-qfile', type=str, help="A variable used to store the question file.", default=None)
    args.qfile = open(args.qpath, "w")
    parser.add_argument('-qfileutt', type=str, help="A variable used to store the GV question file.", default=None)
    args.qfileutt = open(args.qpath+"_utt", "w")
  
  for lab in labs:
    print "Making full context label for {0}".format(lab[0])
    #Make an utt
    utt = utterance.Utterance(lab, args)
    #This writes out the label and also the questions
    write_context_utt(utt, args)
  
  #Removes duplicates in the question set
  if args.questions:
    args.qfile.close()
    finalise_questions(args.qpath)
    args.qfileutt.close()
    finalise_questions(args.qpath+"_utt")
