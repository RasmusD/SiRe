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
import argparse, os, utterance, contexts, copy, context_skeletons, dictionary, phoneme_features
import sire_io as io
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
#Actually it could be useful to let contexts sort this out. See TODO
def write_context_utt(utt, args):
  wf = open(os.path.join(args.labdir, utt.id+".lab"), "w")
  if args.questions == True:
    cs = []
  for phone in utt.phonemes:
    if args.stanford_pcfg_parse == True and args.stanford_dependency_parse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanfordCombined(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanfordCombined(phone)
      elif args.context_type == "categorical":
        context = contexts.CategoricalStanfordCombined(phone)
    elif args.stanford_pcfg_parse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanfordPcfg(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanfordPcfg(phone)
      elif args.context_type == "categorical":
        context = contexts.CategoricalStanfordPcfg(phone)
    elif args.stanford_dependency_parse == True:
      if args.context_type == "relational":
        context = contexts.RelationalStanfordDependency(phone)
      elif args.context_type == "absolute":
        context = contexts.AbsoluteStanfordDependency(phone)
      elif args.context_type == "categorical":
        context = contexts.CategoricalStanfordDependency(phone)
    elif args.emphasis == True:
        if args.context_type == "absolute":
            context = contexts.Emphasis(phone)
        elif args.context_type != "absolute":
            print "Emphasis features can only be used with the Absolute context type."
    else:
      if args.context_type == "relational":
          context = contexts.Relational(phone)
      elif args.context_type == "absolute":
          context = contexts.Absolute(phone)
      elif args.context_type == "categorical":
        context = contexts.Categorical(phone)
    if args.questions == True:
      cs.append(context)
    if args.labtype == "Phone":
      wf.write(context.get_context_string(args.HHEd_fix))
    elif args.labtype == "AlignState":
      base_string = context.get_context_string(args.HHEd_fix).split()
      if phone.states:
        if len(phone.states) != 5:
          raise SiReError("Wrong number of states for phone {0}!".format(phone.id))
        #S2
        wf.write(phone.states[0][0]+" "+phone.states[0][1]+" "+base_string[-1]+"[2] "+base_string[-1]+"\n")
        #S3
        wf.write(phone.states[1][0]+" "+phone.states[1][1]+" "+base_string[-1]+"[3]\n")
        #S4
        wf.write(phone.states[2][0]+" "+phone.states[2][1]+" "+base_string[-1]+"[4]\n")
        #S5
        wf.write(phone.states[3][0]+" "+phone.states[3][1]+" "+base_string[-1]+"[5]\n")
        #S6
        wf.write(phone.states[4][0]+" "+phone.states[4][1]+" "+base_string[-1]+"[6]")
      else:
        print SiReError("No states in phone {0}! Faking phone states is not a feature currently.".format(phone.id))
    else:
      raise SiReError("Invalid labtype {0}!")
    wf.write("\n")
  wf.close()
  #This is an odd way of doing it but it works.
  if args.questions == True:
    write_questions(cs, args)

def write_questions(context_set, args):
  if args.stanford_pcfg_parse == True and args.stanford_dependency_parse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanfordCombined(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanfordCombined(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "categorical":
      qs, q_utt = contexts.get_question_sets(context_skeletons.CategoricalStanfordCombined(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
  elif args.stanford_pcfg_parse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanfordPcfg(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanfordPcfg(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "categorical":
      qs, q_utt = contexts.get_question_sets(context_skeletons.CategoricalStanfordPcfg(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
  elif args.stanford_dependency_parse == True:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.RelationalStanfordDependency(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.AbsoluteStanfordDependency(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "categorical":
      qs, q_utt = contexts.get_question_sets(context_skeletons.CategoricalStanfordDependency(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
  else:
    if args.context_type == "relational":
      qs, q_utt = contexts.get_question_sets(context_skeletons.Relational(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "absolute":
      qs, q_utt = contexts.get_question_sets(context_skeletons.Absolute(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
    elif args.context_type == "categorical":
      qs, q_utt = contexts.get_question_sets(context_skeletons.Categorical(args.phoneme_features), args.qtype, True, context_set, args.HHEd_fix)
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
  parser.add_argument('intype', type=str, help='The type of input.', choices=['align_mlf', 'hts_mlf', 'hts_lab', 'txt', 'sire_lab', 'state_align_mlf'])
  parser.add_argument('labdir', type=str, help="The output lab dir.")
  parser.add_argument('inpath', type=str, help='The input path. The path to the mlf if that is the input. A dir path if labs or txt as input.')
  parser.add_argument('txtdir', type=str, help="The directory containing the original txt files. If producing input from txt this is set to equal INPATH and is technically superfluous, but necessary for other contexts.")
  parser.add_argument('-dict', type=str, nargs=2, help="The path to the dictionary.", default=None, metavar=["DICTTYPE", "DICTPATH"])
  parser.add_argument('-phoneset', type=str, help="The phoneset to use - combilex or cmudict. Is overwritten to fit the dictionary if one is used.", default="combilex", choices=["combilex", "cmudict"])
  parser.add_argument('-questions', action="store_true", help="Write out a question set fitting the input dataset.")
  parser.add_argument('-qpath', type=str, help="The path to write the question set to. Default is \"questions/DATETIMENOW.hed\".", default=os.path.join("questions", str(datetime.now())+".hed"))
  parser.add_argument('-qtype', type=str, help="The target type of the output questions.", choices=['HMM', 'Nitech_NN', 'CSTR_NN'], default='HMM')
  parser.add_argument('-labtype', type=str, help="The target type of the output labels.", choices=['Phone', 'AlignState'], default='Phone')
  parser.add_argument('-stanford_pcfg_parse', action="store_true", help="Add stanford pcfg parse information from parses in provided dirpath. Note this assumes you have already run txt2parse to create a parse.")
  parser.add_argument('-stanford_dependency_parse', action="store_true", help="Add stanford dependency parse information from parses in provided dirpath. Note this assumes you have already run txt2parse to create a parse.")
  parser.add_argument('-context_type', type=str, choices=['absolute', 'relational', 'categorical'], help="The type of positional contexts to add.", default='absolute')
  parser.add_argument('-parsedir', type=str, help="The path to the parses.", default="parse")
  parser.add_argument('-HHEd_fix', action="store_true", help="Applies a fix to the contexts around the current phoneme to be compatible with hardcoded delimiters in HHEd.")
  parser.add_argument('-comma_is_pause', action='store_true', help="If making labs from txt, commas mark where to pause and so we should pause.")
  parser.add_argument('-general_sil_phoneme', type=str, help="If making labs from txt, use this as the silence phoneme.", default="sil")
  parser.add_argument('-emphasis', action="store_true", help="If using a corpus emphasis tagged via all capital letters, use this to add emphasis features")
  parser.add_argument('-state_level', action="store_true", help="If the input labels are state aligned. Uses HTK 3.5 labels.")
  #A few mutually exclusive groups
  #TODO should be more
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-pron_reduced', type=str, nargs=2, help='Produce labels with a reduced pronunciation based on word level LM scores. REDUCTION_LEVEL should be a float between 1.0 (fully pronunced) and 0.0 (fully reduced).', metavar=('REDUCTION_LEVEL', 'LM_SCORE_DIR_PATH'))
  group.add_argument('-pron_phoneme_lm', type=str, help='Produce labels with a pronunciation based on phoneme level LM scores. LM_SCORE_DIR_PATH is the path to the stored best paths.', metavar=('LM_SCORE_DIR_PATH'))
  args = parser.parse_args()

  #Just a check - argparse does not have mutually inclusive groups.
  if args.pron_reduced or args.pron_phoneme_lm:
    if args.intype != "txt":
      raise SiReError("If producing LM based pronunciations you must be making utterances from text!")

  #The phoneme set used
  if args.phoneset == "combilex":
    args.phoneme_features = phoneme_features.CombilexPhonemes()
  else:
    args.phoneme_features = phoneme_features.CMUPhonemes()
  #We use festival features always - hardcoded here as we want them in all full-context labs but not in e.g. corpus analysis
  args.festival_features = True

  #We can't use commas as pause if we are not creating labs from text.
  if args.comma_is_pause and args.intype != "txt":
    raise SiReError("It makes no sense to insert pauses at commas when you already have the pauses from the alignment or labs!")

  #Check if this is well-formed
  if args.pron_reduced:
    if args.intype != "txt":
      raise SiReError("Cannot make reduced pronunciation from non-textual input!")
    try:
      args.reduction_level = float(args.pron_reduced[0])
      args.lm_score_dir = args.pron_reduced[1]
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
    if args.dict == None:
      raise SiReError("No path to dictionary. Please use -dict option.")
    args.dictionary = dictionary.Dictionary(args.dict[1], args.dict[0])
    #The phoneme set used must match the dictionary.
    args.phoneme_features = args.dictionary.phoneme_feats
  elif args.intype == "hts_lab":
    labs = io.open_labdir_line_by_line(args.inpath)
    # print "This is a lab", len(labs[0])
    # labs is a list of lists. Each list within the list of one of the labs
    args.intype = "hts_mlf"
  elif args.intype == "sire_lab":
    labs = io.open_labdir_line_by_line(args.inpath)
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
    # print "The lab sent in", lab
    utt = utterance.Utterance(lab, args)
    #This writes out the label and also the questions
    write_context_utt(utt, args)

  #Removes duplicates in the question set
  if args.questions:
    args.qfile.close()
    finalise_questions(args.qpath)
    args.qfileutt.close()
    finalise_questions(args.qpath+"_utt")
