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

# A collection of methods for creating HTK style (SLF) lattices

#Makes an slf for a phoneme path
#pronoun_variant outputs all variants of each word in the dictionary
#no_syll_stress marks syllable boundaries only and with a common tag "sb" instead of syllable stress.
def make_phoneme_slf(words, dictionary, pronoun_variant=False, no_syll_stress=False, SRILM_lattice_fix=False):
  #We can't write immediately as some lines depend on later lines
  slf = []
  slf.append("# Size of Network: N=num nodes, L=num arcs\n")
  N = 0
  L = 0
  #To be filled later
  slf.append("")
  slf.append("# List of nodes: I=node-number, W=word\n")
  nodes = []
  arcs = []
  #We always start with sil - we have to add two and an arc for it to be processed
  nodes.append("I="+str(N)+" W=sil\n")
  N+=1
  if SRILM_lattice_fix == True:
    nodes.append("I="+str(N)+" W=sil\n")
    arcs.append("J="+str(L)+" S="+str(N-1)+" E="+str(N)+"\n")
    N+=1
    L+=1
  #The first word starts at sil
  w_start_node = N-1
  #The first word ends at sil+1
  w_end_node = N
  #And the node is sp normally but if only 1 word in utt it is sil.
  wlen = len(words)-1
  if wlen > 0:
    nodes.append("I="+str(N)+" W=sp\n")
  else:
    nodes.append("I="+str(N)+" W=sil\n")
  N+=1
  #Add each pronounciation allowed for the word
  for wi, word in enumerate(words):
    if pronoun_variant:
      entries = dictionary.get_all_lattice_entries(word, no_syll_stress)
      for entry in entries:
        nodes, arcs, N, L = make_word_nodes_arcs(entry, nodes, arcs, N, L, w_start_node, w_end_node)
    else:
      entry = dictionary.get_single_lattice_entry(word, no_syll_stress)
      nodes, arcs, N, L = make_word_nodes_arcs(entry, nodes, arcs, N, L, w_start_node, w_end_node)
    #Now the new start_node is the previous end node
    w_start_node = w_end_node
    #And the new end node is either sil or sp depending on if this is the word before last.
    if wi < wlen - 1: #If it is not the word before last or the last word add sp
      nodes.append("I="+str(N)+" W=sp\n")
    elif wi == wlen - 1: #If it is the word before last we add sil as the last node
      nodes.append("I="+str(N)+" W=sil\n")
    elif wi == wlen:
      #If this is the last word we are done
      break
    w_end_node = N
    N+=1
  
  for node in nodes:
    slf.append(node)
  slf.append("# List arcs: J=arc-number, S=start-node, E=end-node\n")
  for arc in arcs:
    slf.append(arc)
  #Fix the line with N and L
  slf[1] = "N="+str(len(nodes))+" L="+str(len(arcs))+"\n"
  
  return slf

#Make nodes and arcs for a word starting at node num N and arc num L
#Returns nodes and arcs with the added new nodes and arcs
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
