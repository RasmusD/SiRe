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

import argparse, io, sys

def get_phoneme_strings(labs):
  n_labs = []
  for i, lab in enumerate(labs):
    tmp = []
    #Get rid of the name
    #print lab
    lab.pop(0)
    for phon in lab:
      #The align labs have stops split marked with _cl. We don't want the _cl.
      #We also don't want phoneme boundaries and the like.
      #One could experiment with keeping some of these markers in the data.
      if "_cl" not in phon[-1] and phon[-1] not in [".", "#1", "#2"]:
        #Only use sp if it has any length
        if phon[-1] == "sp":
          if phon[0] != phon[1]:
            print phon
            tmp.append("sil")
        else:
          tmp.append(phon[-1])
    n_labs.append(tmp)
  return n_labs

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create a txt file with phoneme strings for phoneme LM creation.')
  parser.add_argument('input_mlf', type=str, help="The input mlf.")
  parser.add_argument('outputpath', type=str, help="The output filepath.")
  parser.add_argument('-f', action='store_true', help="Force overwrite of outputpath file if it exists.")
  args = parser.parse_args()
  
  wf = io.open_writefile_safe(args.outputpath, args.f)
  
  labs = io.parse_mlf(io.open_file_line_by_line(args.input_mlf), "align_mlf")
  
  labs = get_phoneme_strings(labs)
  
  for lab in labs:
    wf.write(" ".join(lab)+"\n")
  wf.close()
