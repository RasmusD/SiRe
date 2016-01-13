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

#Load the SiReImports.pth file
import site
site.addsitedir(".")

#Rest of imports
import argparse, os, utterance, contexts, copy, context_skeletons, utterance_load, dictionary, phoneme_features
import SiReIO as io
from datetime import datetime
from error_messages import SiReError

def read_stanford_pcfg_parses(dirpath):
  pdct = {}
  for f in os.listdir(dirpath):
    if ".parse" in f:
      pdct[f[:-6]] = open(os.path.join(dirpath, f), "r").read().strip()
  return pdct

def read_stanford_dependency_parses(dirpath):
  pdct = {}
  for f in os.listdir(dirpath):
    if ".relations" in f:
      pdct[f.split(".rel")[0]] = io.open_file_line_by_line(os.path.join(dirpath, f))
  return pdct

#Writes out a label context.
#If args.questions is true it returns a list of
#contexts for each phoneme to make questions about.
def write_context_utt(utt, args):
  wf = open(os.path.join(args.labdir, utt.id+".lab"), "w")
  if args.questions == True:
    cs = []
  for phone in utt.phonemes:
    if args.festival_features == True:
      context = contexts.Festival(phone)
    elif args.context_type == "categorical":
      context = contexts.Categorical(phone)
    elif args.stanford_pcfg_parse == True and args.stanford_dependency_parse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanfordCombined(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanfordCombined(phone)
    elif args.stanford_pcfg_parse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanfordPcfg(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanfordPcfg(phone)
    elif args.stanford_dependency_parse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanfordDependency(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanfordDependency(phone)
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
  if args.festival_features == True:
    qs, q_utt = contexts.get_question_sets(context_skeletons.Festival(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  elif args.context_type == "categorical":
    qs, q_utt = contexts.get_question_sets(context_skeletons.Categorical(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  elif args.stanford_pcfg_parse == True and args.stanford_dependency_parse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanfordCombined(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanfordCombined(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  elif args.stanford_pcfg_parse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanfordPcfg(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanfordPcfg(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  elif args.stanford_dependency_parse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanfordDependency(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanfordDependency(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
  else:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.Relational(args.phoneme_features), args.target, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
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
  parser.add_argument('labdir', type=str, help="The output lab dir.")
  parser.add_argument('inpath', type=str, help='The input path. The path to the mlf if that is the input. A dir path if labs or txt as input.')
  parser.add_argument('-pron_reduced', type=str, nargs=2, help='Produce labels with a reduced pronunciation based on LM scores. REDUTCION_LEVEL should be a float between 1.0 (fully pronunced) and 0.0 (fully reduced).', metavar=('REDUCTION_LEVEL', 'LM_SCORE_DIR_PATH'))
  parser.add_argument('-txtdir', type=str, help="The directory containing the original txt files. If producing input from txt this is set to equal INPATH and does not need to be set.", default="txt")
  parser.add_argument('-combilexpath', type=str, help="The path to the combilex dictionary directory. It will look for two files - combilex.dict and combilex.add - and retrieve all entries from these.", default=None)
  parser.add_argument('-questions', action="store_true", help="Write out a question set fitting the input dataset.")
  parser.add_argument('-qpath', type=str, help="The path to write the question set to. Default is \"questions/DATETIMENOW.hed\".", default=os.path.join("questions", str(datetime.now())+".hed"))
  parser.add_argument('-target', type=str, help="The target type of the output labs and questions.", choices=['HMM', 'NN'], default='HMM')
  parser.add_argument('-stanford_pcfg_parse', action="store_true", help="Add stanford pcfg parse information from parses in provided dirpath. Note this assumes you have already run txt2parse to create a parse.")
  parser.add_argument('-stanford_dependency_parse', action="store_true", help="Add stanford dependency parse information from parses in provided dirpath. Note this assumes you have already run txt2parse to create a parse.")
  parser.add_argument('-festival_features', action="store_true", help="Outputs a set of features equivalent to that produced by Festival for HTS. Note this will take precedence over the -stanford_pcfg_parse option which in that case will provide the POS tags instead of using the simple_festival_pos_predict method. It will also ignore the -context_type flag and always use absolute values.")
  parser.add_argument('-context_type', type=str, choices=['absolute', 'relational', 'categorical'], help="The type of positional contexts to add.", default='relational')
  parser.add_argument('-parsedir', type=str, help="The path to the parses.", default="parse")
  parser.add_argument('-HHEd_fix', action="store_true", help="Applies a fix to the contexts around the current phoneme to be compatible with hardcoded delimiters in HHEd.")
  parser.add_argument('-comma_is_pause', action='store_true', help="If making labs from txt, commas mark where to pause and so we should pause.")
  parser.add_argument('-general_sil_phoneme', type=str, help="If making labs from txt, use this as the silence phoneme.", default="sil")
  args = parser.parse_args()
  
  #The phoneme set used - hardcoded as currently only combilex is possible.
  args.phoneme_features = phoneme_features.CombilexPhonemes()
  
  #We can't use commas as pause if we are not creating labs from text.
  if args.comma_is_pause and args.intype != "txt":
    raise SiReError("It makes no sense to insert pauses at commas when you already have the pauses from the alignment or labs!")
  
  #We make sure we do the right context_type if Festival labs are produced
  if args.festival_features == True:
    args.context_type = 'absolute'
  
  #Check if this is well-formed
  if args.pron_reduced:
    if args.intype != "txt":
      raise SiReError("Cannot make reduced pronunciation from non-textual input!")
    try:
      args.reduction_level = float(args.pron_reduced[0])
      args.reduction_score_dir = args.pron_reduced[1]
      if args.reduction_level > 1.0 or args.reduction_level < 0.0:
        raise SiReError("REDUCTION_LEVEL must be between 1.0 and 0.0! Was {0}".format(args.pron_reduced[0]))
      else:
        args.reduction_level = float(args.pron_reduced[0])
      args.pron_reduced = True
    except ValueError:
      raise SiReError("REDUCTION_LEVEL must be a float value! Was {0}!".format(args.pron_reduced[0]))
  else:
    args.pron_reduced = False
  
  if args.stanford_pcfg_parse:
    args.pcfgdict = read_stanford_pcfg_parses(args.parsedir)
  
  if args.stanford_dependency_parse:
    args.dependencydict = read_stanford_dependency_parses(args.parsedir)
  
  
  if args.intype == "txt":
    if not os.path.isdir(args.inpath):
      raise SiReError("Input path is not a directory! It must be when creating labs from text.")
    args.txtdir = args.inpath
    labs = io.load_txt_dir(args.txtdir, args.comma_is_pause)
    if args.combilexpath == None:
      raise SiReError("No path to combilex. Please use -combilexpath option.")
    elif not os.path.isdir(args.combilexpath):
        raise SiReError("Combilex path is not valid ({0}).\nPlease specify the dir in which the combilex.dict and .add files are.".format(args.combilexpath))
    args.dictionary = dictionary.Dictionary(args.combilexpath)
    #The phoneme set used must match the dictionary - currently pointless as only combilex is possible and this is hardcoded above. But here for the future.
    args.phoneme_features = args.dictionary.phoneme_feats
  elif args.intype == "hts_lab":
    labs = io.open_labdir_line_by_line(args.inpath)
    args.intype = "hts_mlf"
  else:
    if not os.path.exists(args.inpath):
      raise SiReError("Input path to mlf does no exist!")
    mlf = open(args.inpath, "r").readlines()
    labs = io.parse_mlf(mlf, args.intype)
  
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
