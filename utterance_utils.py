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

import utterance
from error_messages import SiReError

#Methods for manipulating utterances in non-standard ways. Most of these are considered dangerous and unsafe.

#Try to split words in the utterance which may be contraction which parsing expands.
#This is potentially unsafe so outputs warnings when doing it.
#This list is likely incomplete, but it is also likely not all issues can be resolved.
def try_split_words(utt):
  l = len(utt.words)
  #We should not try this if we have not gotten the word.id from txt.
  if utt.txtloaded != True:
    raise SiReError("Cannot split words if word ids not loaded from txt.")
  for word in utt.words:
    #End of word 's
    if word.id[-2:] == "'s":
      split_word(word, -2)
    #Contracted are's (e.g. we're)
    elif word.id[-3:] == "'re":
      split_word(word, -3)
    #Contracted not's (e.g. don't)
    elif word.id[-3:] == "n't":
      split_word(word, -2)
    #Contracted will's (e.g. it'll)
    elif word.id[-3:] == "'ll":
      split_word(word, -3)
    #Contracted have's (e.g. I've)
    elif word.id[-3:] == "'ve":
      split_word(word, -3)
    #Contracted I am
    elif word.id == "i'm":
      split_word(word, -2)
    #Contracted would or had (e.g. she'd)
    elif word.id[-2:] == "'d":
      split_word(word, -2)
    #Contracted going to
    elif word.id == "gonna":
      split_word(word, -2)
    #Contracted can not
    elif word.id == "cannot":
      split_word(word, -3)
    #Contracted want to
    elif word.id == "wanna":
      split_word(word, -2)
  if l == len(utt.words):
    print "Warning: Nothing to split in word."

#Splits a word into two, the new being its last syllable.
#Split_pos is the character pos in the word from which to split.
def split_word(word, split_pos):
  utt = word.parent_utt
  split_more_than_one_phoneme = False
  #We usually only want to change one phoneme and this list checks for those.
  if word.syllables[-1].num_phonemes() != 1:
    s = word.syllables[-1]
    #This should also update the word itself with the new syll info.
    #End of word 's
    if word.id[-2:] == "'s":
      split_syll(s, ["s", "z"])
    #Contracted are's (e.g. we're)
    elif word.id[-3:] == "'re":
      #'r' is a bit... meh. In e.g. "you're" pronounced "jU@r" we kinda want to add a phony
      #before "r".
      #But this is not supported atm.
      split_syll(s, ["I@", "U@", "E@", "@", "r"], ["I@", "U@", "E@", "O"])
    #Contracted not's (e.g. don't)
    elif word.id[-3:] == "n't":
      split_syll(s, ["n", "G", "t"])
    #Contracted will's (e.g. it'll)
    elif word.id[-3:] == "'ll":
      split_syll(s, ["lw", "l"])
    #Contracted have's (e.g. I've)
    elif word.id[-3:] == "'ve":
      split_syll(s, ["f", "v"])
    #Contracted I am
    elif word.id[-3:] == "i'm":
      split_syll(s, ["m"])
    #Contracted would or had (e.g. she'd)
    elif word.id[-2:] == "'d":
      split_syll(s, ["d", "G"], ["u"])
    #Contracted going to
    elif word.id == "gonna":
      if s.id in ["nu", "n@"]:
        split_more_than_one_phoneme = True
    #Contracted can not
    elif word.id == "cannot":
      #If the syll is "nQG" or "nQt" we're good and can split
      if s.id in ["nQG", "nQt"]:
        split_more_than_one_phoneme = True
    elif word.id == "wanna":
      #If the syll is "n@" we're good and can split
      if s.id == "n@":
        split_more_than_one_phoneme = True
  #If there is only one syllable with one word we have to add a phony syll.
  elif len(word.syllables) < 2:
    s = word.syllables[-1]
    #Contracted would or had (e.g. I'd)
    if word.id[-2:] == "'d":
      split_syll(s, ["aI"], ["aI"])
  
  if word.syllables[-1].num_phonemes() > 1 and split_more_than_one_phoneme != True:
    raise SiReError("Cannot split a word {0} with final syllable {1} with more than one phoneme ({2}) as this has not been explicitly allowed!".format(word.id, word.syllables[-1].id, word.syllables[-1].num_phonemes()))
  w1 = utterance.Word()
  w1.id = word.id[:split_pos]
  w2 = utterance.Word()
  w2.id = word.id[split_pos:]
  print "Warning: Splitting word ({0}) into two ({1} and {2}). Is this correct?".format(word.id, w1.id, w2.id)
  #Start time
  w1.start = word.start_time()
  w2.start = word.syllables[-1].start_time()
  #End time
  w1.end = word.syllables[-2].end_time()
  w2.end = word.end_time()
  #Parent utt
  w1.parent_utt = utt
  w2.parent_utt = utt
  #Pos in utt
  #Slice out the original word
  w_p_u = word.pos_in_utt()
  utt.words = utt.words[:w_p_u] + [w1, w2] + utt.words[w_p_u + 1:]
  #Fix syllables
  w1.syllables = word.syllables[:-1]
  w2.syllables = [word.syllables[-1]]
  for s in w1.syllables:
    s.parent_word = w1
  w2.syllables[0].parent_word = w2
  #Fix phonemes
  w1.phonemes = word.phonemes[:-len(word.syllables[-1].phonemes)]
  w2.phonemes = word.phonemes[-len(word.syllables[-1].phonemes):]
  for p in w1.phonemes:
    p.parent_word = w1
  for p in w2.phonemes:
    p.parent_word = w2
  
  #Delete the original word. If all has gone well this should be fine.
  del word

#Splits a syllable on its last phoneme.
def split_syll(syll, acceptable_phoneme_set, word_spanning_phonemes=[]):
  #Makes life a bit easier
  utt = syll.parent_utt
  phoneme_features = utt.phoneme_features
  
  #A special case for phonemes which may have ended up spanning across what would normally
  #be two words or if all phonemes related to the "2nd" word has been deleted.
  #E.g. I@ in we're (w I@) or u in who'd (h u).
  #In this case we add a new "phony" syllable with no duration. So it affects contexts
  #but does not take any frames.
  if syll.phonemes[-1].id in word_spanning_phonemes:
    phony = utterance.Syllable()
    phony.id = syll.phonemes[-1].id
    phony.stress = syll.stress
    phony.parent_utt = syll.parent_utt
    phony.parent_word = syll.parent_word
    #Slice in phony
    phony.parent_utt.syllables.insert(syll.pos_in_utt()+1, phony)
    phony.parent_word.syllables.insert(syll.pos_in_word()+1, phony)
    #We need to add a phony phoneme for e.g. start end time information
    phony_phone = utterance.Phoneme()
    phony_phone.start = syll.end_time()
    phony_phone.end = syll.end_time()
    phony.phonemes = [phony_phone]
    phony.vowel_id = syll.vowel_id
    return
  
  #You must know which phonemes are acceptable to replace.
  #Just a safety that things don't go horribly wrong. Disable this if you feel lucky.
  if syll.phonemes[-1].id not in acceptable_phoneme_set:
    raise SiReError("Cannot split syllable {0} unless its last phoneme {1} exists in the acceptable set ({2})".format(syll.id, syll.phonemes[-1].id, acceptable_phoneme_set))
  
  #ID
  s1 = utterance.Syllable()
  s1.id = syll.id[:-1]
  s2 = utterance.Syllable()
  s2.id = syll.id[-1]
  print "Warning: Splitting syll ({0}) into two {1} and {2}".format(syll.id, s1.id, s2.id)
  #Start pos
  s1.start = syll.start_time()
  s2.start = syll.phonemes[-1].start
  #End pos
  s1.end = syll.phonemes[-2].end
  s2.end = syll.end_time()
  #Stress
  #If we have stress on phonemes we use that, else we use the syll stress
  if syll.phonemes[0].stress == None:
    s1.stress = syll.stress
    s2.stress = syll.stress
  else:
    s = 0
    for p in syll.phonemes[:-1]:
      if int(p.stress) > 0:
        s = 1
    s1.stress = str(s)
    if int(syll.phonemes[-1].stress) > 0:
      s2.stress = str(1)
    else:
      s2.stress = str(0)
  #Pos in utt
  #Slice in syll
  s_p_u = syll.pos_in_utt()
  utt.syllables = utt.syllables[:s_p_u] + [s1, s2] + utt.syllables[s_p_u + 1:]
  #Pos in word
  word = syll.parent_word
  s_p_w = syll.pos_in_word()
  #Slice in the new sylls
  word.syllables = word.syllables[:s_p_w] + [s1, s2]
  #Parents
  s1.parent_utt = utt
  s2.parent_utt = utt
  s1.parent_word = word
  s2.parent_word = word
  #Update child phonemes
  s1.phonemes = syll.phonemes[:-1]
  s2.phonemes = [syll.phonemes[-1]]
  for p in s1.phonemes:
    p.parent_syllable = s1
  s2.phonemes[0].parent_syllable = s2
  #Update vowel id
  if phoneme_features.is_vowel(s2.phonemes[0].id):
    s2.vowel_id = s2.phonemes[0].id
  else:
    s2.vowel_id = "novowel"
  v = "novowel"
  for p in s1.phonemes:
    if phoneme_features.is_vowel(p.id):
      v = p.id
      break
  s1.vowel_id = v
  
  #Delete the original syll.
  del syll

