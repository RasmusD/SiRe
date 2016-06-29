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

# Takes pronunciation lattices and scores them using a phone LM before outputting a mlf in the align style.

#Load the SiReImports.pth file
#Note this assumes we are in the SiReData dir when calling the script.
import site
site.addsitedir("../")

import argparse, os, subprocess, sire_io

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Load pronunciation lattices and scores them using a phone LM before outputting a mlf in the align style.')
  parser.add_argument('inpath', type=str, help='The input slf dir.')
  parser.add_argument('outmlfpath', type=str, help="The output mlf path.")
  parser.add_argument('lmpath', type=str, help="The lm to use for scoring.")
  parser.add_argument('latticetoolpath', type=str, help="The path to the SRILM lattice-tool.")
  parser.add_argument('-options', type=str, help="Overwrite the standard options to lattice-tool with the provided string [-read-htk -order 4 -viterbi-decode -old-decoding].", default="-read-htk -order 4 -viterbi-decode -old-decoding")
  args = parser.parse_args()
  
  slfs = os.listdir(args.inpath)
  
  mlf = ["#!MLF!#\n"]
  
  for slf in slfs:
    bestpath = subprocess.check_output(args.latticetoolpath+" -in-lattice "+os.path.join(args.inpath, slf)+" -lm "+args.lmpath+" "+args.options, stderr=subprocess.STDOUT, shell=True)
    bestpath = bestpath.split()
    mlf.append("\"*/"+bestpath.pop(0)+".rec\"\n")
    faketime = 0
    for p in bestpath:
      if p == "<s>" or p == "</s>":
        pass
      elif p in [".", "sp"]:
        mlf.append(str(faketime)+" "+str(faketime)+" "+p+" 0.0 "+p+"\n")
      elif p in ["#1", "#2"]:
        # We first add the stress marker and then a "." to mark the boundary.
        # Without the dot load_utterance from align mlf will not detect the syllable boundary.
        mlf.append(str(faketime)+" "+str(faketime)+" "+p+" 0.0 "+p+"\n")
        mlf.append(str(faketime)+" "+str(faketime)+" . 0.0 .\n")
      else:
        mlf.append(str(faketime)+" "+str(faketime+10000)+" "+p+" 0.0 "+p+"\n")
        faketime+=10000
    mlf.append(".\n")
  
  
  wf = sire_io.open_writefile_safe(args.outmlfpath)
  
  for l in mlf:
    wf.write(l)
  
  wf.close()
