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

import phoneme_features, utterance_load, os, prosody, pos
from error_messages import SiReError

class Utterance(object):
  """An object representing an utterance."""
  
  #Create an empty utt.
  #The proto utterance follows the following conventions:
  #It is a dictionary with two keys, id giving the name of the utt,
  #and utt containing the actual utt.
  #Utt is itself a list of proto_words.
  #A proto_word is a dict containing two keys, id giving the name of the word,
  #and syllables.
  #Syllables is itself a list of proto_syllables.
  #A proto_syllable is a dict containing three keys, id giving the name of the syllable,
  #stress giving its stress value and phonemes.
  #The id of a syllable is expected to be the id of all its contained
  #phonemes in order as a string. 
  #Phonemes is itself a list of proto_phonemes.
  #A proto_phoneme is a dict containing 4 keys.
  #Id being the type of phoneme, must be a valid phoneme in phoneme set used.
  #Start - the start time in HTK style values where 10000 is 1ms.
  #End - the end time in HTK style values where 10000 is 1 ms.
  #Stress - the stress value of the phoneme - this may be None in case we do not have the information.
  def __init__(self, lab, args):
    #Make a proto utt from the input
    if args.intype == "align_mlf":
      proto = utterance_load.proto_from_align_lab(lab)
    elif args.intype == "state_align_mlf":
      proto = utterance_load.proto_from_state_align_lab(lab)
      self.txtloaded = False
    elif args.intype == "hts_mlf":
      proto = utterance_load.proto_from_hts_lab(lab)
      self.txtloaded = False
    elif args.intype == "sire_lab":
      #As we need additional information here we check if args contains it
      if not hasattr(args, "context_type"):
        raise SiReError("You're trying to create an utterance from a SiRe label but have not told what kind of positional context_type was used!")
      if not hasattr(args, "HHEd_fix"):
        raise SiReError("You're trying to create an utterance from a SiRe label but have not told if HHEd_fix was used to create the labels!")
      proto = utterance_load.proto_from_sire_lab(lab, args.context_type, args.HHEd_fix)
      self.txtloaded = False
    elif args.intype == "txt":
      #Check if args has all the necessary elements and insert defaults if not.
      if not hasattr(args, 'pron_reduced') or args.pron_reduced == False:
        args.pron_reduced = False
        args.lm_score_dir = None
        args.reduction_level = 1.0
      else:
        #If we are we need to check if we know enough to do it and fail if we don't.
        if not hasattr(args, 'lm_score_dir'):
          raise SiReError("You have asked to produce a reduced phonemisation but no path to a directory containing LM word probabilities to base the reduction on.")
        if not hasattr(args, 'reduction_level'):
          raise SiReError("You have asked to produce a reduced phonemisation but not specified to which degree the sentence should be reduced.")
      if not hasattr(args, 'general_sil_phoneme'):
        print "Warning! args does not tell if there is a standard silence phoneme! Using default... (\"sil\")"
        args.general_sil_phoneme = "sil"
      if not hasattr(args, 'comma_is_pause'):
        print "Warning! args does not tell if commas should be used as pauses! Using default... (no)"
        args.comma_is_pause = False
      if not hasattr(args, 'stanford_pcfg_parse'):
        print "Warning! args does not tell if we are using stanford parsing! Using default... (no)"
        args.stanford_pcfg_parse = False
      if args.stanford_pcfg_parse == False:
        args.pcfgdict = False
      proto = utterance_load.proto_from_txt(lab, args.dictionary, args.general_sil_phoneme, args.comma_is_pause, args.stanford_pcfg_parse, args.pcfgdict, args.pron_reduced, args.lm_score_dir, args.reduction_level)
      self.txtloaded = True
    else:
      raise SiReError("Don't know what to do with intype - {0}".format(args.intype))
    
    #Construct the utt from the proto utt
    self.id = proto["id"]
    self.phonemes = []
    self.syllables = []
    self.words = []
    #We need to know which phoneme features this utterance is created with.
    if hasattr(args, 'dictionary'):
      self.phoneme_features = args.dictionary.phoneme_feats
    elif hasattr(args, 'phoneme_features'):
      self.phoneme_features = args.phoneme_features
    else:
      raise SiReError("args does not contain either a dictionary or a phoneme featureset!")
    s_utt_pos = 0
    p_utt_pos = 0
    
    for wi, proto_word in enumerate(proto["utt"]):
      p_word_pos = 0
      word = Word()
      word.load_from_proto(proto_word, wi, p_utt_pos, s_utt_pos, len(proto["utt"]), self)
      self.words.append(word)
      for si, proto_syll in enumerate(proto_word["syllables"]):
        syll = Syllable()
        syll.load_from_proto(proto_syll, p_utt_pos, si, s_utt_pos, word, self)
        self.syllables.append(syll)
        for pi, proto_phone in enumerate(proto_syll["phonemes"]):
          phoneme = Phoneme()
          phoneme.load_from_proto(proto_phone, pi, p_utt_pos, p_word_pos, syll, word, self)
          self.phonemes.append(phoneme)
          p_word_pos += 1
          p_utt_pos += 1
        s_utt_pos += 1
        syll.add_phonemes()
      word.add_phonemes()
      word.add_syllables()
    
    #If we should use the stanford pcfg parse info
    if hasattr(args, 'stanford_pcfg_parse') and args.stanford_pcfg_parse:
      print "Loading stanford pcfg parse info to utt..."
      if args.intype != "txt":
        utterance_load.load_txt(self, os.path.join(args.txtdir, self.id+".txt"))
      utterance_load.load_stanford_pcfg_parse(self, args.pcfgdict[self.id], args.comma_is_pause)
    
    #If we should use the stanford dependency parse info
    if hasattr(args, 'stanford_dependency_parse') and args.stanford_dependency_parse:
      print "Loading stanford dependency parse info to utt..."
      if args.intype != "txt" and self.txtloaded == False:
        utterance_load.load_txt(self, os.path.join(args.txtdir, self.id+".txt"))
      utterance_load.load_stanford_dependency_parse(self, args.dependencydict[self.id])
    
    #If we output a Festival context set we should modify the UTT a bit further.
    #Right now we use the full festival features as standard, but some operations, like corpus analysis, does not rely on this and it is a nuisance to have the text a requirement so this is still just an option.
    if args.festival_features == True:
      #We need to know the words
      if args.intype != "txt" and self.txtloaded == False:
        utterance_load.load_txt(self, os.path.join(args.txtdir, self.id+".txt"))
      #If we have a pcfg parse we have a proper POS tag mechanism and they have already been added
      if not args.stanford_pcfg_parse:
        pos.simple_festival_pos_predict(self)
      prosody.simple_festival_accent_predict(self)
    
#    #Replacing UH - test!
#    if not self.txtloaded:
#      utterance_load.load_txt(self, os.path.join(args.txtdir, self.id+".txt"))
#    for w in self.words:
#      if w.id.lower() in ["uh", "uhu", "um", "uhum"]:
#        for p in w.phonemes:
#          if p.id in ["@", "V"]:
#            p.id = "V"
  
  def num_phonemes(self):
    return len(self.phonemes)
  
  def num_syllables(self):
    return len(self.syllables)
  
  def num_words(self):
    return len(self.words)
  
  def num_words_no_pau(self, keep_comma=False):
    return len(self.get_words_no_pau(keep_comma))
  
  def num_phonemes_no_pau(self):
    return len(self.get_phonemes_no_pau())
  
  #Gets the words without pausing
  #Used when comparing to stanford parse etc.
  def get_words_no_pau(self, keep_comma=False):
    tmp = []
    ignore = self.phoneme_features.get_sil_phonemes()
    for word in self.words:
      if keep_comma == False:
        ignore += [","]
      if word.id not in ignore:
        tmp.append(word)
    return tmp
  
  def get_phonemes_no_pau(self):
    tmp = []
    ignore = self.phoneme_features.get_sil_phonemes()
    for p in self.phonemes:
      if p.id not in ignore:
        tmp.append(p)
    return tmp

class Phoneme:
  """A class representing a phoneme."""
  def __init__(self, p_id=None):
    self.id = p_id
  
  def load_from_proto(self, proto_phone, p_syll_pos, p_utt_pos, p_word_pos, syll, word, utt):
    self.id = proto_phone["id"]
    self.start = proto_phone["start"]
    self.end = proto_phone["end"]
    self.stress = proto_phone["stress"]
    #These work because they are objects and are so passed by reference value.
    #I.e. a copy of the reference to the object is what is stored not the full object.
    self.parent_syllable = syll
    self.parent_word = word
    self.parent_utt = utt
    if proto_phone["states"]:
      self.states = proto_phone["states"]
  
  #These are expensive operations I think.
  #But necessary to keep things properly dynamic and has lots of benefits further on
  #when merging parses into utterances.
  def pos_in_syllable(self):
    for i, p in enumerate(self.parent_syllable.phonemes):
      if p == self:
        return i
    raise SiReError("Cannot find self {0} in syll {1}!".format(self.id, self.parent_syllable.id))
  
  def pos_in_word(self):
    for i, p in enumerate(self.parent_word.phonemes):
      if p == self:
        return i
    raise SiReError("Cannot find phoneme {0} in word {1}!".format(self.id, self.parent_word.id))
  
  def pos_in_utt(self):
    for i, p in enumerate(self.parent_utt.phonemes):
      if p == self:
        return i
    raise SiReError("Cannot find phoneme {0} in utt {1}!".format(self.id, self.parent_utt.id))

  def get_feats(self):
    return self.parent_utt.phoneme_features.get_phoneme_feats(self.id)
  
  def get_feats_dict(self):
    return self.parent_utt.phoneme_features.get_phoneme_feats_dict(self.id)
  
  def get_left_phoneme(self):
    pos = self.pos_in_utt()
    if pos == 0:
      return Phoneme("xx")
    else:
      return self.parent_utt.phonemes[pos-1]
  
  def get_left_left_phoneme(self):
    pos = self.pos_in_utt()
    if pos <= 1:
      return Phoneme("xx")
    else:
      return self.parent_utt.phonemes[pos-2]
  
  def get_right_phoneme(self):
    pos = self.pos_in_utt()
    u_len = self.parent_utt.num_phonemes() - 1
    if pos == u_len:
      return Phoneme("xx")
    else:
      return self.parent_utt.phonemes[pos+1]
  
  def get_righ_right_phoneme(self):
    pos = self.pos_in_utt()
    u_len = self.parent_utt.num_phonemes() - 2
    if pos >= u_len:
      return Phoneme("xx")
    else:
      return self.parent_utt.phonemes[pos+2]
  
  #Returns the duration of the phone
  #Note that if the utterance was created from text
  #then this duration is phony and not valid.
  def get_duration(self):
    return int(self.end)-int(self.start)

class Syllable:
  """A class representing a syllable."""
  
  #An empty syll.
  #Using this can be dangerous if you don't add everything necesary later.
  def __init__(self, s_id=None):
    self.id = None
  
  def load_from_proto(self, proto_syll, current_phoneme_utt_pos, s_word_pos, s_utt_pos, word, utt):
    self.id = proto_syll["id"]
    self.stress = proto_syll["stress"]
    #These work because they are objects and are so passed by reference value.
    #I.e. a copy of the reference to the object is what is stored not the full object.
    self.parent_word = word
    self.parent_utt = utt
    #We initially save the utt pos of each phoneme in the syll
    #instead of direct references because of the order we create these.
    #These are later added and this list removed.
    self.child_phoneme_utt_positions = []
    for i in range(len(proto_syll["phonemes"])):
      self.child_phoneme_utt_positions.append(i+current_phoneme_utt_pos)
    #This will be filled later
    self.phonemes = None
    self.vowel_id = self.find_vowel(proto_syll, utt.phoneme_features)
  
  #This works because we are passing by reference value.
  def add_phonemes(self):
    self.phonemes = []
    for i in self.child_phoneme_utt_positions:
      self.phonemes.append(self.parent_utt.phonemes[i])
    del self.child_phoneme_utt_positions
  
  #If a syllable contains more than one vowel this return the first one.
  def find_vowel(self, proto_syll, phoneme_features):
    for p in proto_syll["phonemes"]:
      if phoneme_features.is_vowel(p["id"]):
        return p["id"]
    return "novowel"
  
  def pos_in_word(self):
    for i, p in enumerate(self.parent_word.syllables):
      if p == self:
        return i
    raise SiReError("Cannot find syllable {0} in word {1}!".format(self.id, self.parent_word.id))
    
  def pos_in_utt(self):
    for i, p in enumerate(self.parent_utt.syllables):
      if p == self:
        return i
    raise SiReError("Cannot find syllable {0} in utt {1}!".format(self.id, self.parent_utt.id))
  
  def num_phonemes(self):
    return len(self.phonemes)
  
  def start_time(self):
    return self.phonemes[0].start
  
  def end_time(self):
    return self.phonemes[-1].end
  
  def get_vowel_feats(self):  
    return self.parent_utt.phoneme_features.get_phone_feats(self.vowel_id)
  
  def get_vowel_feats_dict(self):  
    return self.parent_utt.phoneme_features.get_phone_feats_dict(self.vowel_id)
  
  def get_left_syllable(self):
    pos = self.pos_in_utt()
    if pos == 0:
      return "xx"
    else:
      return self.parent_utt.syllables[pos-1]
  
  def get_right_syllable(self):
    pos = self.pos_in_utt()
    u_len = self.parent_utt.num_syllables() - 1
    if pos == u_len:
      return "xx"
    else:
      return self.parent_utt.syllables[pos+1]


class Word:
  """A classs representing a word."""
  
  #An empty word with only a name.
  #This can go wrong if you don't add everything needed later.
  def __init__(self):
    self.id = None
  
  def load_from_proto(self, proto_word, word_utt_pos, current_phoneme_utt_pos, current_syll_utt_pos, proto_utt_len, utt):
    self.id = proto_word["id"]
    self.parent_utt = utt
    #We initially save the utt pos of each syllable and phoneme in the word
    #instead of direct references because for the order we create these.
    #These can later be added, but should not be necessary
    #as each phoneme and syll already nows its parent word.
    self.child_syllable_utt_positions = []
    for i in range(len(proto_word["syllables"])):
      self.child_syllable_utt_positions.append(i+current_syll_utt_pos)
    self.phonemes = None
    self.child_phoneme_utt_positions = []
    tmp = 0
    for s in proto_word["syllables"]:
      tmp += len(s["phonemes"])
    for i in range(tmp):
      self.child_phoneme_utt_positions.append(i+current_phoneme_utt_pos)
    self.syllables = None
  
  #This works because we are passing by reference value.
  def add_syllables(self):
    self.syllables = []
    for i in self.child_syllable_utt_positions:
      self.syllables.append(self.parent_utt.syllables[i])
    del self.child_syllable_utt_positions
  
  #This works because we are passing by reference value.
  def add_phonemes(self):
    self.phonemes = []
    for i in self.child_phoneme_utt_positions:
      self.phonemes.append(self.parent_utt.phonemes[i])
    del self.child_phoneme_utt_positions
  
  def pos_in_utt(self):
    for i, p in enumerate(self.parent_utt.words):
      if p == self:
        return i
    raise SiReError("Cannot find word {0} in utt {1}!".format(self.id, self.parent_utt.id))
  
  def num_syllables(self):
    return len(self.syllables)
  
  def num_phonemes(self):
    return len(self.phonemes)
  
  def start_time(self):
    return self.phonemes[0].start
  
  def end_time(self):
    return self.phonemes[-1].end
  
  #Gets the durations of the word.
  #NOTE: This will be a phony if utt created from text.
  def get_duration(self):
    return int(self.phonemes[-1].end) - int(self.phonemes[0].start)
  
  #Returns the previous word in the utterance. Returns "xx" if this is the first word in the utt.
  def get_prev_word(self):
    if self.pos_in_utt() == 0:
      return "xx"
    else:
      return self.parent_utt.words[self.pos_in_utt() - 1]
  
  #Returns the next word in the utterance. Returns "xx" if this is the last word in the utt.
  def get_next_word(self):
    #Pos in utt starts from 0, len starts at 1, so add 1
    pos = self.pos_in_utt() + 1
    if pos == len(self.parent_utt.words):
      return "xx"
    else:
      #We want the next one and have already added one to pos.
      return self.parent_utt.words[pos]
