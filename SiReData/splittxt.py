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

import argparse, os

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Load txt file and output one txt file per line.')
  parser.add_argument('inpath', type=str, help='The input txt file path.')
  parser.add_argument('txtdir', type=str, help="The output directory.")
  parser.add_argument('prepend', type=str, help="The output filename prepend.")
  args = parser.parse_args()
  
  f = [x.strip() for x in open(args.inpath, "r").readlines()]
  
  for i, l in enumerate(f):
    wf = open(os.path.join(args.txtdir, args.prepend+str(i)+".txt"), "w")
    wf.write(l)
    wf.close()
