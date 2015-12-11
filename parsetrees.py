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

class stanfordPcfgTree:
  def __init__(self, label=None, parent=None, children=[]):
    self.label = label
    self.parent = parent
    self.children = []
    self.list = []
  
  def make_tree(self, parenthesis_string):
    #Prep a lsit of the right format
    tree = parenthesis_string.replace("(", " ( ").replace(")", " ) ").split()
    tmp = []
    #Combine words with their pos tag
    for i, x in enumerate(tree):
      if x not in ["(", ")"]:
        if tree[i-1] not in ["(", ")"]:
          tmp.append(tree[i-1]+"-"+x)
        elif tree[i+1] in ["(", ")"]:
          tmp.append(x)
      else:
          tmp.append(x)
    tree = tmp
    #Parse the list
    stack = []
    index = 0
    while index < len(tree):
      if tree[index] is '(':
        if self.label is None:
          self.label = tree[index+1]
          index = index+1
        else:
          if len(stack) == 0:
            stack.append(stanfordPcfgTree(tree[index+1], self.label))
            index = index+1
          else:
              stack.append(stanfordPcfgTree(tree[index+1], stack[len(stack)-1].label))
              index = index+1
      elif tree[index] is ')':
        if len(stack) == 1:
          self.children.append(stack.pop())
          #Add parents proper and child pos info
          self.add_parents_info()
          return
        else:
          stack[len(stack)-2].children.append(stack.pop())
      index = index+1
  
  def add_parents_info(self):
    if self.parent == None:
      self.parent = "xx"
      self.pos_in_parent = "xx"
      self.num_siblings = "xx"
    l = len(self.children)
    for i, child in enumerate(self.children):
      child.parent = self
      child.pos_in_parent = i
      child.num_siblings = l
      child.add_parents_info()
  
  #When using include_punct pass a list of the punctuation to include or True if any punctuation.
  #If include_punct is passed punct_as_pause will make each of these return as the specified pos.
  def get_leafs(self, include_punct=None):
    leafs = []
    for child in self.children:
      if child.children is None or len(child.children) == 0:
          if child.label[0].isalpha(): #If it is not punctuation
            leafs.append(child)
          elif include_punct: #If it is not None
            if include_punct == True:
              leafs.append(child)
            elif child.label[0] in include_punct:
              leafs.append(child)
      else:
        leafs += child.get_leafs(include_punct)
    return leafs

#Returns an empty "fake" stanford parse
def get_fake_stanford_pcfg_parse():
  fake_tree = stanfordPcfgTree()
  fake_tree.label = "xx"
  fake_tree.parent = "xx"
  fake_tree.pos_in_parent = "xx"
  fake_tree.num_siblings = "xx"
  return fake_tree

class stanfordDependencyTree:
  def __init__(self, label=None, parent=None, parent_relation=None, utt_pos=None):
    self.label = label
    self.utt_pos = utt_pos
    self.parent_relation = parent_relation
    self.parent = parent
    self.children = None
  
  def __repr__(self):
    return '{}: {} {}'.format(self.__class__.__name__,
                              self.label,
                              self.utt_pos)
  
  #While this can be accessed directly this is useful for sorting by utt_pos
  def get_utt_pos(self, item):
    return item.utt_pos
  
  def make_tree(self, relation_list):
    #First we make a dictionary of each word and what relations it is the parent of
    rel_dct = {}
    for line in relation_list:
      #Just a check if there is an empty line
      if line == "":
        continue
      #Make whitespace the delimiter
      line = line.replace("(", " ")
      line = line.replace(", ", " ")
      line = line.replace(")", "")
      line = line.split()
      #Middle is the parent word
      #First is the relation type
      #Last is the child word
      if line[1] not in rel_dct:
        rel_dct[line[1]] = [(line[0], line[2])]
      else:
        rel_dct[line[1]] += [(line[0], line[2])]
    self.label = "ROOT"
    self.utt_pos = 0
    self.parent_relation = "xx"
    self.make_children(rel_dct, self)
  
  #Recursively creates the children of a tree
  def make_children(self, rel_dct, parent):
    #The key is based on both label and utt_pos (the same word may reappear but will have different utt_pos so this is important)
    key = parent.label+"-"+str(parent.utt_pos)
    if key in rel_dct:
      parent.children = []
      for child in rel_dct[key]:
        label, utt_pos = child[1].split("-")
        c = stanfordDependencyTree(label=label, parent=parent, parent_relation=child[0], utt_pos=int(utt_pos))
        parent.children.append(c)
        self.make_children(rel_dct, c)
  
  #Returns the leafs of the tree
  def get_leafs(self):
    leafs = []
    for child in self.children:
      if child.children is None:
          leafs.append(child)
      else:
        leafs += child.get_leafs()
    return leafs
  
  #Returns the nodes of the tree below the current node
  #So if given the root node it returns all nodes except the root.
  #If utt_sorted is True it will return them ordered by the word
  #utt pos not by root children pos.
  def get_nodes(self, utt_sorted=False):
    if self.parent_relation in ["xx", None]:
      nodes = []
    else:
      nodes = [self]
    for child in self.children:
      if child.children is None:
          nodes.append(child)
      else:
        nodes += child.get_nodes(utt_sorted)
    if utt_sorted == True:
      return sorted(nodes, key=self.get_utt_pos)
    return nodes
  
  
  #Recursively prints the tree with tab indentation for levels
  def print_tree(self, tabs=0):
    tab = ""
    for x in range(tabs):
      tab += "\t"
    print tab+self.label
    print tab+self.parent
    print tab+self.parent_relation
    if self.children != None:
      for child in self.children:
        print child.print_tree(tabs+1)

