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
