import os

#Opens each .lab file in a dir line by line.
def open_line_by_line(path):
  l = os.listdir(path)
  labs = []
  for i, lab in enumerate(l):
    if ".lab" in lab:
      tmp = [lab.split(".")[0]]
      tmp += [x.split() for x in open(os.path.join(path, lab), "r").readlines()]
      labs.append(tmp)
  return labs

#Opens and tokenizes a file.
def open_and_tokenise_txt(path):
  txt = open(path, "r").read()
  for x in [".", ",", "!", "?", ";", ":"]:
    txt = txt.replace(x, "")
  return [path[:-4]]+txt.lower().split()

#Opens, and tokenizes all txt files in a dir.
def load_txt_dir(dirpath):
  return [open_and_tokenise_txt(os.path.join(dirpath, x)) for x in os.listdir(dirpath) if ".txt" in x]
