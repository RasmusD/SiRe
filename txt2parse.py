import os, argparse, subprocess

def parse_stanford(args):
  #First perform PTB tokenisation
  if not args.pretokenised:
    for txt in os.listdir(args.txtdir):
      if ".txt" in txt:
        subprocess.call(args.javapath+" -cp "+os.path.join(args.parserdir, "stanford-parser.jar")+" edu.stanford.nlp.process.PTBTokenizer "+os.path.join(args.txtdir, txt)+" | paste -s --delimiters=\" \" | sed s': \\. : , :'g > "+os.path.join(args.tokenpath, txt[:-3]+"tokenised"), shell=True)
  
  subprocess.call(args.javapath+" -mx2000m -cp \""+args.parserdir+"/*:\" edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat \"penn,typedDependencies\" edu/stanford/nlp/models/lexparser/englishFactored.ser.gz "+args.tokenpath+"/*.tokenised > "+os.path.join(args.outpath, "parser.log"), shell=True)

#Split a stanford parse log into seperate sentences.
def split_parse(pf):
  parses = []
  cur_parse = []
  ln = len(pf)
  
  for i, l in enumerate(pf):
    if l == "(ROOT" or i + 1 == ln:
      if cur_parse != []:
        parses.append(split_parse_relations(cur_parse))
      cur_parse = [l]
    else:
      cur_parse.append(l)
  
  return parses

#Split into parse and relations
def split_parse_relations(parse):
  syntactic = ""
  relations = []
  
  split = False
  for l in parse:
    if not split:
      if l == "":
        split = True
      else:
        syntactic += l
    else:
      relations.append(l)
  
  return [syntactic, relations]

#We can write out an individual file for each parse with the right name
#by matching it with the files in the tokenised dir.
#This is necessary as the stanford parser does not add the id of the
#parent file to the parse. But it is a bit unsafe.
#We need to sort as the output of the parser is also sorted. Makes it a bit less unsafe.
def write_out(pf, out, tf):
  count = 0
  tf.sort()
  for txt in tf:
    wf = open(os.path.join(out, txt.split(".")[0]+".parse"), "w")
    wf2 = open(os.path.join(out, txt.split(".")[0]+".relations"), "w")
    
    wf.write(pf[count][0]+"\n")
    for l in pf[count][1]:
      wf2.write(l+"\n")
    wf.close()
    wf2.close()
    count += 1

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Perform a syntactic parsing of the text files using the Stanford parser. The output log of the stanford parser is subsequently loaded and split into individual parse files.')
  parser.add_argument('parserdir', type=str, help="The directory containing the parser to use.")
  parser.add_argument('-txtdir', type=str, help="The directory containing the original txt files.", default="txt")
  parser.add_argument('-parser_type', type=str, help="The type of parser to use. Currently only stanford is supported.", default="stanford", choices=["stanford"])
  parser.add_argument('-outpath', type=str, help="The output directory.", default="parse")
  parser.add_argument('-tokenpath', type=str, help="The directory to output PTB tokenised sentences.", default="tokenised")
  parser.add_argument('-javapath', type=str, help="Specify the path to the java executable. This is in case the default javapath is not correct or points to a wrong version of java.", default="java")
  parser.add_argument('-preparsed', action='store_true', help="Specify as true if the sentences have already been parsed and the outdir contains a parser.log file. Parsing is then skipped and the log file is split into seperate parse files.")
  parser.add_argument('-pretokenised', action='store_true', help="Specify as true if the sentences have already been tokenised and the output is present in tokenpath.")
  args = parser.parse_args()
  
  if not args.preparsed:
    parse_stanford(args)
  
  parse = [x.strip() for x in open(os.path.join(args.outpath, "parser.log")).readlines()]
  
  parse = split_parse(parse)
  
  #Write out the parses to seperate files
  write_out(parse, args.outpath, os.listdir(args.tokenpath))
