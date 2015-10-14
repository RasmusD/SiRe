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

#Methods for writing out the necessary files for forced alignment.

import argparse, dictionary, os, utterance, io

#Writes out an mlf for initialising alignment and one with short pauses added.
#These are compatible with the multisyn alignment tools. Their main difference
#to the standard festival mlfs is that they include dots for syllable boundaries
#and marks syllable stress using "#1" and "#2" for primary and secondary stress
#respectively (only in the sp version as that is what is used for the final alignment).
#These are marked as if phoneme stress but are incorrect (simply
#put at first phoneme in syllable). You must add these as tee models in the multisyn
#alignments to make it work.
#NOTE: No stress is NOT marked #0, it is simply assumed it is unstressed if unmarked.
def write_initial_alignment_mlfs(utt, spmlf, nospmlf):
  spmlf.write("\"*/"+utt.id+".lab\"\n")
  nospmlf.write("\"*/"+utt.id+".lab\"\n")
  #We start with silence
  spmlf.write("sil\n")
  nospmlf.write("sil\n")
  
  wlen = len(utt.words)-1
  for wi, word in enumerate(utt.words):
    slen = len(word.syllables)-1
    for si, syllable in enumerate(word.syllables):
      if syllable.stress != "0":
        spmlf.write("#"+syllable.stress+"\n")
      for phoneme in syllable.phonemes:
        #If the phoneme is a stop we split it in closure and release.
        if phoneme.get_feats_dict()["CT"] == "s":
          spmlf.write(phoneme.id+"_cl\n")
          spmlf.write(phoneme.id+"\n")
          nospmlf.write(phoneme.id+"_cl\n")
          nospmlf.write(phoneme.id+"\n")
        else:
          spmlf.write(phoneme.id+"\n")
          nospmlf.write(phoneme.id+"\n")
      if si != slen:
        spmlf.write(".\n")
    #At the end of a word we add sp model
    if wi != wlen:
      spmlf.write("sp\n")
  
  #We end with silence and a dot
  spmlf.write("sil\n.\n")
  nospmlf.write("sil\n.\n")

#Writes out an HTK SLF lattice for lattice based alignment.
def write_slf_alignment_lattices(utt, slfdirpath, dictionary, pronoun_variant):
  #We can't write immediately as some line sdepend on later lines
  slf = []
  slf.append("# Size of Network: N=num nodes, L=num arcs\n")
  N = 0
  L = 0
  #To be filled later
  slf.append("")
  slf.append("# List of nodes: I=node-number, W=word\n")
  nodes = []
  arcs = []
  #We always start with sil
  nodes.append("I="+str(N)+" W=sil\n")
  N+=1
  #The first word starts at sil
  w_start_node = N-1
  #The first word ends at sil+1
  w_end_node = N
  #And the node is sp normally but if only 1 wor din utt it is sil.
  wlen = len(utt.words)-1
  if wlen > 0:
    nodes.append("I="+str(N)+" W=sp\n")
  else:
    nodes.append("I="+str(N)+" W=sil\n")
    #If at the end we add an arc as well
    arcs.append("J="+str(L)+" S="+str(w_end_node)+" E="+str(N))
  N+=1
  #Add each pronounciation allowed for the word
  for wi, word in enumerate(utt.words):
    if pronoun_variant:
      entries = dictionary.get_all_align_entries(word.id)
      for entry in entries:
        nodes, arcs, N, L = make_word_nodes_arcs(entry, nodes, arcs, N, L, w_start_node, w_end_node)
    else:
      entry = dictionary.get_single_align_entry(word.id)
      nodes, arcs, N, L = make_word_nodes_arcs(entry, nodes, arcs, N, L, w_start_node, w_end_node)
    #Now the new start_node is the previous end node
    w_start_node = w_end_node
    #And the new end node is either sil or sp depending on if this is the last word.
    if wlen != wi:
      nodes.append("I="+str(N)+" W=sp\n")
    else:
      nodes.append("I="+str(N)+" W=sil\n")
      #If at the end we add an arc as well
      arcs.append("J="+str(L)+" S="+str(w_end_node)+" E="+str(N))
    w_end_node = N
    N+=1
  
  for node in nodes:
    slf.append(node)
  slf.append("# List arcs: J=arc-number, S=start-node, E=end-node\n")
  for arc in arcs:
    slf.append(arc)
  #Fix the line with N and L
  slf[1] = "N="+str(len(nodes))+" L="+str(len(arcs))+"\n"
  
  #Write it out
  wf = open(os.path.join(slfdirpath, utt.id+".slf"), "w")
  for l in slf:
    wf.write(l)
  wf.close()

#Make nodes and arcs for a word starting at node num N and arc num L
#Returns nodes and arcs with the added new nodes and arcs
#If pronoun_variant is true 
def make_word_nodes_arcs(phons, nodes, arcs, N, L, start_node, end_node):
  for i, phone in enumerate(phons):
    #Add the node
    nodes.append("I="+str(N)+" W="+phone+"\n")
    #If the first phon we add arch from start_node
    if i == 0:
      arcs.append("J="+str(L)+" S="+str(start_node)+" E="+str(N)+"\n")
    else: #else we add from previous to current
      arcs.append("J="+str(L)+" S="+str(N-1)+" E="+str(N)+"\n")
    N+=1
    L+=1
  #The last phoneme has been added so we add arc to end_node
  #Note S is -1 because we just incremented N
  arcs.append("J="+str(L)+" S="+str(N-1)+" E="+str(end_node)+"\n")
  L+=1
  return nodes, arcs, N, L

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create alignment mlfs and slfs.')
  parser.add_argument('-txtdir', type=str, help="The directory containing the original txt files.", default="txt")
  parser.add_argument('-outdir', type=str, help="The outpath directory.", default="align")
  parser.add_argument('-mlf', action="store_true", help="Output mlfs.")
  parser.add_argument('-mlfname', type=str, help="The name to prepend the output mlfs, if making mlfs.", default="txt")
  parser.add_argument('-slf', action="store_true", help="Output slfs.")
  parser.add_argument('-pronoun_variant', action="store_true", help="Create pronounciation variant slfs.")
  parser.add_argument('combilexpath', type=str, help="The path to the combilex dictionary directory.")
  args = parser.parse_args()
  
  #Used for utt creation
  args.intype = "txt"
  args.stanfordparse = False
  args.dictionary = dictionary.Dictionary(args.combilexpath)
  
  if args.pronoun_variant and not args.slf:
    print "Cannot create pronounciation variant mlfs. Please output slfs."
    sys.exit()
  
  txtfiles = io.load_txt_dir(args.txtdir)
  
  #Opening the mlf files here means we don't have to loop twice if outputtinh slfs as well.
  if args.mlf:
    #Out mlf with short pause
    wfsp = open(os.path.join(args.outdir, args.mlfname+"_sp.mlf"), "w")
    wfsp.write("#!MLF!#\n")
    #out mlf without short pause
    wfnosp = open(os.path.join(args.outdir, args.mlfname+"_no_sp.mlf"), "w")
    wfnosp.write("#!MLF!#\n")
  
  for txt in txtfiles:
    print "Processing {0}".format(txt)
    #Make an utt
    utt = utterance.Utterance(txt, args)
    if args.mlf:
      #Write out mlfs for standard alignment methods.
      write_initial_alignment_mlfs(utt, wfsp, wfnosp)
    if args.slf:
      write_slf_alignment_lattices(utt, args.outdir, args.dictionary, args.pronoun_variant)
  
  if args.mlf:
    wfsp.close()
    wfnosp.close()
