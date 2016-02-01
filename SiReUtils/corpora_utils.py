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

import argparse, dictionary, utterance

from error_messages import SiReError
from check_dictionary import get_oov_words
from sire_io import open_writefile_safe
from sire_io import load_txt_dir

def count_words(txt):
  n_words = 0
  for t in txt:
    n_words += len(t[1:])
  return n_words

def get_utts(txt, args):
  utts = []
  for t in txt:
    utts.append(utterance.Utterance(t, args))
  return utts

def get_phoneme_count(utts):
  n_phonemes = 0
  n_phonemes_no_sil = 0
  for utt in utts:
    #Add full amount
    n_phonemes += utt.num_phonemes()
    #Without silence/pau
    n_phonemes_no_sil += utt.num_phonemes_no_pau()
  return n_phonemes, n_phonemes_no_sil

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Checks a TTS corpora for various statistics.')
  parser.add_argument('indir', type=str, help='The input dir of txt files.')
  parser.add_argument('combilexpath', type=str, help='The path to the directory containing combilex.')
  parser.add_argument('-outfile', type=str, help='The output filepath if stats should be written out.')
  args = parser.parse_args()
  
  txt = load_txt_dir(args.indir)
  
  dct = dictionary.Dictionary(args.combilexpath)
  
  outstr = "\nCorpora details\n\n"
  
  if args.outfile:
    wf = open_writefile_safe(args.outfile)
  
  n_words = count_words(txt)
  
  outstr += "Number of words:\n"
  outstr += str(n_words)+"\n\n"
  
  oov = get_oov_words(txt, dct)
  
  outstr += "Number of OOV words:\n"
  outstr += str(len(oov))+"\n\n"
  
  if len(oov) != 0:
    print "Please remove all OOV word containing sents or add the words to dictonary before proceeding."
    for w in oov:
      print w
    raise SiReError("OOV words present, cannot continue.")
  
  args.dictionary = dct
  args.intype = "txt"
  utts = get_utts(txt, args)
  
  n_phonemes, n_phonemes_no_sil = get_phoneme_count(utts)
  
  outstr += "Number of phonemes (from txt):\n"
  outstr += str(n_phonemes)+"\n\n"
  
  outstr += "Number of silence/pause phonemes (from txt):\n"
  outstr += str(n_phonemes - n_phonemes_no_sil)+"\n\n"
  
  print outstr
  
  if args.outfile:
    wf.write(outstr)
    wf.close()
