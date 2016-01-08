##########################################################################
#Copyright 2016 Rasmus Dall                                              #
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

#A class for all part of speech related methods. Does NOT include a POS tagger (yet).

from error_messages import SiReError

#Checks if a word is a content word in the definition of Festivals english_guess_pos method in pos.scm
#Exists for compatibility reasons (to enable output of exact festival featureset)
def is_festival_content(pos):
  if pos in ["in", "to", "det", "md", "cc", "wp", "pps", "aux", "punc"]:
    return False
  return True

def get_festival_general_pos(pos):
  if is_festival_content(pos):
    return "content"
  return pos

#An implementation of the english_guess_pos method from festival in pos.scm
#Festival description of method:
#"An assoc-list of simple part of speech tag to list of words in that
#class. This basically only contains closed class words all other 
#words may be assumed to be content words.  This was built from information
#in the f2b database and is used by the ffeature gpos."
#Pause phonemes get a "punc" tag for compatibility with sil_as_punc option.
def simple_festival_pos_predict(utt):
  if utt.txtloaded != True:
    raise SiReError("We cannot be sure that we know each word id correctly! It may just be phonemes strung together!")
  for word in utt.words:
    if word.id in ["of", "for", "in", "on", "that", "with", "by", "at", "from", "as", "if", "that", "against", "about", "before", "because", "if", "under", "after", "over", "into", "while", "without", "through", "new", "between", "among", "until", "per", "up", "down"]:
      word.pos = "in"
    elif word.id == "to":
      word.pos = "to"
    elif word.id in ["the", "a", "an" ,"no" ,"some", "this", "that", "each", "another", "those", "every", "all", "any", "these" ,"both", "neither", "no", "many"]:
      word.pos = "det"
    elif word.id in ["will", "may", "would", "can", "could", "should", "must", "ought", "might"]:
      word.pos = "md"
    elif word.id in ["and", "but", "or", "plus", "yet", "nor"]:
      word.pos = "cc"
    elif word.id in ["who", "what", "where", "how", "when"]:
      word.pos = "wp"
    elif word.id in ["her", "his", "their", "its", "our" ,"their", "its", "mine"]:
      word.pos = "pps"
    elif word.id in ["is", "am", "are", "was", "were", "has", "have", "had", "be"]:
      word.pos = "aux"
    elif word.id in [".", ",", ":", ";", "\"", "'", "(", "?", ")", "!"]:
      word.pos = "punc"
    elif word.id in utt.phoneme_features.get_sil_phonemes():
      word.pos = "punc"
    else:
      word.pos = "content"
