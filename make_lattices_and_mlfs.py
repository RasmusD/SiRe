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

#Methods for writing out the necessary files for forced alignment.

#Load the SiReImports.pth file
import site
site.addsitedir(".")

#Other imports
import argparse, dictionary, os, utterance, lattice_tools
import sire_io as io
from error_messages import SiReError

#Writes out an mlf for initialising alignment and one with short pauses added.
#These are compatible with the multisyn alignment tools. Their main difference
#to the standard festival mlfs is that they include dots for syllable boundaries
#and marks syllable stress using "#1" and "#2" for primary and secondary stress
#respectively (only in the sp version as that is what is used for the final alignment).
#These are marked as if phoneme stress but are incorrect (simply
#put at first phoneme in syllable). You must add these as tee models in the multisyn
#alignments to make it work.
#NOTE: No stress is NOT marked #0, it is simply assumed it is unstressed if unmarked.
#If syll_info is set to false we don't write out the syllable stress markers and dots for syll boundaries.
def write_initial_alignment_mlfs(utt, spmlf, nospmlf, no_stop_split=False):
  spmlf.write("\"*/"+utt.id+".lab\"\n")
  nospmlf.write("\"*/"+utt.id+".lab\"\n")
  
  wlen = len(utt.words)-1
  for wi, word in enumerate(utt.words):
    slen = len(word.syllables)-1
    for si, syllable in enumerate(word.syllables):
      if syllable.stress != "0":
        spmlf.write("#"+syllable.stress+"\n")
      for phoneme in syllable.phonemes:
        #If the phoneme is a stop we split it in closure and release.
        if phoneme.get_feats_dict()["CT"] == "s" and no_stop_split == False:
          spmlf.write(phoneme.id+"_cl\n")
          spmlf.write(phoneme.id+"\n")
          nospmlf.write(phoneme.id+"_cl\n")
          nospmlf.write(phoneme.id+"\n")
        else:
          spmlf.write(phoneme.id+"\n")
          nospmlf.write(phoneme.id+"\n")
      if si != slen:
        spmlf.write(".\n")
    #At the end of a word which is not "sil" we add sp model
    if wi != wlen and word.id != "sil":
      spmlf.write("sp\n")
  
  #We end with a dot
  spmlf.write(".\n")
  nospmlf.write(".\n")

#Writes out an HTK SLF lattice for lattice based alignment.
def write_slf_alignment_lattices(outpath, sent, slfdirpath, dictionary, pronoun_variant):
  #Make the SLF
  slf = lattice_tools.make_phoneme_slf(sent, dictionary, pronoun_variant)
  
  #Write it out
  wf = open(os.path.join(slfdirpath, outpath), "w")
  for l in slf:
    wf.write(l)
  wf.close()

#Writes out an HTK SLF lattice for phoneme ngram re-scoring.
def write_slf_phoneme_ngram_lattices(outpath, sent, slfdirpath, dictionary, no_syll_stress):
  #Make the SLF
  slf = lattice_tools.make_phoneme_slf(sent, dictionary, pronoun_variant=True, no_syll_stress=no_syll_stress, SRILM_lattice_fix=True)
  
  #Write it out
  wf = open(os.path.join(slfdirpath, outpath), "w")
  for l in slf:
    wf.write(l)
  wf.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create alignment mlfs and slfs.')
  parser.add_argument('txtdir', type=str, help="The directory containing the txt files with the sentences to create lattices/mlfs from.")
  parser.add_argument('combilexpath', type=str, help="The path to the combilex dictionary directory.")
  parser.add_argument('outdir', type=str, help="The outpath directory.")
  parser.add_argument('-mlf', action="store_true", help="Output mlfs.")
  parser.add_argument('-mlfname', type=str, help="The name to prepend the output mlfs, if making mlfs.", default="txt")
  parser.add_argument('-pronoun_variant', action="store_true", help="Create pronounciation variant slfs. Always true when creating phoneme ngram slfs.")
  parser.add_argument('-no_syll_stress', action="store_true", help="Create pronounciation variant slfs for ngram rescoring without syllable stress information.")
  parser.add_argument('-no_stop_split', action="store_true", help="If making mlfs do not split stops in two.")
  
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-slf_phoneme', action="store_true", help="Output phoneme ngram rescoring suitable slfs.")
  group.add_argument('-slf_align', action="store_true", help="Output alignment suitable slfs.")
  
  args = parser.parse_args()
  
  if args.mlf == True and args.slf_phoneme == True:
    raise SiReError("It makes no sense to make mlfs at the same time as phoneme slfs.")
  
  
  if args.mlf != True and args.slf_phoneme != True and args.slf_align != True:
    raise SiReError("You must be doing at least one mlf or slf type.")
  
  #Used for utt creation
  args.intype = "txt"
  args.stanford_pcfg_parse = False
  args.stanford_dependency_parse = False
  args.festival_features = False
  args.dictionary = dictionary.Dictionary(args.combilexpath)
  
  if args.pronoun_variant:
    if args.slf_phoneme or args.slf_align:
      pass
    else:
      raise SiReError("Cannot create pronounciation variant mlfs. Please output slfs.")
  
  txtfiles = io.load_txt_dir(args.txtdir)
  
  #Opening the mlf files here means we don't have to loop twice if outputting slfs as well.
  if args.mlf:
    #Out mlf with short pause
    wfsp = open(os.path.join(args.outdir, args.mlfname+"_sp.mlf"), "w")
    wfsp.write("#!MLF!#\n")
    #out mlf without short pause
    wfnosp = open(os.path.join(args.outdir, args.mlfname+"_no_sp.mlf"), "w")
    wfnosp.write("#!MLF!#\n")
  
  for txt in txtfiles:
    print "Processing {0}".format(txt)
    if args.mlf:
      #Make an utt
      utt = utterance.Utterance(txt, args)
      #Write out mlfs for standard alignment methods.
      write_initial_alignment_mlfs(utt, wfsp, wfnosp, args.no_stop_split)
    if args.slf_align:
      write_slf_alignment_lattices(txt[0]+'.slf', txt[1:], args.outdir, args.dictionary, args.pronoun_variant)
    elif args.slf_phoneme:
      write_slf_phoneme_ngram_lattices(txt[0]+'.slf', txt[1:], args.outdir, args.dictionary, args.no_syll_stress)
  
  if args.mlf:
    wfsp.close()
    wfnosp.close()
