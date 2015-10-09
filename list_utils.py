#Additional list related methods

import itertools

#Removes duplicates in a list of lists.
#alternative methods at http://stackoverflow.com/questions/2213923/python-removing-duplicates-from-a-list-of-lists
def unique_list_of_lists(inlist):
  inlist.sort()
  return list(inlist for inlist,_ in itertools.groupby(inlist))
