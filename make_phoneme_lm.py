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

#Methods for writing out the necessary files for training a phoneme language model based on an existing alignment.
#This phoneme LM can then be used for phoneme reductions when synthesising.
#This does not make sense on mlfs produced by non-variant alignment methods.

#Load the SiReImports.pth file
import site
site.addsitedir(".")

#Other imports
import argparse, subprocess, os
import sire_io as io

#It is assumed that the input mlf uses "#1" and "#2" to mark syllable stress at the beginning of syllables. This is changed to "sb"
#"." to mark word internal syllable boundaries. This is changed to "sb".
#"sp" to mark word boundaries. These may have some duration if there is a mid sentential pause and is replaced with "sil" if that is the case else kept as marker of word boundary.
#"_cl" to mark the closure of a stop. This is discarded.
def get_phoneme_strings(labs, no_syll_stress):
  n_labs = []
  for i, lab in enumerate(labs):
    tmp = []
    #Get rid of the name
    #print lab
    lab.pop(0)
    for n, phon in enumerate(lab):
      #The align labs have stops split marked with _cl. We don't want the _cl.
      #We include phoneme boundaries and the like for later recreation of the utt.
      #One could experiment with removing some of these markers in the data.
      if "_cl" not in phon[-1]:
        if phon[-1] in [".", "#1", "#2"]:
          if lab[n-1][-1] not in ["sp", "sil"]:
            if no_syll_stress == True:
              tmp.append("sb")
            else:
              tmp.append(phon[-1])
        #Use sp as sil if it has any length
        #Else we simply keep it to mark a word boundary
        elif phon[-1] == "sp" and phon[0] != phon[1]:
          tmp.append("sil")
        else:
          tmp.append(phon[-1])
    n_labs.append(tmp)
  return n_labs

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create a dir of txt files with phoneme strings for phoneme LM creation.')
  parser.add_argument('input_mlf', type=str, help="The input mlf.")
  parser.add_argument('outpath', type=str, help="The output directory path.")
  parser.add_argument('ngram_binary_path', type=str, help="The path to the LM making binary. For SRILM this is the ngram-count binary.")
  parser.add_argument('-lm_binary_options', type=str, help="Additional arguments to be sent to the ngram binary as options. Overwrites the defaults options: -order 4 -interpolate -gt3min 1 -wbdiscount -debug 3", nargs=argparse.REMAINDER, default='-order 4 -interpolate -gt3min 1 -wbdiscount -debug 3'.split())
  parser.add_argument('-f', action='store_true', help="Force overwrite of outputpath file if it exists.")
  parser.add_argument('-no_syll_stress', action='store_true', help="Replace syllable stress markers with a boundary marker sb.")
  args = parser.parse_args()
  
  wf = io.open_writefile_safe(os.path.join(args.outpath, "sents.txt"), args.f)
  
  labs = io.parse_mlf(io.open_file_line_by_line(args.input_mlf), "align_mlf")
  
  labs = get_phoneme_strings(labs, args.no_syll_stress)
  
  for lab in labs:
    wf.write(" ".join(lab)+"\n")
  wf.close()
  
  txtpath = os.path.join(args.outpath, "sents.txt")
  
  lmpath = os.path.join(args.outpath, "ngram.lm")
  
  #This allows for people to pass their own options to the ngram binary
  options = " "+" ".join(args.lm_binary_options)
  subprocess.call(args.ngram_binary_path+" -text "+txtpath+" -lm "+lmpath+options, shell=True)
