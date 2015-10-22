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

import argparse, io, os, sys, subprocess

#Combines all txt files in a dir to one txt file where the others are written line by line.
def combine_txt(indirpath, outfilepath, overwrite=False):
  lines = io.load_txt_dir(indirpath)
  
  wf = io.open_writefile_safe(outfilepath, overwrite)
  
  for line in lines:
    wf.write(" ".join(line[1:])+"\n")
  
  wf.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Make a file with each sentence line by line from a directory of txt files.')
  parser.add_argument('txtdir', type=str, help="The input directory.")
  parser.add_argument('outdirpath', type=str, help="The output directory path.")
  parser.add_argument('lm_path', type=str, help="Path to the LM to use.")
  parser.add_argument('lm_binary', type=str, help="Path to the LM binary to use. For SRILM_NGRAM this should be the ngram binary.")
  parser.add_argument('-lm_type', type=str, help="The type of LM to use. Currently only SRILM NGRAM.", choices=['SRILM_NGRAM'], default='SRILM_NGRAM')
  parser.add_argument('-f', action="store_true", help="Overwrite all output files without asking.")
  parser.add_argument('-no_tmp_file', action="store_true", help="If true a scored.txt file will not be written out and the .scored files produced directly.")
  parser.add_argument('-pre_scored', action="store_true", help="Indicates that .scores files already exists and do not need to be remade.")
  args = parser.parse_args()
  
  if not args.pre_scored:
    comb_file = os.path.join(args.outdirpath, "combined.txt")
    
    combine_txt(args.txtdir, comb_file, args.f)
    
    if args.lm_type == "SRILM_NGRAM":
      if not args.no_tmp_file:
        subprocess.call(args.lm_binary+" -debug 2 -tolower -ppl "+comb_file+" -lm "+args.lm_path+" -unk > "+os.path.join(args.outdirpath, "scored.txt"), shell=True)
        scores = open(os.path.join(args.outdirpath, "scored.txt"), "r").read()
      else:
        scores = subprocess.communicate(args.lm_binary+" -debug 2 -tolower -ppl "+comb_file+" -lm "+args.lm_path+" -unk > "+os.path.join(args.outdirpath, "scored.txt"))
  
  
  scores = open(os.path.join(args.outdirpath, "scored.txt"), "r").read()
  
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
  #This relies on positions when lisitng txt dir.
  #Will fail if other files than txt files in dir.
  #Could also rely on content <- safer see TODO.
  txt = os.listdir(args.txtdir)
  n = 0
  for t in txt:
    if ".txt" in t:
      wf = io.open_writefile_safe(os.path.join(args.outdirpath, t[:-3]+"scored"))
      for l in scores[n]:
        wf.write(l+"\n")
      wf.close()
      n+=1
  
  sys.exit()
