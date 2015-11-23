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

import argparse, dictionary, os, utterance, io, lattice_tools

#Writes out an mlf for initialising alignment and one with short pauses added.
#These are compatible with the multisyn alignment tools. Their main difference
#to the standard festival mlfs is that they include dots for syllable boundaries
#and marks syllable stress using "#1" and "#2" for primary and secondary stress
#respectively (only in the sp version as that is what is used for the final alignment).
#These are marked as if phoneme stress but are incorrect (simply
#put at first phoneme in syllable). You must add these as tee models in the multisyn
#alignments to make it work.
#NOTE: No stress is NOT marked #0, it is simply assumed it is unstressed if unmarked.
def write_initial_alignment_mlfs(utt, spmlf, nospmlf):
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
        if phoneme.get_feats_dict()["CT"] == "s":
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

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create alignment mlfs and slfs.')
  parser.add_argument('-txtdir', type=str, help="The directory containing the original txt files.", default="txt")
  parser.add_argument('-outdir', type=str, help="The outpath directory.", default="align")
  parser.add_argument('-mlf', action="store_true", help="Output mlfs.")
  parser.add_argument('-mlfname', type=str, help="The name to prepend the output mlfs, if making mlfs.", default="txt")
  parser.add_argument('-slf', action="store_true", help="Output slfs.")
  parser.add_argument('-pronoun_variant', action="store_true", help="Create pronounciation variant slfs.")
  parser.add_argument('combilexpath', type=str, help="The path to the combilex dictionary directory.")
  args = parser.parse_args()
  
  #Used for utt creation
  args.intype = "txt"
  args.stanfordparse = False
  args.dictionary = dictionary.Dictionary(args.combilexpath)
  
  if args.pronoun_variant and not args.slf:
    print "Cannot create pronounciation variant mlfs. Please output slfs."
    sys.exit()
  
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
      write_initial_alignment_mlfs(utt, wfsp, wfnosp)
    if args.slf:
      write_slf_alignment_lattices(txt[0]+'.slf', txt[1:], args.outdir, args.dictionary, args.pronoun_variant)
  
  if args.mlf:
    wfsp.close()
    wfnosp.close()
