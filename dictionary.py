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
import os, sys, list_utils, phoneme_features

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
          print "ERROR! Cannot parse entry in combilex:\n{0}".format(e)
          sys.exit()
        #Make entry the syllable structure
        entry = ") (".join(entry[1:])[:-1]
      else: #The entry is definitely not reduced
        entry = entry.split(" (")
        pos = entry[0].split("|")[0]
        reduced = False
        entry = " (".join(entry[1:])[:-1]
      #The entry is done
      if name in self.raw_dictionary_entries:
        self.raw_dictionary_entries[name] += [{"pos":pos, "reduced":reduced, "phonetics":entry}]
      else:
        self.raw_dictionary_entries[name] = [{"pos":pos, "reduced":reduced, "phonetics":entry}]
    self.phoneme_feats = phoneme_features.CombilexPhonemes()
    print "Done."
  
  #This returns the first non-reduced phomisation of a word in the dictionary.
  #Words not in the dictionary but with underscores between letters are
  #treated as needing seperate pronunciations.
  #If a POS is specified we return the first non-reduced word with the specified POS.
  #Else the first reduced witht the POS and finally if no other with another POS.
  #If reduced is specified we aim to deliver a reduced version.
  def get_single_entry(self, word, pos=None, reduced=False):
    try:
      entries = self.raw_dictionary_entries[word]
    except KeyError:
      #If this has udnerscores we try to pronounce each letter individually.
      if "_" in word:
        w_phon = []
        for w in word.split("_"):
          w_phon.append(self.get_single_entry(w))
        print "Warning! \"{0}\" looks like it should be pronounced {1}. I'm doing that. Is it right?".format(word, w_phon)
        return " ".join(w_phon)
      else:
        print "Error: Could not find \"{0}\" in dictionary! Please add it manually.".format(word)
      sys.exit()
    if len(entries) > 1:
      pos_added = False
      c_best = entries[0]["phonetics"]
      for entry in entries:
        #If we have a pos tag to go by
        if pos != None:
          if pos in entry["pos"]:
            if entry["reduced"] == reduced:
              return entry["phonetics"]
            else:
              c_best = entry["phonetics"]
              pos_added = True
          #If we have a non-reduced word and we do not have one with the correct
          #pos we overwrite the previous best.
          elif entry["reduced"] == False and pos_added == False:
            c_best = entry["phonetics"]
        #If we don't have a pos tag to go by but match the reduction desired
        elif entry["reduced"] == reduced:
          return entry["phonetics"]
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
      return e["phonetics"]
  
  #Returns the output of get_single_entry in the form used for alignment.
  #Output is list of phonemes.
  def get_single_align_entry(self, word, pos=None):
    entry = self.get_single_entry(word, pos)
    return self.convert_entry_phonetics_to_align_phonemes(entry)
  
  #Returns a list of alignment strings for each variant of a word in dict.
  def get_all_align_entries(self, word):
    try:
      entries = self.raw_dictionary_entries[word]
    except KeyError:
      #If this has underscores we try to pronounce each letter individually.
      if "_" in word:
        w_phon = []
        for w in word.split("_"):
          #Note the recursiveness here.
          w_phon.append(self.get_single_entry(w))
        print "Warning! \"{0}\" looks like it should be pronounced {1}. I'm doing that. Is it right?".format(word, w_phon)
        entries = [{"phonetics": " ".join(w_phon)}]
      else:
        print "Error: Could not find \"{0}\" in dictionary! Please add it manually.".format(word)
    phonemes = []
    for entry in entries:
      phonemes.append(self.convert_entry_phonetics_to_align_phonemes(entry["phonetics"]))
    #Some might be duplicates in terms of pronunciation, we remove those.
    return list_utils.unique_list_of_lists(phonemes)
  
  #Converts the standard combilex phonetics to alignment phonemes.
  def convert_entry_phonetics_to_align_phonemes(self, entry_phonetics):
    phonemes = []
    sylls = [x.strip("()") for x in entry_phonetics.split(") (")]
    s_len = len(sylls)-1
    for i, syll in enumerate(sylls):
      syll = syll.split(") ")
      #Append stress
      if syll[1] != "0":
        phonemes.append("#"+syll[1])
      phonemes += syll[0].split()
      #append a syllable boundary marker.
      if i != s_len:
        phonemes.append(".")
    return phonemes
