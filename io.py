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

import os, sys

#Opens each .lab file in a dir line by line.
def open_labdir_line_by_line(path):
  l = os.listdir(path)
  labs = []
  for i, lab in enumerate(l):
    if ".lab" in lab:
      tmp = [lab.split(".")[0]]
      tmp += [x.split() for x in open(os.path.join(path, lab), "r").readlines()]
      labs.append(tmp)
  return labs

#Opens a file and returns a list containing each line as a seperate item.
def open_file_line_by_line(path):
#  return open(path, "r").read().split("\n") #This is probably faster but will leave the last item as '' if file ends with \n - the below does not so is easier to work with.
  return [x.strip() for x in open(path, "r").readlines()]

#Opens and makes a simple tokenization of a file (actually just removes tokens).
#The return list has the format of l[0] == The name of the txt filepath - .txt extension.
#l[1:] the tokens.
def open_and_tokenise_txt(path, keep_commas=False):
  txt = open(path, "r").read()
  punctuation = [".", ",", "!", "?", ";", ":"]
  if keep_commas:
    punctuation.remove(",")
    txt = txt.replace(",", " , ")
    #We may have made double whitespace from this
    txt = txt.replace("  ", " ")
  for x in punctuation:
    txt = txt.replace(x, "")
  #This has to be done seperately as some word contain this in the middle
  txt.replace(" - ", " ")
  return [os.path.splitext(os.path.basename(path))[0]]+txt.lower().split()

#Opens, and tokenizes all txt files in a dir and returns them in a list.
#We may wish to keep_commas as they may mark a pause.
#If you want the file id kept use keep_file_id, it will return a tuple (file_id, tokenized_txt_list) for each list item.
def load_txt_dir(dirpath, keep_commas=False):
  print "Loading txt files from dir..."
  txt = [open_and_tokenise_txt(os.path.join(dirpath, x), keep_commas) for x in os.listdir(dirpath) if ".txt" in x]
  print "Done."
  return txt

#Checks if a path exists before opening the file to avoid overwriting.
#Alternatively if overwrite is set to True a warning is printed.
def open_writefile_safe(filepath, overwrite=False):
  if os.path.exists(filepath):
    if overwrite == True:
      print "WARNING! Overwriting file {0}!".format(filepath)
    else:
      a = raw_input("The output file exists ({0})! Overwrite? (y)es / (n)o\n".format(filepath))
      if a == "y":
        print "Overwriting..."
        pass
      elif a == "n":
        print "Will not create outfile, exiting..."
        sys.exit()
      else:
        a = raw_input("Please use (y)es / (n)o\n")
  
  return open(filepath, "w")

#Parse an mlf into the lines of containing labels.
#Each labels is a list of each line split on whitespace.
def parse_mlf(mlf, intype):
  if intype == "align_mlf":
    ext = ".rec"
  elif intype == "hts_mlf":
    ext = ".lab"
  else:
    print "Don't know what to do with mlf of type - {0}".format(intype)
  #Remove mlf header
  mlf.pop(0)
  labs = []
  tmp = []
  for l in mlf:
    tmp.append(l.split())
    if l.strip() == ".":
      if ext not in tmp[0][0]:
        print "Error: Something wrong with lab:\n"
        print tmp
        sys.exit()
      else:
        tmp[0] = tmp[0][0].split("*/")[1].split(".")[0]
        tmp.pop(-1)
      labs.append(tmp)
      tmp = []
  return labs
