import os, argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Converts a Flite style HTS full-context label to monophone lab.')
  parser.add_argument('inpath', type=str, help='The dir contaning full context labels.')
  parser.add_argument('outpath', type=str, help='The output dir for the monophone labs.')
  args = parser.parse_args()
  
  indir = os.listdir(args.inpath)
  
  delim_left = "-"
  delim_right = "+"
  
  for f in indir:
    if ".lab" in f:
      lab = [x.strip().split() for x in open(os.path.join(inpath, f), "r").readlines()]
      wf = open(os.path.join(outpath, f), "w")
      for i, l in enumerate(lab):
        lab[i][2] = l[2].split(delim_left)[1].split(delim_right)[0]
        wf.write(' '.join(lab[i])+"\n")
      wf.close()
