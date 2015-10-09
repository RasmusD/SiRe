import argparse, os

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Load data file and output one txt file per sentence.')
  parser.add_argument('inpath', type=str, help='The input data file path.')
  parser.add_argument('-txtdir', type=str, help="The output directory.", default="txt")
  args = parser.parse_args()
  
  f = [x.split("\"") for x in open(args.inpath, "r").readlines()]
  
  for l in f:
    name = l[0][1:-1].strip()
    wf = open(os.path.join(args.txtdir, name+".txt"), "w")
    wf.write(l[1])
    wf.close()
