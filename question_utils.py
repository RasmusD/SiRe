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

import argparse

def merge(set1, set2, outpath):
  set1 += set2
  set1 = list(set(set1))
  set1.sort()
  wf = open(outpath, "w")
  for l in set1:
    wf.write(l.strip()+"\n")
  wf.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Utility question file related methods.')
  parser.add_argument('-merge', nargs=3, help="Merge two question sets into 1.", metavar=('set1', 'set2', 'outpath'))
  args = parser.parse_args()
  
  if args.merge:
    l1 = open(args.merge[0], "r").readlines()
    l2 = open(args.merge[1], "r").readlines()
    merge(l1, l2, args.merge[2])
