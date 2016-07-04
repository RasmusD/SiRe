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
from error_messages import SiReError

#Opens each .lab file in a dir line by line.
def open_labdir_line_by_line(path, dur_lab=False):
  l = os.listdir(path)
  labs = []
  if dur_lab == False:
    for i, lab in enumerate(l):
      if ".lab" in lab:
        tmp = [lab.split(".")[0]]
        tmp += [x.split() for x in open(os.path.join(path, lab), "r").readlines()]
        labs.append(tmp)
  elif dur_lab == True:
    for i, lab in enumerate(l):
      if ".dur" in lab:
        c_pos = 0
        tmp = [lab.split(".")[0]]
        for x in open(os.path.join(path, lab), "r").readlines():
          if ".state[" not in x:
            x = x.split()
            frames = int(x[-3].split("=")[1])
            tmp += [[str(c_pos*50000), str((c_pos+frames)*50000), x[0]]]
            c_pos += frames
        labs.append(tmp)
  else:
    raise SiReError("dur_lab must be boolean!")
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
  if intype in ["align_mlf", "state_align_mlf"]:
    ext = ".rec"
  elif intype == "hts_mlf":
    ext = ".lab"
  else:
    raise SiReError("Don't know what to do with mlf of type - {0}".format(intype))
  #Remove mlf header
  mlf.pop(0)
  labs = []
  tmp = []
  end = len(mlf) - 1
  for i, l in enumerate(mlf):
    l = l.split()
    if ext in l[0]:
      if tmp == []:
        tmp.append(l[0].split("*/")[1].split(".")[0])
      else:
        if tmp[-1] == ["."]:
          tmp.pop(-1)
        labs.append(tmp)
        tmp = []
        tmp.append(l[0].split("*/")[1].split(".")[0])
    elif i == end:
      labs.append(tmp)
    else:
      tmp.append(l)
  # Collapse states
  if intype == "state_align_mlf":
    new_labs = []
    for lab in labs:
      n_lab = []
      tmp = []
      for i, line in enumerate(lab):
        #print line
        if i == 0:
          n_lab.append(line)
        elif line[2] == "s2":
          tmp.append(line)
        elif line[2] == "s6":
          #Append the state info
          tmp.append(line)
          if len(tmp) != 5:
            raise SiReError("Not enough states in phone! 5 expected but I got {0}! Please check format.\n{1}".format(len(tmp), tmp))
          n_lab.append(tmp)
          tmp = []
        else:
          tmp.append(line)
      new_labs.append(n_lab)
    labs = new_labs
  return labs
