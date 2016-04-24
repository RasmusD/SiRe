##########################################################################
#Copyright 2016 Rasmus Dall                                              #
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

#This contains a number of things for investigating a TTS corpus. E.g. a count for the number of triphoneme types in the corpus.

#Load the SiReImports.pth file
import site
site.addsitedir(".")

import argparse, dictionary, utterance, sire_io

from error_messages import SiReError
from check_dictionary import get_oov_words
from sire_io import open_writefile_safe
from sire_io import load_txt_dir

def get_utts(txt, args):
  utts = []
  for t in txt:
    utts.append(utterance.Utterance(t, args))
  return utts

def analyse_text_corp(indir, compilexpath):
  txt = load_txt_dir(indir)
  
  dct = dictionary.Dictionary(compilexpath)
  
  oov = get_oov_words(txt, dct)
  
  if len(oov) != 0:
    print "Please remove all OOV word containing sents or add the words to dictonary before proceeding."
    for w in oov:
      print w
    raise SiReError("OOV words present, cannot continue.")
  
  args.dictionary = dct
  args.intype = "txt"
  utts = get_utts(txt, args)
  
  do_analysis(utts)

def analyse_sire_lab(labdir, context_type, hhed_fix, dictionarypath):
  labs = sire_io.open_labdir_line_by_line(labdir)
  quinphone = []
  phone = []
  triphone = []
  args.intype = "sire_lab"
  args.context_type = context_type
  args.HHEd_fix = hhed_fix
  args.dictionary = dictionary.Dictionary(dictionarypath)
  #As we do not require the input text to analyse from a sire_lab we need to disable the festival features
  args.festival_features = False
  utts = get_utts(labs, args)
  do_analysis(utts)

def do_analysis(utts):
  outstr = ""
  #Phone numbers
  quinphone = []
  phone = []
  triphone = []
  n_words = 0
  sil_phones = []
  #Corpus duration numbers
  totaldur = 0
  sildur = 0
  #For disfluencies
  uhdur = 0
  num_uh = 0
  umdur = 0
  num_um = 0
  for utt in utts:
    n_words += utt.num_words_no_pau()
    #Phone level information
    for p in utt.phonemes:
      llp = p.get_left_left_phoneme().id
      lp = p.get_left_phoneme().id
      cp = p.id
      rp = p.get_right_phoneme().id
      rrp = p.get_righ_right_phoneme().id
      quinphone.append((llp, lp, cp, rp, rrp))
      triphone.append((lp, cp, rp))
      phone.append(cp)
      if p.id in ["pau", "sil"]:
        sil_phones.append(p)
        sildur += p.get_duration()
      totaldur += p.get_duration()
    #Word level information
    for word in utt.words:
      if word.id in ["V"]:
        num_uh += 1
        uhdur += word.get_duration()
      if word.id in ["Vm"]:
        num_um += 1
        umdur += word.get_duration()
  
  outstr = "\nCorpora details\n\n"
  
  outstr += "Number of words:\n"
  outstr += str(n_words)+"\n\n"
  
  quinphone = set(quinphone)
  triphone = set(triphone)
  outstr += "Number of phones\n"
  num_phones = len(phone)
  outstr += str(num_phones)+"\n\n"
  outstr += "number of unique quinphones\n"
  outstr += str(len(quinphone))+"\n\n"
  outstr += "Number of unique triphones\n"
  outstr += str(len(triphone))+"\n"
  outstr += "Silence Phones\n\n"
  num_sil = len(sil_phones)
  outstr += str(num_sil)+"\n\n"
  outstr += "Silence Quinphone Types\n"
  outstr += str(len([x for x in quinphone if x[2] in ["pau", "sil"]]))+"\n\n"
  outstr += "Silence Triphones Types\n"
  outstr += str(len([x for x in triphone if x[1] in ["pau", "sil"]]))+"\n\n"
  outstr += "Number of Uhs\n"
  outstr += str(num_uh)+"\n\n"
  outstr += "Number of Ums\n"
  outstr += str(num_um)+"\n\n"
  
  #Find Total Corpora Size
  outstr += "Total duration of corpus (s)\n"
  outstr += str(totaldur/10000000)+"\n\n"
  outstr += "Total duration of corpus (min)\n"
  outstr += str(totaldur/10000000/60)+"\n\n"
  outstr += "Total sil duration in corpus (s)\n"
  outstr += str(sildur/10000000)+"\n\n"
  outstr += "Total sil duration in corpus (min)\n"
  outstr += str(sildur/10000000/60)+"\n\n"
  outstr += "Total uh duration in corpus (s)\n"
  outstr += str(uhdur/10000000)+"\n\n"
  outstr += "Total uh duration in corpus (min)\n"
  outstr += str(uhdur/10000000/60)+"\n\n"
  outstr += "Total um duration in corpus (s)\n"
  outstr += str(umdur/10000000)+"\n\n"
  outstr += "Total um duration in corpus (min)\n"
  outstr += str(umdur/10000000/60)+"\n\n"
  
  #Phone dur stats
  outstr += "Mean phone duration in corpus (ms)\n"
  outstr += str(totaldur/10000/num_phones)+"\n\n"
  outstr += "Mean sil duration in corpus (ms)\n"
  outstr += str(sildur/10000/num_sil)+"\n\n"
  outstr += "Mean uh duration in corpus (ms)\n"
  outstr += str(uhdur/10000/num_uh)+"\n\n"
  outstr += "Mean um duration in corpus (ms)\n"
  outstr += str(umdur/10000/num_um)+"\n\n"
  
  
  print outstr

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Checks a TTS corpora for various statistics.')
  parser.add_argument('-txt_analysis', nargs=2, help='Perform an analysis of a corpora from text files.', metavar=('INDIRPATH', 'COMBILEXPATH'))
  parser.add_argument('-lab_analysis', nargs=4, help='Perform an analysis based on SiRe style full context labels.', metavar=('LABDIRPATH', 'CONTEXTTYPE', 'HHEDFIX', 'COMBILEXPATH'))
  parser.add_argument('-outfile', type=str, help='The output filepath if stats should be written out.')
  args = parser.parse_args()
  
  if args.txt_analysis != None:
    analyse_text_corp(args.txt_analysis[0], args.txt_analysis[1])
  
  if args.lab_analysis != None:
    analyse_sire_lab(args.lab_analysis[0], args.lab_analysis[1], bool(args.lab_analysis[2]), args.lab_analysis[3])

