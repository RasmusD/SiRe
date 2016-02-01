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

import argparse, dictionary, io

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Checks if words in a dictionary.')
  parser.add_argument('indir', type=str, help='The input dir of txt files.')
  parser.add_argument('combilexpath', type=str, help='The path to the directory containing combilex.')
  parser.add_argument('-outfile', type=str, help='The output filepath if an output of words not in the dictionary is desired.')
  args = parser.parse_args()
  
  txt = io.load_txt_dir(args.indir)
  
  dct = dictionary.Dictionary(args.combilexpath)
  
  oov = []
  
  for t in txt:
    tmp = [t[0]]
    for w in t[1:]:
      try:
        dct.raw_dictionary_entries[w]
      except KeyError:
        tmp.append(w)
    if len(tmp) > 1:
      oov.append(tmp)
  
  if args.outfile:
    pass
  else:
    for l in oov:
      print " ".join(l)
