class stanfordtree:
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
            stack.append(stanfordtree(tree[index+1], self.label))
            index = index+1
          else:
              stack.append(stanfordtree(tree[index+1], stack[len(stack)-1].label))
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
  
  def get_leafs(self, include_punct=False):
    leafs = []
    for child in self.children:
      if child.children is None or len(child.children) == 0:
          if include_punct == True:
            leafs.append(child)
          elif child.label[0].isalpha():
            leafs.append(child)
      else:
        leafs += child.get_leafs()
    return leafs

#Returns an empty "fake" stanford parse
def get_fake_stanford_parse():
  fake_tree = stanfordtree()
  fake_tree.label = "xx"
  fake_tree.parent = "xx"
  fake_tree.pos_in_parent = "xx"
  fake_tree.num_siblings = "xx"
  return fake_tree
