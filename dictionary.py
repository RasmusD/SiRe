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
      #The entry is done
      if name in self.raw_dictionary_entries:
        self.raw_dictionary_entries[name] += [{"pos":pos, "reduced":reduced, "phonetics":entry}]
      else:
        self.raw_dictionary_entries[name] = [{"pos":pos, "reduced":reduced, "phonetics":entry}]
    self.phoneme_feats = phoneme_features.CombilexPhonemes()
    print "Done."
  
  #Makes entry phonetics as if it existed in the dictionary.
  #Phonemisation = The phonemisation in a whitespace delimited string - please use numbers as stress indicators
  #and syllable boundary markers. 0 = no stress and 1 = stressed. E.g. "p l a y 0 i N 1"
  #TODO - Make it possible to output in cmudict format beside combilex.
  def make_entry_phonetics(self, phonemisation):
    entry = ""
    p_in_s = 0
    #Add each phoneme
    for i, p in enumerate(phonemisation.split()):
      if p.isalpha() and self.phoneme_feats.is_phoneme(p, fail=True):
        if p_in_s == 0:
          if i != 0:
            entry += " (("+p
          else:
            entry += "(("+p
        else:
          entry += " "+p
        p_in_s += 1
      else:
        #Check this is an int
        try:
          int(p)
        except ValueError:
          raise SiReError("Something wrong with phonemisation {0}!".format(phonemisation))
        entry += ") "+p+")"
        p_in_s = 0
    return entry
  
  #Makes a dictionary entry as if it exists in the dictionary.
  #Pos = the words pos to use
  #Phonemisation = The phonemisation in a whitespace delimited string - please use numbers as stress indicators
  #and syllable boundary markers. 0 = no stress and 1 = stressed. E.g. "p l a y 0 i N 1"
  #Reduced = Is this a reduced form?
  def make_entry(self, pos, phonemisation, reduced=False):
    phonetics = self.make_entry_phonetics(phonemisation)
    return [{"pos":pos, "reduced":reduced, "phonetics":phonetics}]
  
  def get_entries(self, word, punct_as_sil=None):
    try:
      return self.raw_dictionary_entries[word]
    except KeyError:
      #If this has underscores we try to pronounce each letter individually.
      if "_" in word:
        w_phon = []
        for w in word.split("_"):
          #Get the entry
          ent = self.get_single_entry(w)
          #Get the phoneme string
          ent = " ".join(self.convert_entry_phonetics_to_phoneme_string(ent, True, True, True))
          #Remove unnecessary syllable parts while keeping stress info
          ent = ent.replace("#", "")
          ent = ent.replace(" . ", " ")
          w_phon.append(ent)
        print "Warning! \"{0}\" looks like it should be pronounced {1} and is a proper noun. I'm doing that. Is it right?".format(word, w_phon)
        return self.make_entry("nnp", " ".join(w_phon))
      elif punct_as_sil and word in punct_as_sil[0]:
        if punct_as_sil[1] in self.phoneme_feats.get_sil_phonemes():
          return self.make_entry(punct_as_sil[1], punct_as_sil[1]+" 0")
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
    return self.convert_entry_phonetics_to_phoneme_string(entry, True)
  
  #Returns a list of alignment strings for each variant of a word in dict.
  def get_all_align_entries(self, word):
    entries = self.get_entries(word)
    phonemes = []
    for entry in entries:
      phonemes.append(self.convert_entry_phonetics_to_phoneme_string(entry["phonetics"], True))
    #Some might be duplicates in terms of pronunciation, we remove those.
    return list_utils.unique_list_of_lists(phonemes)
  
  #Converts the standard combilex phonetics to alignment phonemes.
  #If syll_info then we include syllable boundaries and syllable stress info.
  def convert_entry_phonetics_to_phoneme_string(self, entry_phonetics, syll_info=False, with_no_stress=False, append_syll_stress=False):
    phonemes = []
    sylls = [x.strip("()") for x in entry_phonetics.split(") (")]
    s_len = len(sylls)-1
    for i, syll in enumerate(sylls):
      syll = syll.split(") ")
      #Preppend stress
      if syll_info == True and append_syll_stress == False:
        if with_no_stress == True:
          phonemes.append("#"+syll[1])
        elif syll[1] != "0":
          phonemes.append("#"+syll[1])
      phonemes += syll[0].split()
      #Append stress
      if syll_info == True and append_syll_stress == True:
        if with_no_stress == True:
          phonemes.append("#"+syll[1])
        elif syll[1] != "0":
          phonemes.append("#"+syll[1])
      #Append a syllable boundary marker.
      if syll_info == True and i != s_len:
        phonemes.append(".")
    return phonemes
