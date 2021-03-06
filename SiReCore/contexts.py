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

import context_skeletons, copy, pos, prosody
from context_utils import strintify
from context_utils import strfloatify
from context_utils import to_relational
from context_utils import get_pos_cat
from context_utils import get_dep_pos_cat
from parsetrees import dep_distance_in_arcs
from error_messages import SiReError

#This contains the methods for creating a variety of context types from an utterance.

def Categorical(phoneme):
  """Creates a categorical context string of the given phoneme."""
  c = context_skeletons.Categorical(phoneme.parent_utt.phoneme_features)
  add_categorical(c, phoneme)
  add_festival(c, phoneme)
  return c

def CategoricalStanfordPcfg(phoneme):
  """Creates a categorical context string of the given phoneme."""
  c = context_skeletons.CategoricalStanfordPcfg(phoneme.parent_utt.phoneme_features)
  add_categorical(c, phoneme)
  #We have proper pos tags to simplify
  add_festival(c, phoneme, False)
  add_categorical_stanford_pcfg(c, phoneme)
  return c

def CategoricalStanfordDependency(phoneme):
  """Creates a categorical context string of the given phoneme."""
  c = context_skeletons.CategoricalStanfordDependency(phoneme.parent_utt.phoneme_features)
  add_categorical(c, phoneme)
  add_festival(c, phoneme)
  add_categorical_stanford_dependency(c, phoneme)
  return c

def Relational(phoneme):
  """Creates a relational context string of the given phoneme."""
  c = context_skeletons.Relational(phoneme.parent_utt.phoneme_features)
  add_relational(c, phoneme)
  add_festival(c, phoneme)
  return c

def RelationalStanfordPcfg(phoneme):
  """An extension of the relational base set including information from a stanford parsing of the sentence."""
  c = context_skeletons.RelationalStanfordPcfg(phoneme.parent_utt.phoneme_features)
  add_relational(c, phoneme)
  #We have proper pos tags to simplify
  add_festival(c, phoneme, False)
  add_relational_stanford_pcfg(c, phoneme)
  return c

def RelationalStanfordDependency(phoneme):
  """An extension of the relational base set including information from a stanford parsing of the sentence."""
  c = context_skeletons.RelationalStanfordDependency(phoneme.parent_utt.phoneme_features)
  add_relational(c, phoneme)
  add_festival(c, phoneme)
  add_relational_stanford_dependency(c, phoneme)
  return c

def Emphasis(phoneme):
    """Creates emphasis features based on the absolute context type"""
    c = context_skeletons.Emphasis(phoneme.parent_utt.phoneme_features)
    add_absolute(c, phoneme)
    add_festival(c, phoneme)
    add_emphasis(c, phoneme)
    return c

#This set is equivalent to what Festival does.
def Absolute(phoneme):
  """Creates an absolute context string of the given phoneme."""
  c = context_skeletons.Absolute(phoneme.parent_utt.phoneme_features)
  add_absolute(c, phoneme)
  add_festival(c, phoneme)
  return c

def AbsoluteStanfordPcfg(phoneme):
  """Creates an absolute context string of the given phoneme including information from a stanford parse."""
  c = context_skeletons.AbsoluteStanfordPcfg(phoneme.parent_utt.phoneme_features)
  add_absolute(c, phoneme)
  #We have proper pos tags to simplify
  add_festival(c, phoneme, False)
  add_absolute_stanford_pcfg(c, phoneme)
  return c

def AbsoluteStanfordDependency(phoneme):
  """Creates an absolute context string of the given phoneme including information from a stanford parse."""
  c = context_skeletons.AbsoluteStanfordDependency(phoneme.parent_utt.phoneme_features)
  add_absolute(c, phoneme)
  add_festival(c, phoneme)
  add_absolute_stanford_dependency(c, phoneme)
  return c

def CategoricalStanfordCombined(phoneme):
  """Creates an absolute context string of the given phoneme including information from a stanford parse."""
  c = context_skeletons.CategoricalStanfordCombined(phoneme.parent_utt.phoneme_features)
  add_categorical(c, phoneme)
  #We have proper pos tags to simplify
  add_festival(c, phoneme, False)
  add_categorical_stanford_pcfg(c, phoneme)
  add_categorical_stanford_dependency(c, phoneme)
  return c

def RelationalStanfordCombined(phoneme):
  """Creates an absolute context string of the given phoneme including information from a stanford parse."""
  c = context_skeletons.RelationalStanfordCombined(phoneme.parent_utt.phoneme_features)
  add_relational(c, phoneme)
  #We have proper pos tags to simplify
  add_festival(c, phoneme, False)
  add_relational_stanford_pcfg(c, phoneme)
  add_relational_stanford_dependency(c, phoneme)
  return c

def AbsoluteStanfordCombined(phoneme):
  """Creates an absolute context string of the given phoneme including information from a stanford parse."""
  c = context_skeletons.AbsoluteStanfordCombined(phoneme.parent_utt.phoneme_features)
  add_absolute(c, phoneme)
  #We have proper pos tags to simplify
  add_festival(c, phoneme, False)
  add_absolute_stanford_pcfg(c, phoneme)
  add_absolute_stanford_dependency(c, phoneme)
  return c

def add_basic(context_skeleton, phoneme):
  """Adds the basic context set to a context skeleton. What is considered basic is currently what overlaps between relational and absolute. If the skeleton does not support the set this will fail."""
  utt = phoneme.parent_utt
  phoneme_features = utt.phoneme_features
  c = context_skeleton
  syll = phoneme.parent_syllable
  word = phoneme.parent_word
  ##### Timings #####
  ##We must use the add method to ensure that the context skeleton already contains this context.
  c.add("start", str(phoneme.start))
  c.add("end", str(phoneme.end))
  ##### Phoneme level features #####
  #print "Adding phoneme level features to {0} in {1}".format(phoneme.id, phoneme.parent_utt.id)
  p_pos_in_utt = phoneme.pos_in_utt()
  p_pos_in_word = phoneme.pos_in_word()
  p_pos_in_syllable = phoneme.pos_in_syllable()
  #Left left phoneme
  if p_pos_in_utt > 1:
    llp = utt.phonemes[p_pos_in_utt - 2].id
  else:
    llp = "xx"
  c.add("llp", llp)
  #Left phoneme
  if p_pos_in_utt > 0:
    lp = utt.phonemes[p_pos_in_utt - 1].id
  else:
    lp = "xx"
  c.add("lp", lp)
  #Current phoneme
  c.add("cp", phoneme.id)
  #Right phoneme
  #Minus one as the pos_in_utt starts at 0
  diff = len(utt.phonemes) - p_pos_in_utt - 1
  if diff > 0:
    rp = utt.phonemes[p_pos_in_utt + 1].id
  else:
    rp = "xx"
  c.add("rp", rp)
  #Right right phoneme
  if diff > 1:
    rrp = utt.phonemes[p_pos_in_utt + 2].id
  else:
    rrp = "xx"
  c.add("rrp", rrp)
  #Left phoneme stress
  #if lp != "xx":
  #  c.add("lps", str(utt.phonemes[p_pos_in_utt - 1].stress))
  #else:
  #  c.add("lps", "xx")
  #Current phoneme stress
  #c.add("cps", str(phoneme.stress))
  #Right phoneme stress
  #if rp != "xx":
  #  c.add("rps", str(utt.phonemes[p_pos_in_utt + 1].stress))
  #else:
  #  c.add("rps", "xx")
  #Phonemes to next stressed phoneme
  #i = p_pos_in_utt + 1
  #pnsp = "xx"
  #while i < len(utt.phonemes):
  #  if utt.phonemes[i].stress not in ["xx", 0]:
  #    pnsp = str(i - p_pos_in_utt)
  #    break
  #  else:
  #    i += 1
  #c.add("pnsp", pnsp)
  #Phonemes from previous stressed phoneme
  #i = p_pos_in_utt - 1
  #ppsp = "xx"
  #while i > 0:
  #  if utt.phonemes[i].stress not in ["xx", 0]:
  #    ppsp = str(p_pos_in_utt - i)
  #    break
  #  else:
  #    i -= 1
  #c.add("ppsp", ppsp)
  #Phoneme features
  lpf = phoneme_features.get_phoneme_feats_dict(lp)
  cpf = phoneme_features.get_phoneme_feats_dict(phoneme.id)
  rpf = phoneme_features.get_phoneme_feats_dict(rp)
  for feat in phoneme_features.get_feature_lists():
    #Left phoneme feats
    c.add("lp"+feat, lpf[feat])
    #Current phoneme feats
    c.add("cp"+feat, cpf[feat])
    #Right phoneme feats
    c.add("rp"+feat, rpf[feat])

  ##### Syllable level features #####
  #print "Adding syllable level features to {0} in {1}".format(phoneme.id, phoneme.parent_utt.id)
  s_pos_in_utt = syll.pos_in_utt()
  s_pos_in_word = syll.pos_in_word()
  if s_pos_in_utt > 0:
    ls = utt.syllables[s_pos_in_utt - 1]
  else:
    ls = "xx"
  #Minus 1 as pos_in_utt starts at 0
  diff = utt.num_syllables() - s_pos_in_utt - 1
  if diff > 0:
    rs = utt.syllables[s_pos_in_utt + 1]
  else:
    rs = "xx"
  #L Syllable stress
  if ls != "xx":
    c.add("lss", str(ls.stress))
  else:
    c.add("lss", "xx")
  #C Syllable stress
  if syll.stress == "xx":
    print "Warning! Current syllable stress is xx!"
    print "Should only happen when converting hts labs"
    print "Changing to 0 and continuing."
    c.add("css", "0")
  else:
    c.add("css", str(syll.stress))
  #R Syllable stress
  if rs != "xx":
    c.add("rss", str(rs.stress))
  else:
    c.add("rss", "xx")
  #Syllables to next stressed syllable
  i = s_pos_in_utt + 1
  snss = "xx"
  while i < utt.num_syllables():
    if utt.syllables[i].stress not in ["xx", 0]:
      snss = str(i - s_pos_in_utt)
      break
    else:
      i += 1
  c.add("snss", snss)
  #Syllables from previous stressed syllable
  i = s_pos_in_utt - 1
  spss = "xx"
  while i > 0:
    if utt.syllables[i].stress not in ["xx", 0]:
      spss = str(s_pos_in_utt - i)
      break
    else:
      i -= 1
  c.add("spss", spss)
  #L Syllable number of phonemes
  if ls != "xx":
    c.add("lsnp", str(ls.num_phonemes()))
  else:
    c.add("lsnp", "xx")
  #C Syllable number of phonemes
  c.add("csnp", str(syll.num_phonemes()))
  #R Syllable number of phonemes
  if rs != "xx":
    c.add("rsnp", str(rs.num_phonemes()))
  else:
    c.add("rsnp", "xx")
  #Syll vowel id
  c.add("svid", syll.vowel_id)
  #Syll Vowel Feats
  v_dct = phoneme_features.get_phoneme_feats_dict(syll.vowel_id)
  for feat in phoneme_features.get_feature_lists():
    c.add("sv"+feat, v_dct[feat])

  ##### Word level features #####
  #print "Adding word level features to {0} in {1}".format(phoneme.id, phoneme.parent_utt.id)
  w_pos_in_utt = word.pos_in_utt()
  #Word number of phonemes
  c.add("wnp", str(word.num_phonemes()))
  #Word number of syllables
  c.add("wns", str(word.num_syllables()))

  ##### Utterance level features #####
  #Phonemes in utterance
  c.add("unp", str(utt.num_phonemes()))
  #Syllables in utterance
  c.add("uns", str(utt.num_syllables()))
  #Words in utterance
  c.add("unw", str(utt.num_words()))

  ##### EXPERIMENTAL DO NOT COMMIT! #####
#  c.add("ut", "read")

def add_emphasis(context_skeleton, phoneme):
    """Adds the emphasis context set"""
    c = context_skeleton
    word = phoneme.parent_word
    utt = phoneme.parent_utt
    ### Word Level Emphasis ###
    #Word emphasis
    c.add("wemph", str(word.get_emph()))
    #Next word emphasis
    c.add("fwemph", str(word.forward_emph()))
    #Previous word emphasis
    c.add("bwemph", str(word.backward_emph()))
    # #Words until next emphasised word
    c.add("wnew", str(word.next_emph()))
    # #Words until last emphasised word
    c.add("wpew", str(word.prev_emph()))

    ### Utterance Level Emphasis ###
    #Emphasised words in utterance
    c.add("unew", str(utt.num_emph_words()))

def add_categorical(context_skeleton, phoneme):
  """Adds the categorical context set. Categorical means that positions in segments are categorical."""
  utt = phoneme.parent_utt
  phoneme_features = utt.phoneme_features
  c = context_skeleton
  syll = phoneme.parent_syllable
  word = phoneme.parent_word
  #Add the basic features
  add_basic(c, phoneme)
  #Get the R and L phonemes
  p_pos = phoneme.pos_in_utt()
  try:
    rp = utt.phonemes[p_pos+1]
  except IndexError:
    rp = None
  if phoneme.pos_in_utt() > 0:
    lp = utt.phonemes[p_pos-1]
  else:
    lp = None

  #Add current phoneme syll and word pos
  #Phoneme pos in syll
  if phoneme.id in phoneme_features.get_sil_phonemes():
    c.add("cpsp", "xx")
    c.add("cpwp", "xx")
  else:
    c.add("cpsp", get_pos_cat(phoneme.pos_in_syllable(), syll.num_phonemes()))
    c.add("cpwp", get_pos_cat(phoneme.pos_in_word(), word.num_phonemes()))
  #Add left phoneme syll and word pos
  if lp == None or lp.id in phoneme_features.get_sil_phonemes():
    c.add("lpsp", "xx")
    c.add("lpwp", "xx")
  else:
    c.add("lpsp", get_pos_cat(lp.pos_in_syllable(), lp.parent_syllable.num_phonemes()))
    c.add("lpwp", get_pos_cat(lp.pos_in_word(), lp.parent_word.num_phonemes()))
  #Add right phoneme syll and word pos
  if rp == None or rp.id in phoneme_features.get_sil_phonemes():
    c.add("rpsp", "xx")
    c.add("rpwp", "xx")
  else:
    c.add("rpsp", get_pos_cat(rp.pos_in_syllable(), rp.parent_syllable.num_phonemes()))
    c.add("rpwp", get_pos_cat(rp.pos_in_word(), rp.parent_word.num_phonemes()))
  #Add syllable word pos
  s_pos = phoneme.parent_syllable.pos_in_utt()
  try:
    rs = utt.syllables[s_pos+1]
  except IndexError:
    rs = None
  if syll.pos_in_utt() > 0:
    ls = utt.syllables[s_pos-1]
  else:
    ls = None
  #C Syllable pos in word
  c.add("cswp", get_pos_cat(syll.pos_in_word(), syll.parent_word.num_syllables()))
  #L Syllable pos in word
  if ls == None:
    c.add("lswp", "xx")
  else:
    c.add("lswp", get_pos_cat(ls.pos_in_word(), ls.parent_word.num_syllables()))
  #R Syllable pos in word
  if rs == None:
    c.add("rswp", "xx")
  else:
    c.add("rswp", get_pos_cat(rs.pos_in_word(), rs.parent_word.num_syllables()))
  #Add pos in utt
  #Word pos in utterance
  w_pos = phoneme.parent_word.pos_in_utt()
  try:
    rw = utt.words[w_pos+1]
  except IndexError:
    rw = None
  if word.pos_in_utt() > 0:
    lw = utt.words[w_pos-1]
  else:
    lw = None
  #C Word pos in utt
  c.add("cwup", get_pos_cat(word.pos_in_utt(), word.parent_utt.num_words(), True))
  #L Word pos in utt
  if lw == None:
    c.add("lwup", "xx")
  else:
    c.add("lwup", get_pos_cat(lw.pos_in_utt(), lw.parent_utt.num_words(), True))
  #R Word pos in utt
  if rw == None:
    c.add("rwup", "xx")
  else:
    c.add("rwup", get_pos_cat(rw.pos_in_utt(), rw.parent_utt.num_words(), True))

def add_relational(context_skeleton, phoneme):
  """Adds the relational context set. Relational means that positions in segments are relational."""
  utt = phoneme.parent_utt
  phoneme_features = utt.phoneme_features
  c = context_skeleton
  syll = phoneme.parent_syllable
  word = phoneme.parent_word
  #Add the basic features
  add_basic(c, phoneme)
  #Add phoneme syll and word pos
  if phoneme.id in phoneme_features.get_sil_phonemes():
    #Phone forward pos in syll
    c.add("pfwsp", str(0.0))
    #Phone backward pos in syll
    c.add("pbwsp", str(0.0))
    #Phone forward pos in word
    c.add("pfwwp", str(0.0))
    #Phone backward pos in word
    c.add("pbwwp", str(0.0))
  else:
    #Phone forward pos in syll
    s_n_p = syll.num_phonemes()
    c.add("pfwsp", str(to_relational(phoneme.pos_in_syllable(), s_n_p - 1, True)))
    #Phone backward pos in syll
    c.add("pbwsp", str(to_relational(phoneme.pos_in_syllable(), s_n_p - 1, False)))
    #Phone forward pos in word
    w_n_p = word.num_phonemes()
    c.add("pfwwp", str(to_relational(phoneme.pos_in_word(), w_n_p - 1, True)))
    #Phone backward pos in word
    c.add("pbwwp", str(to_relational(phoneme.pos_in_word(), w_n_p - 1, False)))
  #Add syllable forward and backward word pos
  #If this is a silence segment we have no relational pos.
  if phoneme.id in phoneme_features.get_sil_phonemes():
    #Syllable forward pos in word
    c.add("sfwwp", str(0.0))
    #Syllable backward pos in word
    c.add("sbwwp", str(0.0))
  else:
    #Syllable forward pos in word
    w_n_s = syll.parent_word.num_syllables()
    c.add("sfwwp", str(to_relational(syll.pos_in_word(), w_n_s - 1, True)))
    #Syllable backward pos in word
    c.add("sbwwp", str(to_relational(syll.pos_in_word(), w_n_s - 1, False)))
  #Add pos in utt
  #Word forward pos in utterance
  u_n_w = word.parent_utt.num_words()
  c.add("wfwup", str(to_relational(word.pos_in_utt(), u_n_w - 1, True)))
  #Word forward pos in utterance
  c.add("wbwup", str(to_relational(word.pos_in_utt(), u_n_w - 1, False)))

def add_absolute(context_skeleton, phoneme):
  """Adds the absolute context set. Absolute means that positions in segmetns are absolute values."""
  utt = phoneme.parent_utt
  phoneme_features = utt.phoneme_features
  c = context_skeleton
  syll = phoneme.parent_syllable
  word = phoneme.parent_word
  #Add the basic features
  add_basic(c, phoneme)
  #Add phoneme syll and word pos
  #We remove one as the pos_in start from 0
  s_n_p = syll.num_phonemes() - 1
  c.add("pfwsp", str(phoneme.pos_in_syllable()))
  #Phone backward pos in syll
  c.add("pbwsp", str(s_n_p-phoneme.pos_in_syllable()))
  #Phone forward pos in word
  w_n_p = word.num_phonemes() - 1
  c.add("pfwwp", str(phoneme.pos_in_word()))
  #Phone backward pos in word
  c.add("pbwwp", str(w_n_p-phoneme.pos_in_word()))
  #Add syllable forward and backward word pos
  #If this is a silence segment we have no relational pos.
  w_n_s = syll.parent_word.num_syllables() - 1
  c.add("sfwwp", str(syll.pos_in_word()))
  #Syllable backward pos in word
  c.add("sbwwp", str(w_n_s - syll.pos_in_word()))
  #Add pos in utt
  #Word forward pos in utterance
  u_n_w = word.parent_utt.num_words() - 1
  c.add("wfwup", str(word.pos_in_utt()))
  #Word forward pos in utterance
  c.add("wbwup", str(u_n_w - word.pos_in_utt()))

def add_basic_stanford_pcfg(context_skeleton, phoneme):
  """Adds the basic elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  w = phoneme.parent_word
  ###### Stanford Parse Information ######
  #Word parent phrase
  c.add("wpp", w.parent_phrase.label)
  #Word grandpparent phrase
  c.add("wgpp", w.grandparent_phrase.label)
  #Word greatgrandparent phrase
  c.add("wggpp", w.greatgrandparent_phrase.label)

def add_relational_stanford_pcfg(context_skeleton, phoneme):
  """Adds the relational elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  #Add basic info
  add_basic_stanford_pcfg(c, phoneme)
  #Word
  w = phoneme.parent_word
  #Word relational position in parent phrase
  c.add("wfwrppp", str(to_relational(w.parent_phrase.pos_in_parent, w.parent_phrase.num_siblings, True, True)))
  c.add("wbwrppp", str(to_relational(w.parent_phrase.pos_in_parent, w.parent_phrase.num_siblings, False, True)))
  #Word relational position in grandparent phrase
  c.add("wfwrgppp", str(to_relational(w.grandparent_phrase.pos_in_parent, w.grandparent_phrase.num_siblings, True, True)))
  c.add("wbwrgppp", str(to_relational(w.grandparent_phrase.pos_in_parent, w.grandparent_phrase.num_siblings, False, True)))
  #Word relational position in greatgrandparent phrase
  c.add("wfwrggppp", str(to_relational(w.greatgrandparent_phrase.pos_in_parent, w.greatgrandparent_phrase.num_siblings, True, True)))
  c.add("wbwrggppp", str(to_relational(w.greatgrandparent_phrase.pos_in_parent, w.greatgrandparent_phrase.num_siblings, False, True)))

def add_categorical_stanford_pcfg(context_skeleton, phoneme):
  """Adds the categorical elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  #Add basic info
  add_basic_stanford_pcfg(c, phoneme)
  #Word
  rw = phoneme.parent_word.get_next_word()
  cw = phoneme.parent_word
  lw = phoneme.parent_word.get_prev_word()
  utt = phoneme.parent_utt
  #Right word categorical position in parent, grandparent and greatgrandparent phrase
  if rw == "xx":
    c.add("rwcppp", "xx")
    c.add("rwcgppp", "xx")
    c.add("rwcggppp", "xx")
  else:
    c.add("rwcppp", get_pos_cat(rw.pos_in_utt(), len(utt.words), with_sil=True))
    c.add("rwcgppp", get_pos_cat(rw.pos_in_utt(), len(utt.words), with_sil=True))
    c.add("rwcggppp", get_pos_cat(rw.pos_in_utt(), len(utt.words), with_sil=True))
  #Current word categorical position in parent, grandparent and greatgrandparent phrase
  c.add("cwcppp", get_pos_cat(cw.pos_in_utt(), len(utt.words), with_sil=True))
  c.add("cwcgppp", get_pos_cat(cw.pos_in_utt(), len(utt.words), with_sil=True))
  c.add("cwcggppp", get_pos_cat(cw.pos_in_utt(), len(utt.words), with_sil=True))
  #Left word categorical position in parent, grandparent and greatgrandparent phrase
  if lw == "xx":
    c.add("lwcppp", "xx")
    c.add("lwcgppp", "xx")
    c.add("lwcggppp", "xx")
  else:
    c.add("lwcppp", get_pos_cat(lw.pos_in_utt(), len(utt.words), with_sil=True))
    c.add("lwcgppp", get_pos_cat(lw.pos_in_utt(), len(utt.words), with_sil=True))
    c.add("lwcggppp", get_pos_cat(lw.pos_in_utt(), len(utt.words), with_sil=True))

def add_absolute_stanford_pcfg(context_skeleton, phoneme):
  """Adds the absolute elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  #Add basic info
  add_basic_stanford_pcfg(c, phoneme)
  #Word
  w = phoneme.parent_word
  #Word absolute position in parent phrase
  #We may have xx
  c.add("wfwrppp", str(w.parent_phrase.pos_in_parent))
  if w.parent_phrase.pos_in_parent == "xx":
    c.add("wbwrppp", str(w.parent_phrase.pos_in_parent))
  else:
    c.add("wbwrppp", str(w.parent_phrase.num_siblings - 1 - w.parent_phrase.pos_in_parent))
  #Word absolute position in grandparent phrase
  c.add("wfwrgppp", str(w.grandparent_phrase.pos_in_parent))
  if w.grandparent_phrase.pos_in_parent == "xx":
    c.add("wbwrgppp", str(w.grandparent_phrase.pos_in_parent))
  else:
    c.add("wbwrgppp", str(w.grandparent_phrase.num_siblings - 1 - w.grandparent_phrase.pos_in_parent))
  #Word absolute position in greatgrandparent phrase
  c.add("wfwrggppp", str(w.greatgrandparent_phrase.pos_in_parent))
  if w.greatgrandparent_phrase.pos_in_parent == "xx":
    c.add("wbwrggppp", str(w.greatgrandparent_phrase.num_siblings))
  else:
    c.add("wbwrggppp", str(w.greatgrandparent_phrase.num_siblings - 1 - w.greatgrandparent_phrase.pos_in_parent))

def add_basic_stanford_dependency(context_skeleton, phoneme):
  """Adds the basic elements of stanford dependency parse information to a phoneme context."""
  c = context_skeleton
  #Word
  w = phoneme.parent_word
  ###### Stanford Dependency Parse Information ######
  #Word parent dependency relation
  if w.parent_dependency.parent_relation != None:
    c.add("wpdr", w.parent_dependency.parent_relation)
  else:
    c.add("wpdr", "xx")
  #Word parent to grandparent relation
  if w.grandparent_dependency.parent_relation != None:
    c.add("wgpdr", w.grandparent_dependency.parent_relation)
  else:
    c.add("wgpdr", "xx")
  #Word grandparent to greatgrandparent relation
  if w.greatgrandparent_dependency.parent_relation != None:
    c.add("wggpdr", w.greatgrandparent_dependency.parent_relation)
  else:
    c.add("wggpdr", "xx")
  #Word parent general dependency relation
  if w.parent_dependency.parent_relation != None:
    c.add("wpgdr", w.parent_dependency.get_parent_general_relation())
  else:
    c.add("wpgdr", "xx")
  #Number of children
  if w.parent_dependency.children == None:
    if phoneme.id in phoneme.parent_utt.phoneme_features.get_sil_phonemes(): #this is a pause
      c.add("dnc", "xx")
    else: #This is a leaf
      c.add("dnc", "0")
  else:
    c.add("dnc", str(len(w.parent_dependency.children)))
  #Tree distance to left word in num arcs
  #If the current is a pau
  if w.phonemes[0].id in phoneme.parent_utt.phoneme_features.get_sil_phonemes():
    c.add("dtdrw", "xx")
    c.add("dtdlw", "xx")
  else:
    if w.pos_in_utt() > 0:
      wl = w.parent_utt.words[w.pos_in_utt()-1]
      #If prev word is sil
      if wl.phonemes[0].id in phoneme.parent_utt.phoneme_features.get_sil_phonemes():
        c.add("dtdlw", "xx")
      else:
        c.add("dtdlw", str(dep_distance_in_arcs(w.parent_dependency, wl.parent_dependency)))
    else:
        c.add("dtdlw", "xx")
    #Tree distance to right word in num arcs
    try:
      wr = w.parent_utt.words[w.pos_in_utt()+1]
      #If next word is sil
      if wr.phonemes[0].id in phoneme.parent_utt.phoneme_features.get_sil_phonemes():
        c.add("dtdrw", "xx")
      else:
        c.add("dtdrw", str(dep_distance_in_arcs(w.parent_dependency, wr.parent_dependency)))
    except IndexError:
        c.add("dtdrw", "xx")

def add_absolute_stanford_dependency(context_skeleton, phoneme):
  """Adds the absolute elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  #Word
  w = phoneme.parent_word
  ###### Stanford Dependency Parse Information ######
  add_basic_stanford_dependency(c, phoneme)
  #If the current phoneme is sil/pau etc. the label is None and we can just add "xx" all through
  if w.parent_dependency.label == None and phoneme.id in phoneme.parent_utt.phoneme_features.get_sil_phonemes():
    c.add("wdpr", "xx")
    c.add("wdgpr", "xx")
    c.add("wdggpr", "xx")
    return
  #Word absolute distance to parent relation
  dep_pos = w.parent_dependency.utt_pos
  if w.parent_dependency.parent != None and w.parent_dependency.parent.label != "ROOT":
    p_dep_pos = w.parent_dependency.parent.utt_pos
    c.add("wdpr", str(abs(dep_pos-p_dep_pos)))
  else:
    c.add("wdpr", "xx")
  #Word absolute distance to grandparent relation
  if w.grandparent_dependency.parent != None and w.grandparent_dependency.parent.label != "ROOT":
    p_dep_pos = w.grandparent_dependency.parent.utt_pos
    c.add("wdgpr", str(abs(dep_pos-p_dep_pos)))
  else:
    c.add("wdgpr", "xx")
  #Word absolute position to greatgrandparent relation
  if w.greatgrandparent_dependency.parent != None and w.greatgrandparent_dependency.parent.label != "ROOT":
    p_dep_pos = w.greatgrandparent_dependency.parent.utt_pos
    c.add("wdggpr", str(abs(dep_pos-p_dep_pos)))
  else:
    c.add("wdggpr", "xx")

def add_relational_stanford_dependency(context_skeleton, phoneme):
  """Adds the relational elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  #Word
  w = phoneme.parent_word
  ###### Stanford Dependency Parse Information ######
  add_basic_stanford_dependency(c, phoneme)
  #Word relational distance to parent relation
  #We subtract 1 because label pos and num phonemes start from 1 but to_relational starts from 0
  #If the current phoneme is sil/pau etc. the label is None and we can just add "xx" all through
  if w.parent_dependency.label == None and phoneme.id in phoneme.parent_utt.phoneme_features.get_sil_phonemes():
    c.add("wdpr", "xx")
    c.add("wdgpr", "xx")
    c.add("wdggpr", "xx")
    return
  dep_pos = to_relational(w.parent_dependency.utt_pos-1, w.parent_utt.num_words()-1, True)
  if w.parent_dependency.parent != None and w.parent_dependency.parent.label != "ROOT":
    p_dep_pos = to_relational(w.parent_dependency.parent.utt_pos-1, w.parent_utt.num_words()-1, True)
    c.add("wdpr", str(abs(dep_pos-p_dep_pos)))
  else:
    c.add("wdpr", "xx")
  #Word relational distance to grandparent relation
  if w.grandparent_dependency.parent != None and w.grandparent_dependency.parent.label != "ROOT":
    p_dep_pos = to_relational(w.grandparent_dependency.parent.utt_pos-1, w.parent_utt.num_words()-1, True)
    c.add("wdgpr", str(abs(dep_pos-p_dep_pos)))
  else:
    c.add("wdgpr", "xx")
  #Word relational position in greatgrandparent phrase
  if w.greatgrandparent_dependency.parent != None and w.greatgrandparent_dependency.parent.label != "ROOT":
    p_dep_pos = to_relational(w.greatgrandparent_dependency.parent.utt_pos-1, w.parent_utt.num_words()-1, True)
    c.add("wdggpr", str(abs(dep_pos-p_dep_pos)))
  else:
    c.add("wdggpr", "xx")

def add_categorical_stanford_dependency(context_skeleton, phoneme):
  """Adds the categorical elements of stanford parse information to a phoneme context."""
  c = context_skeleton
  #Word
  w = phoneme.parent_word
  utt = phoneme.parent_utt
  ###### Stanford Dependency Parse Information ######
  add_basic_stanford_dependency(c, phoneme)
  #If the current phoneme is sil/pau etc. the label is None and we can just add "xx" all through
  if w.parent_dependency.label == None and phoneme.id in phoneme.parent_utt.phoneme_features.get_sil_phonemes():
    c.add("wdpr", "xx")
    c.add("wdgpr", "xx")
    c.add("wdggpr", "xx")
    return
  #Word categorical distance to parent relation
  dep_pos = w.parent_dependency.utt_pos
  if w.parent_dependency.parent != None and w.parent_dependency.parent.label != "ROOT":
    p_dep_pos = w.parent_dependency.parent.utt_pos
    c.add("wdpr", get_dep_pos_cat(dep_pos, p_dep_pos, len(utt.words), with_sil=True))
  else:
    c.add("wdpr", "xx")
  #Word categorical distance to grandparent relation
  if w.grandparent_dependency.parent != None and w.grandparent_dependency.parent.label != "ROOT":
    p_dep_pos = w.grandparent_dependency.parent.utt_pos
    c.add("wdgpr", get_dep_pos_cat(dep_pos, p_dep_pos, len(utt.words), with_sil=True))
  else:
    c.add("wdgpr", "xx")
  #Word categorical distance to greatgrandparent relation
  if w.greatgrandparent_dependency.parent != None and w.greatgrandparent_dependency.parent.label != "ROOT":
    p_dep_pos = w.greatgrandparent_dependency.parent.utt_pos
    c.add("wdggpr", get_dep_pos_cat(dep_pos, p_dep_pos, len(utt.words), with_sil=True))
  else:
    c.add("wdggpr", "xx")

#These are features necessary for festival equivalence, but generally doubtful how much they add.
#Festival_gpos - use the festival pos generalisation or the sire_generalisation. Sire_generalisation requires a propor pos tagger (e.g. through parsing)
def add_festival(context_skeleton, phoneme, festival_gpos=True):
  c = context_skeleton
  #General pos
  w = phoneme.parent_word
  #If we are not the first word.
  #Note this starts from 1 as pos_in_utt returns output of len()
  w_pos = w.pos_in_utt() - 1
  if festival_gpos == True:
    gpos_method = pos.get_festival_general_pos
  else:
    gpos_method = pos.get_sire_general_pos
  if w_pos > 0:
    c.add("rgpos", gpos_method(phoneme.parent_utt.words[w_pos-1]))
  else:
    c.add("rgpos", "xx")
  c.add("cgpos", gpos_method(w))
  if w_pos < phoneme.parent_utt.num_words() - 1:
    c.add("lgpos", gpos_method(phoneme.parent_utt.words[w_pos+1]))
  else:
    c.add("lgpos", "xx")
  #Cur Syll Accent
  c.add("csacc", phoneme.parent_syllable.accent)
  #Number of accented syllables before current syll
  n = 0
  last_accent_dist = "xx"
  utt_pos = phoneme.parent_syllable.pos_in_utt()
  for i, cs in enumerate(phoneme.parent_utt.syllables[:utt_pos]):
    if cs.accent == 1:
      n += 1
      last_accent_dist = utt_pos-i
  c.add("nasbcs", n)
  #Number of accented syllables after current syll
  n = 0
  next_accent_dist = "xx"
  if phoneme.parent_utt.num_syllables() != utt_pos+1:
    for i, cs in enumerate(phoneme.parent_utt.syllables[utt_pos+1:]):
      if cs.accent == 1:
        n += 1
        if next_accent_dist == "xx":
          next_accent_dist = i+1
  c.add("nasacs", n)
  #Distance to previous accented syllable
  c.add("pasd", last_accent_dist)
  #Distance to next accented syllable
  c.add("nasd", next_accent_dist)

#Returns a question set and a GV/utt question set.
#context_skeleton = The type of question set to output.
#qformat = Return the set in HMM format ("HMM") or Neural Network format ("NN").
#fit_contexts = If False creates generic question set, if True creates
#               question set adapted to contexts passed to contexts_to_fit.
#contexts_to_fit = The set of contexts to produce a fitted question set to.
def get_question_sets(context_skeleton, qformat, fit_contexts=False, contexts_to_fit=None, HHEd_fix=False):
  #Should be unnecessary due to argparse, but just to be sure.
  if qformat not in ["Nitech_NN", "HMM", "CSTR_NN"]:
    raise SiReError("Invalid question format ({0})! Must be either HMM, Nitech_NN or CSTR_NN!".format(qformat))
  c = context_skeleton
  c_utt = copy.deepcopy(context_skeleton)
  questions = []
  if fit_contexts == True:
    #First we obtain a dict containing a list of all used values for each context feature.
    for context in contexts_to_fit:
      for key in context.added_contexts:
        c.add_multiple(key, context.added_contexts[key])
        #Check if this should be in the GV context set
        if getattr(c, key) and "utt" in getattr(c, key):
          c_utt.add_multiple(key, context.added_contexts[key])
    #Then we create questions based on these
    qs = make_questions(c, qformat, False, HHEd_fix)
    q_utt = make_questions(c_utt, qformat, False, HHEd_fix, True)
    return (qs, q_utt)
  else:
    raise SiReError("Not Implemented yet! (Not fitting contexts for question set.)")

#Returns a list of questions for the appropriate feature.
#If generic is True outputs a generic set which may or may not cover your dataset.
#If generic is False it only output questions fitting the values in the
#added_contexts dict (do remember to add_multiple these from your dataset first).
#qformat = Return the questions in HMM format ("HMM") or Neural Network format ("NN").
#generic = Return a generic question set not fitted to the data.
#HHEd_fix = Make current phoneme context -phoneme+ as this is hardcoded in HHEd.
def make_questions(context_skeleton, qformat, generic=True, HHEd_fix=False, utt=False):
  context_dict = context_skeleton.added_contexts
  #We write out each context not used just for checks.
  #TODO: Make it possible to throw an exception if context not used.
  #TODO: Currently we ignore this when making GV contexts.
  if utt == False:
    for context in vars(context_skeleton).keys():
      if context not in context_dict and context != "added_contexts":
        print context_dict.keys()
        print "Warning! Context ({0}) not used!".format(context)
  if qformat not in ["Nitech_NN", "HMM", "CSTR_NN"]:
    raise SiReError("Invalid question format ({0})! Must be either HMM, Nitech_NN or CSTR_NN!".format(qformat))
  questions = []
  if generic == False:
    for key in context_dict:
      qtype = getattr(context_skeleton, key)
      #Setting it removes duplicates and sorting them is important for HMM question creation
      #(sorting them is also prettier for the NN)
      vals = list(set(context_dict[key]))
      vals.sort()
      if qtype == None:
        pass
      elif qtype == "bool":
        for val in vals:
          #If this is current phoneme id we apply the HHEd_fix
          if HHEd_fix == True and key == "cp":
            val = "-"+str(val)+"+"
          if qformat == "HMM" or qformat == "CSTR_NN":
            questions.append("QS \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
          elif qformat == "Nitech_NN":
            questions.append("LQ 0 \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
      elif "float" in qtype:
        if qformat == "HMM":
          questions += make_hmm_relational_qs(vals, key, qtype)
        elif qformat == "Nitech_NN":
          for val in vals:
            #HHEd's pattern matching for both NN and HMM's uses '.' as a special
            #character. We therefore use the int version of the float value in the
            #search pattern. But we have to check for xx first.
            if val == "xx":
              questions.append("LQ 1 0.0 \""+key+"-xx\" {*|"+key+":xx|*}")
            else:
              questions.append("LQ 1 "+str(val)+" \""+key+"-"+strintify(float(val))+"\" {*|"+key+":"+strintify(float(val))+"|*}")
        elif qformat == "CSTR_NN":
          #For CSTR's DNN system we just need to specify the question and not one for each value of the question if float or int.
          #Note that floats needs to be strintified in the actual question.
          questions.append("CQS \""+key+"\" {*|"+key+":(\d+)|*}")
      elif "int" in qtype:
        if qformat == "HMM":
          questions += make_hmm_relational_qs(vals, key, qtype)
        elif qformat == "Nitech_NN":
          for val in vals:
            #The NN relies on floats for the actual value so we use that there
            #and the int in the naming. But we have to check for xx first.
            if val == "xx":
              questions.append("LQ 1 0.0 \""+key+"-xx\" {*|"+key+":xx|*}")
            else:
              questions.append("LQ 1 "+strfloatify(int(val))+" \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
        elif qformat == "CSTR_NN":
          #For CSTR's DNN system we just need to specify the question and not one for each value of the question if float or int.
          #Note that floats needs to be strintified in the actual question.
          questions.append("CQS \""+key+"\" {*|"+key+":(\d+)|*}")
      else:
        raise SiReError("Odd question type, should not exist - {0}".format(qtype))
  else:
    raise SiReError("Not implemented yet! (Outputting generic question set)")
  return questions

#This assumes that values are already sorted in ascending order!
def make_hmm_relational_qs(values, key, qtype):
  questions = []
  #Add xx question if appropriate else ignore
  if "xx" in values:
    if "xx" in qtype:
      questions.append("QS \""+key+"-xx\" {*|"+key+":xx|*}")
    else:
      raise SiReError("xx in values but not in qtype {0} for key {1} - why?".format(qtype,key))
    values.remove("xx")
  for i, val in enumerate(values):
    if "float" in qtype:
      val = strintify(float(val))
    questions.append("QS \""+key+"-"+str(val)+"\" {*|"+key+":"+str(val)+"|*}")
    #If val is more than one we make a less than question
    #If we count 0 then we start at 0
    if "0" in qtype:
      start = 0
    else:
      start = 1
    if int(val) > start:
      #Prep the less than string
      s = "QS \""+key+"<="+str(val)+"\" {"
      #Make the less than string
      #Get tens and remainder
      tens = int(val)/10
      remainder = int(val)%10
      if tens > 0:
        #Make singles
        for n in range(start, 10):
          s += "*|"+key+":"+str(n)+"|*,"
        #Make tens
        for n in range(1, tens):
          s += "*|"+key+":"+str(n)+"?|*,"
        for n in range(remainder+1):
          if n != remainder:
            s += "*|"+key+":"+str(tens)+str(n)+"|*,"
          else:
            s += "*|"+key+":"+str(tens)+str(n)+"|*}"
            questions.append(s)
      else:
        #Just make singles
        for n in range(start, int(val)+1):
          s += "*|"+key+":"+str(n)+"|*"
          if n != int(val):
            s += ","
          else:
            s += "}"
            questions.append(s)
  return questions
