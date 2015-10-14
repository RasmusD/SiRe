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
#self.combilex = the dictionary with its entries (see TODO for renaming)
#self.phoneme_feats = An instance of the relevant phoneme features for the relevant type of dictionary from phone_features.py
#TODO - Should be flexible which type of dictionary to create - currently only supports combilex.
class Dictionary(object):
  """A dictionary class."""
  
  #Create a combilex dictionary
  def __init__(self, path):
    print "Loading combilex..."
    entries = [x for x in open(os.path.join(path, "combilex.dict"), "r").readlines() if x[0] == "("]
    entries += [x for x in open(os.path.join(path, "combilex.add"), "r").readlines() if x[0] == "("]
    self.combilex = {}
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
      if name in self.combilex:
        self.combilex[name] += [{"pos":pos, "reduced":reduced, "phonetics":entry}]
      else:
        self.combilex[name] = [{"pos":pos, "reduced":reduced, "phonetics":entry}]
    self.phoneme_feats = phoneme_features.CombilexPhonemes()
    print "Done."
  
  #This returns the first non-reduced phomisation of a word in the dictionary.
  #Words not in the dictionary but with underscores between letters are
  #treated as needing seperate pronunciations.
  def get_single_entry(self, word):
    try:
      entries = self.combilex[word]
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
      added = False
      for entry in entries:
        if entry["reduced"] == False:
          return entry["phonetics"]
          added = True
          break
      if added == False:
        print "Warning: Could only find reduced form of {0}!".format(word)
        return entries[0]["phonetics"]
    else:
      return entries[0]["phonetics"]
  
  #Returns the output of get_single_entry in the form used for alignment.
  #Output is list of phonemes.
  def get_single_align_entry(self, word):
    entry = self.get_single_entry(word)
    return self.convert_entry_phonetics_to_align_phonemes(entry)
  
  #Returns a list of alignment strings for each variant of a word in dict.
  def get_all_align_entries(self, word):
    try:
      entries = self.combilex[word]
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
