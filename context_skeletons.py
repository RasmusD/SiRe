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

import sys, context_utils
from collections import OrderedDict

#This contains the context skeletons which ensure compatibility between
#question sets and full context labels. These also dump out the resulting
#context after being filled.
#A few conventions.
#Each context is initialised with its type. This is used by
#the question set generator to know which type of questions to generate.
#The following types are valid:
#"bool" = A yes/no question, examples are "Is this a @ phoneme?" or "Is this phoneme a
#         consonant?"
#"float" = A question which has a value which can be checked for higher than, lower than etc.
#          an example would be "Phoneme relational forward position in syllable".
#          The value of it must be a float type and multipliable with 100 to yield an int
#          (i.e. 0.01 is valid, 0.011 is not and will be rounded to two decimal places).
#"int" = A question which has a value which can be checked for higher than, lower than etc.
#        an example would be "Phoneme relational forward position in syllable".
#        The value of it must be an int type.
#None = This is not something any questions should be made about, i.e. start/end times.
#OrderedDict() = Only used for the context dict. This will be ignored for generic question
#                making.
#Any other type = Yields an error when generating a question set.
#If "xx" is in typename = "xx" is a valid value for this type. This is only valid for float
#and int. (xx is always valid for bool type)
#If "0" is in typename = Signals that 0 value is not exclusive to silence segments. This is
#only valid for float and int.
#If "utt" is in typename = Signals that this question should be included in the GV question set (which is only at the utt level).


class Relational(object):
  """Contains the set of variables used in the relational context set."""
  def __init__(self, phoneme_features):
    #Container for all contexts given a value
    #The whole thing could be built up around this dict
    #but I think it more clear not to.
    self.added_contexts = OrderedDict()
    ##### Timings #####
    self.start = None
    self.end = None
    ##### Phoneme level features #####
    #Left left phoneme
    self.llp = "bool"
    #Left phoneme
    self.lp = "bool"
    #Current phoneme
    self.cp = "bool"
    #Right phoneme
    self.rp = "bool"
    #Right right phoneme
    self.rrp = "bool"
    #Forward syllable pos
    self.pfwsp = "float"
    #Backward syllable pos
    self.pbwsp = "float"
    #Forward word pos
    self.pfwwp = "float"
    #Backward word pos
    self.pbwwp = "float"
    #Left Phone stress
    #self.lps = "intxx0"
    #Current Phone stress
    #self.cps = "int0"
    #Right Phone stress
    #self.rps = "intxx0"
    #Phone features
    for feat in phoneme_features.get_feature_lists():
      #Left Phoneme feats
      setattr(self, "lp"+feat, "bool")
      #Cur Phoneme feats
      setattr(self, "cp"+feat, "bool")
      #Right Phoneme feats
      setattr(self, "rp"+feat, "bool")
    #Phonemes to next stressed phoneme
    #self.pnsp = "intxx"
    #Phonemes from previous stressed phoneme
    #self.ppsp = "intxx"
    
    ##### Syllable level features #####
    #Left syllable stress
    self.lss = "intxx0"
    #Current syllable stress
    self.css = "int0"
    #Right syllable stress
    self.rss = "intxx0"
    #L Syllable number of phonemes
    self.lsnp = "intxx"
    #C Syllable number of phonemes
    self.csnp = "int"
    #R Syllable number of phonemes
    self.rsnp = "intxx"
    #Syllable vowel id
    self.svid = "bool"
    #Syllable vowel features
    for feat in phoneme_features.get_feature_lists():
      setattr(self, "sv"+feat, "bool")
    #Syllable forward pos in word
    self.sfwwp = "float"
    #Syllable backward pos in word
    self.sbwwp = "float"
    #Syllables to next stressed syll
    self.snss = "intxx"
    #Syllables from previous stressed syll
    self.spss = "intxx"
    
    ##### Word level features #####
    #Word number of phonemes
    self.wnp = "intxx"
    #Word number of syllables
    self.wns = "intxx"
    #Forward pos in utt
    self.wfwup = "float"
    #Backward pos in utt
    self.wbwup = "float"
    
    ##### Utterance level features #####
    #Utterance number of phonemes
    self.unp = "intutt"
    #Utterance number of syllables
    self.uns = "intutt"
    #Utterance number of words
    self.unw = "intutt"
    ##### Experimental! #####
    #Is this read or spontaneous data?
    self.ut = "bool"
  
  #Can only add one context value to the dict.
  #Overwrites old values present.
  #Used for phoneme context string generation.
  #Also checks if the type of the value to add is valid.
  def add(self, v_name, value):
    if hasattr(self, v_name):
      if context_utils.check_value(self, v_name, value):
        self.added_contexts[v_name] = value
    else:
      print "Tried to add context which does not exist in skeleton! "+v_name
      sys.exit()
  
  #Adds values in a list to the dict.
  #Ignores the initial value and only adds
  #to to the dict in a list for each key.
  #Used for question set generation.
  #Also checks if the type of the value to add is valid.
  def add_multiple(self, v_name, value):
    if hasattr(self, v_name):
      if context_utils.check_value(self, v_name, value):
        if v_name not in self.added_contexts:
          self.added_contexts[v_name] = [value]
        else:
          self.added_contexts[v_name] += [value]
    else:
      print "Tried to add context which does not exist in skeleton! "+v_name
      sys.exit()
  
  #Returns a context string based on what is in added_contexts.
  def get_context_string(self, HHEd_fix=False):
    s = ""
    s += str(self.added_contexts["start"]) + " "
    s += str(self.added_contexts["end"]) + " "
    for key in self.added_contexts:
      if key in ["start", "end"]:
        continue
      if "float" in getattr(self, key):
        s += "|"+key+":"+context_utils.strintify(self.added_contexts[key])
      else:
        s += "|"+key+":"+str(self.added_contexts[key])
    if HHEd_fix == True:
      s = s.replace("cp:"+self.added_contexts["cp"], "cp:-"+self.added_contexts["cp"]+"+")
    return s+"|"

class RelationalStanford(Relational):
  """An extension of the relational base set including information from a stanford parsing of the sentence."""
  def __init__(self, phoneme_features):
    super(RelationalStanford, self).__init__(phoneme_features)
    ###### Stanford Parse Information ######
    #Part of speech
    self.lwpos = "bool"
    self.cwpos = "bool"
    self.rwpos = "bool"
    #Word parent phrase
    self.wpp = "bool"
    #Word grandpparent phrase
    self.wgpp = "bool"
    #Word greatgrandparent phrase
    self.wggpp = "bool"
    #Word relational position in parent phrase
    #Forward
    self.wfwrppp = "float"
    #Backward
    self.wbwrppp = "float"
    #Word relational position in grandparent phrase
    #Forward
    self.wfwrgppp = "float"
    #Backward
    self.wbwrgppp = "float"
    #Word relational position in greatgrandparent phrase
    #Forward
    self.wfwrggppp = "float"
    #Backward
    self.wbwrggppp = "float"
