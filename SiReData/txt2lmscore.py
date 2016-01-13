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

#Takes the txt files in a directory and scores them using a LM outputting
#one .scores file per .txt file containing each word line by line with its
#LM probability.

#Load the SiReImports.pth file
import site
site.addsitedir("../")

import argparse, os, subprocess, dictionary, lattice_tools
import SiReIO as io

#Combines all txt files in a dir to one txt file where the others are written line by line.
def combine_txt(indirpath, outfilepath, overwrite=False):
  lines = io.load_txt_dir(indirpath)
  
  wf = io.open_writefile_safe(outfilepath, overwrite)
  
  for line in lines:
    wf.write(" ".join(line[1:])+"\n")
  
  wf.close()

def score_word_ngram(args):
  #Combine all txt files into one for LM scoring in one go.
  comb_file = os.path.join(args.outdirpath, "combined.txt")
  combine_txt(args.txtdir, comb_file, args.f)
  if args.no_tmp_file:
    return subprocess.communicate(args.lm_binary+" -ppl "+comb_file+" -lm "+args.lm_path + options)
  else:
    subprocess.call(args.lm_binary+" -ppl "+comb_file+" -lm "+args.lm_path + options +" > "+os.path.join(args.outdirpath, "scored.txt"), shell=True)
    return open(os.path.join(args.outdirpath, "scored.txt"), "r").read()

def write_word_score_files(scores, args):
  #First split on empty lines and then split on lines
  scores = [x.split("\n") for x in scores.split("\n\n")]
  
  #Pop the overall stats
  scores.pop(-1)
  
  #Take away unnecessaries
  scores = [x[1:-3] for x in scores]
  
  #Fix each line in each entry
  for i, e in enumerate(scores):
    for n, l in enumerate(e):
      l = l.split()
      scores[i][n] = l[1]+ " "+ l[-2]
  
  #Match up each scored sent with a txt file.
  #This relies on positions when listing txt dir.
  #Will fail if other files than txt files in dir or txtdir has been modified since scoring.
  #Could also rely on content <- safer see TODO.
  txt = os.listdir(args.txtdir)
  n = 0
  for t in txt:
    if ".txt" in t:
      wf = io.open_writefile_safe(os.path.join(args.outdirpath, t[:-3]+"scored"), args.f)
      for l in scores[n]:
        wf.write(l+"\n")
      wf.close()
      n+=1

#Create all the slfs and a list with paths to each file
def create_lattices_and_list(txtlist, outdirpath, dictionary, overwrite=False):
  path_list = []
  for txt in txtlist:
    path = os.path.join(outdirpath, txt[0]+".phoneme_slf")
    #Make the slf
    slf = lattice_tools.make_phoneme_slf(txt[1:], dictionary, pronoun_variant=True)
    #Write it out
    wf = io.open_writefile_safe(path, overwrite)
    for l in slf:
      wf.write(l)
    wf.close()
    #Everything has gone well so we add the path
    path_list.append(path)
  #Write out the path file.
  wf = io.open_writefile_safe(os.path.join(outdirpath, "lattices.list"))
  for p in path_list:
    wf.write(p+"\n")
  wf.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Load a dir of txt and output LM scores for each word in the sent or for the most likely phoneme path for each word from a phoneme LM. This currently supports only SRILM NGRAM LMs.')
  parser.add_argument('txtdir', type=str, help="The input directory.")
  parser.add_argument('outdirpath', type=str, help="The output directory path.")
  parser.add_argument('lm_path', type=str, help="Path to the LM to use.")
  parser.add_argument('lm_binary', type=str, help="Path to the LM binary to use. This should be the SRILM NGRAM binary for WORD_NGRAM and SRILM LATTICE_TOOLS for PHONEME_NGRAM.")
  parser.add_argument('-lm_type', type=str, help="The type of LM to use.", choices=['WORD_NGRAM', 'PHONEME_NGRAM'], default='WORD_NGRAM')
  parser.add_argument('-lm_binary_options', type=str, nargs=argparse.REMAINDER, help="Additional arguments to be forwarded to the ngram binary. This overwrites the defaults for each -lm_type. As these differ for each type please see the code for details of the defaults. Note that the input/output options are always already specified by the arguments passed to this python script.")
  parser.add_argument('-f', action="store_true", help="Overwrite all output files without asking.")
  parser.add_argument('-no_tmp_file', action="store_true", help="If true a scored.txt file will not be written out and the .scored files produced directly.")
  parser.add_argument('-pre_scored', action="store_true", help="Indicates that a scored.txt file already exists and do not need to be remade. I.e. if LM does no need to be run.")
  parser.add_argument('-lattices_exist', action="store_true", help="Indicates that lattices have already been created for each txt file and resides in the outdirpath.")
  parser.add_argument('-combilexpath', type=str, help="Path to the combilex dictionary for creating lattices from if lm_type is PHONEME_NGRAM.")
  args = parser.parse_args()
  
  if args.lm_binary_options:
    options += " "+" ".join(args.lm_binary_options)
  else:
    if args.lm_type == "WORD_NGRAM":
      options = " -debug 2 -tolower -unk"
    elif args.lm_type == "PHONEME_NGRAM":
      options = " -viterbi-decode"
      if args.f:
        options += " -overwrite"
  
  if args.lm_type == "WORD_NGRAM":
    if not args.pre_scored:
      scores = score_word_ngram(args)
    else:
      scores = open(os.path.join(args.outdirpath, "scored.txt"), "r").read()
    #Do the work
    write_word_score_files(scores, args)
  elif args.lm_type == "PHONEME_NGRAM":
    #First create lattices
    if not args.lattices_exist:
      txt = io.load_txt_dir(args.txtdir)
      dictionary = dictionary.Dictionary(args.combilexpath)
      create_lattices_and_list(txt, args.outdirpath, dictionary, args.f)
    #Then score them
    lattice_list_path = os.path.join(args.outdirpath, "lattices.list")
    subprocess.call(args.ngram_binary_path+" -lm "+args.lm_path+" -lattice-list "+lattice_list_path+options, shell=True)
