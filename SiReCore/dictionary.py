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

#Contains all dictionary related operations.
import os, list_utils, phoneme_features
from error_messages import SiReError

#A dictionary class for creating dictionaries.
#Currently only combilex is supported.
#Each should have a variable called:
#self.raw_dictionary_entries = the dictionary with its entries.
#self.phoneme_feats = An instance of the relevant phoneme features for the relevant type of dictionary from phone_features.py
#TODO - Should be flexible which type of dictionary to create - currently only supports combilex.
class Dictionary(object):
  """A dictionary class."""
  
  #Create a combilex dictionary
  def __init__(self, path):
    print "Loading combilex..."
    self.type = "combilex"
    entries = [x for x in open(os.path.join(path, "combilex.dict"), "r").readlines() if x[0] == "("]
    entries += [x for x in open(os.path.join(path, "combilex.add"), "r").readlines() if x[0] == "("]
    #Generally this should not be used directly - rather the get methods below should be used
    #to retrieve the desired type of entry.
    self.raw_dictionary_entries = {}
    #Parse each combilex entry into its name, part of speech tag, reduction level and syllable/phonemes
    for e in entries:
      entry = e.split("\"")
      #find the name
      name = entry[1]
      entry = entry[2].strip()
      #There is an extra () pair if the entry is reduced/has a reduced version
      if entry[0] == "(":
        entry = entry.split(") (")
        #Find pos tag and reduction level
        p_r =  entry[0][1:].split()
        #Combilex entries may have several pos tags. We simply ignore the second which is usually the possesive (See ToDo).
        pos = p_r[0].split("|")[0]
        if p_r[1] == "reduced":
          reduced = True
        elif p_r[1] == "full":
          reduced = False
        else:
          raise SiReError("Cannot parse entry in combilex:\n{0}".format(e))
        #Make entry the syllable structure
        entry = ") (".join(entry[1:])[:-1]
      else: #The entry is definitely not reduced
        entry = entry.split(" (")
        pos = entry[0].split("|")[0]
        reduced = False
        entry = " (".join(entry[1:])[:-1]
      #Make syll structure
      sylls = [x.strip("()") for x in entry.split(") (")]
      word = {"pos":pos, "reduced":reduced, "syllables":[]}
      for syll in sylls:
        c_syll = {"id":"", "phonemes":[], "stress":None}
        syll = syll.split(") ")
        c_syll["stress"] = syll[1]
        #Make the phonemes
        for phon in syll[0].split():
          c_phon = {"id":None, "stress":None, "start":None, "end":None}
          c_phon["id"] = phon
          #Phone stress not encoded directly in combilex surface form dicts.
          c_phon["stress"] = None
          c_syll["phonemes"].append(c_phon)
        c_syll["id"] = syll[0].replace(" ", "")
        word["syllables"].append(c_syll)
      if name in self.raw_dictionary_entries:
        self.raw_dictionary_entries[name] += [word]
      else:
        self.raw_dictionary_entries[name] = [word]
    self.phoneme_feats = phoneme_features.CombilexPhonemes()
    print "Done."
  
  #Returns a whitespace delimited phoneme string of an entry
  def get_entry_phonemes(self, entry, with_syll_stress=False):
    phonemes = ""
    for s in entry["syllables"]:
      for p in s["phonemes"]:
        phonemes += " "+p["id"]
      if with_syll_stress == True:
        phonemes += " "+s["stress"]
    return phonemes.strip()
  
  #Makes a dictionary entry as if it exists in the dictionary.
  #Pos = the words pos to use
  #Phonemisation = The phonemisation in a whitespace delimited string - please use numbers as stress indicators
  #and syllable boundary markers. 0 = no stress and 1 = stressed. E.g. "p l a y 0 i N 1"
  #Reduced = Is this a reduced form?
  def make_entry(self, pos, phonemisation, reduced=False):
    entry = {"pos":pos, "reduced":reduced, "syllables":[]}
    c_syll = {"id":"", "phonemes":[], "stress":None}
    c_phon = {"id":None, "stress":None, "start":None, "end":None}
    phonemes = phonemisation.split()
    for i, p in enumerate(phonemes):
      if p.isalpha():
        c_syll["id"] += p
        c_phon["id"] = p
        c_syll["phonemes"].append(c_phon)
        c_phon = {"id":None, "stress":None, "start":None, "end":None}
      elif p in ["0", "1", "2"]:
        c_syll["stress"] = p
        entry["syllables"].append(c_syll)
        c_syll = {"id":"", "phonemes":[], "stress":None}
    return entry
  
  def get_entries(self, word, punct_as_sil=None):
    try:
      return self.raw_dictionary_entries[word]
    except KeyError:
      #If this has underscores we try to pronounce each letter individually.
      if "_" in word:
        #The total phoneme string
        w_phon = ""
        for w in word.split("_"):
          #Get the entry
          ent = self.get_single_entry(w)
          #Get the phoneme string with syllable stress
          ent = self.get_entry_phonemes(ent, True)
          w_phon += " "+ent
        print "Warning! \"{0}\" looks like it should be pronounced {1} and is a proper noun. I'm doing that. Is it right?".format(word, w_phon)
        return [self.make_entry("nnp", w_phon.strip(), reduced=False)]
      elif punct_as_sil and word in punct_as_sil[0]:
        if punct_as_sil[1] in self.phoneme_feats.get_sil_phonemes():
          return [self.make_entry(punct_as_sil[1], punct_as_sil[1]+" 0")]
        else:
          raise SiReError("Cannot add punctuation {0} as silence as sil phoneme specified ({1}) is not valid! Must be in {3}.".format(word, punct_as_sil[1], phoneme_feats.get_sil_phonemes()))
      else:
        raise SiReError("Could not find \"{0}\" in dictionary! Please add it manually.".format(word))

  #This returns the first non-reduced phomisation of a word in the dictionary.
  #Words not in the dictionary but with underscores between letters are
  #treated as needing seperate pronunciations.
  #If a POS is specified we return the first non-reduced word with the specified POS.
  #Else the first reduced witht the POS and finally if no other with another POS.
  #If reduced is specified we aim to deliver a reduced version.
  #If punct_as_sil is specified pass a tuple containing t[0] a list of pucntuation to be silence
  #and t[1] the phoneme to represent the silence both as phoneme and pos.
  def get_single_entry(self, word, pos=None, reduced=False, punct_as_sil=None):
    entries = self.get_entries(word, punct_as_sil)
    if len(entries) > 1:
      pos_added = False
      c_best = entries[0]
      for entry in entries:
        #If we have a pos tag to go by
        if pos != None:
          if pos == entry["pos"]:
            if entry["reduced"] == reduced:
              return entry
            else:
              c_best = entry
              pos_added = True
          #If we have a non-reduced word and we do not have one with the correct
          #pos we overwrite the previous best.
          elif entry["reduced"] == False and pos_added == False:
            c_best = entry
        #If we don't have a pos tag to go by but match the reduction desired
        elif entry["reduced"] == reduced:
          return entry
      if pos_added == False and pos != None:
        print "Warning: Could not find word with correct POS of \"{0}\" for POS {1}!\nReturning word which may be wrongly reduced.".format(word, pos)
        return c_best
      else:
        print "Warning: Could only find wrong reduction form of \"{0}\"! It is {1} that this should have been reduced.".format(word, reduced)
        return c_best
    else:
      e = entries[0]
      if e["reduced"] != reduced:
        print "Warning: I only had one entry in the dictionary and it was not reduced correctly! It is {0} that \"{1}\" should have been reduced.".format(reduced, word)
      return e
  
  #Returns the output of get_single_entry in the form used for alignment or phoneme ngram rescoring.
  #Output is list of phonemes.
  def get_single_lattice_entry(self, word, no_syll_stress, pos=None):
    entry = self.get_single_entry(word, pos)
    if no_syll_stress == True:
      return self.get_phoneme_ngram_phonemes(entry)
    else:
      return self.get_align_phonemes(entry)
  
  def get_align_phonemes(self, entry):
    entry = self.get_entry_phonemes(entry, with_syll_stress=True).split()
    #Fix syllable stress markers and boundaries
    for i, p in enumerate(entry):
      if p in ["1", "2"]:
        entry[i] = "#"+p
      elif p == "0":
        #If it is mid-word make it a dot
        if i+1 != len(entry):
          entry[i] = "."
    #Remove 0 stress markers left over
    while "0" in entry:
      entry.remove("0")
    return entry
  
  #Returns a list of strings for each variant of a word in dict.
  def get_all_lattice_entries(self, word, no_syll_stress):
    entries = self.get_entries(word)
    phonemes = []
    for entry in entries:
      if no_syll_stress == True:
        phonemes.append(self.get_phoneme_ngram_phonemes(entry))
      else:
        phonemes.append(self.get_align_phonemes(entry))
    #Some might be duplicates in terms of pronunciation, we remove those.
    return list_utils.unique_list_of_lists(phonemes)
  
  #Returns a list of phoneme lm strings for each variant of a word in dict.
  def get_all_phoneme_ngram_entries(self, word):
    entries = self.get_entries(word)
    phonemes = []
    for entry in entries:
      phonemes.append(self.get_phoneme_ngram_phonemes(entry))
    #Some might be duplicates in terms of pronunciation, we remove those.
    return list_utils.unique_list_of_lists(phonemes)
  
  #Here syllable stress markers are replaced with a syllable boundary makrer "sb".
  def get_phoneme_ngram_phonemes(self, entry):
    entry = self.get_entry_phonemes(entry, with_syll_stress=True).split()
    #Fix syllable stress markers and boundaries
    to_remove = []
    for i, p in enumerate(entry):
      if p in ["0", "1", "2"]:
        #If it is mid-word we replace it with sb
        if i+1 != len(entry):
          entry[i] = "sb"
        else:
          #If it is end of word it must be removed
          to_remove.append(p)
    #Remove end of word stress markers
    for p in to_remove:
      entry.remove(p)
    return entry
