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

import argparse

class CombilexPhonemes(object):
  def __init__(self):
    self.phonemes = {}
    #The meaning of each element of the list is
    #[0] - VOC: Vowel (v) or Consonant (c)
    #[1] - VL: Vowel length: short (sh) long (l) dipthong (d) schwa (sc) consonant (c)
    #[2] - VH: Vowel height: high (h) mid (m) low (l) consonant (c)
    #[3] - VF: Vowel frontness: front (f) mid (m) back (b) consonant (c)
    #[4] - VL: Vowel lip round: Rounded (r) unrounded (u) consonant (c)
    #[5] - CT: Consonant Type: stop (s) fricative (f) affricative (af) nasal (n) liquid (l) approximant (ap) vowel (v)
    #[6] - CA: Consonant Place of Articulation: labial (la) alveolar (a) palatal (p) labio-dental (ld) dental (d) velar (ve) glottal (g) vowel (vo)
    #[7] - V: Voicing: Voiced (v) unvoiced (u)
    self.phonemes["p"] = ["c", "c", "c", "c", "c","s","la", "u"] #p
    self.phonemes["t"] = ["c", "c", "c", "c", "c","s","a", "u"] #t
    #self.phonemes["?"] = ["c", "c", "c", "c", "c","s","g", "v"] #glottal stop
    self.phonemes["G"] = ["c", "c", "c", "c", "c","s","g", "v"] #glottal stop
    self.phonemes["t^"] = ["c", "c", "c", "c", "c","ap","a", "v"] #t^ - not sure what else to call it to clarify, not used often in english at all
    self.phonemes["g"] = ["c", "c", "c", "c", "c","s","ve", "v"] #g
    self.phonemes["k"] = ["c", "c", "c", "c", "c","s","ve", "u"] #k
    self.phonemes["m"] = ["c", "c", "c", "c", "c","n","la", "v"] #m
    self.phonemes["b"] = ["c", "c", "c", "c", "c","s","la", "v"] #b
    self.phonemes["d"] = ["c", "c", "c", "c", "c","s","a", "v"] #d
    self.phonemes["x"] = ["c", "c", "c", "c", "c","f","ve", "u"] #not "ex" but the "ch" sound in "loch" (as Scots pronounce it)
    self.phonemes["tS"] = ["c", "c", "c", "c", "c","af","p", "u"] #"ch" in e.g. "achieve"
    self.phonemes["dZ"] = ["c", "c", "c", "c", "c","af","p", "v"] #"g" in e.g. "anthology"
    self.phonemes["s"] = ["c", "c", "c", "c", "c","f","a", "u"] #s
    self.phonemes["z"] = ["c", "c", "c", "c", "c","f","a", "v"] #z (not "zed" but "zee")
    self.phonemes["S"] = ["c", "c", "c", "c", "c","f","p", "u"] #"sh" as in "ship"
    self.phonemes["Z"] = ["c", "c", "c", "c", "c","f","p", "v"] #"g" as in "genre" - pronounced like "zh"
    self.phonemes["f"] = ["c", "c", "c", "c", "c","f","ld", "u"] #f
    self.phonemes["v"] = ["c", "c", "c", "c", "c","f","ld", "v"] #v
    self.phonemes["T"] = ["c", "c", "c", "c", "c","f","d", "u"] #"th" as in "think"
    self.phonemes["D"] = ["c", "c", "c", "c", "c","f","d", "v"] #the "th" in "that" but pronounced "dh"
    self.phonemes["h"] = ["c", "c", "c", "c", "c","f","g", "u"] #h
    self.phonemes["m!"] = ["c", "c", "c", "c", "c","n","la", "v"] #"m" in "-ism" ending of words
    self.phonemes["n"] = ["c", "c", "c", "c", "c","n","a", "v"] #n
    self.phonemes["n!"] = ["c", "c", "c", "c", "c","n","a", "v"] #"n" in "-tion" ending of words
    self.phonemes["N"] = ["c", "c", "c", "c", "c","n","ve", "v"] #"ng" in "-ing" ending (when the g is not pronounced fully)
    self.phonemes["l"] = ["c", "c", "c", "c", "c","l","a", "v"] #l
    #self.phonemes["K"] = ["c", "c", "c", "c", "c","l","a", "u"] #ll - Not used in Combilex RPX, GAM or EDI
    self.phonemes["lw"] = ["c", "c", "c", "c", "c","l","a", "v"] #"l" as in "double"
    self.phonemes["l!"] = ["c", "c", "c", "c", "c","l","a", "v"] #"l" as in "dwindle"
    self.phonemes["r"] = ["c", "c", "c", "c", "c","ap","a", "v"] #r
    self.phonemes["j"] = ["c", "c", "c", "c", "c","l","p", "v"] #y - Why it is not just y in name I don't understand
    self.phonemes["w"] = ["c", "c", "c", "c", "c","l","la", "v"] #w
    #self.phonemes["W"] = ["c", "c", "c", "c", "c","f","la", "u"] #hw - Not used in Combilex RPX, GAM or EDI
    self.phonemes["E"] = ["v", "sh", "m", "f", "u","v","vo", "v"] #e
    self.phonemes["a"] = ["v", "sh", "l", "f", "u","v","vo", "v"] #a
    self.phonemes["A"] = ["v", "l", "l", "b", "u","v","vo", "v"] #The second a in "advance" a long "aa"
    #self.phonemes["Ar"] = ["v", "l", "l", "f", "f","v","vo", "v"] #ar - Not used in Combilex RPX, GAM or EDI
    self.phonemes["@U"] = ["v", "d", "m", "b", "r","v","vo", "v"] #The "oa" in "float" pronounced more like "ou"
    self.phonemes["o^"] = ["v", "l", "m", "b", "r","v","vo", "v"] #Often used in French loan-words as a pronounciation variant e.g. "ont" in "montmarte" when pronounced without the "nt"
    self.phonemes["e^"] = ["v", "l", "m", "f", "r","v","vo", "v"] #Often used in French loan-words as a pronounciation variant e.g. "in" in "chargrin" when pronounced without the "n"
    #self.phonemes["9^"] = ["v", "l", "l", "f", "r","n","vo", "v"] #Not used in Combilex RPX, GAM or EDI
    self.phonemes["Q"] = ["v", "sh", "l", "b", "r","v","vo", "v"] #"o" in "pot"
    #self.phonemes["QO"] = ["v", "l", "l", "b", "r","v","vo", "v"] #au - Not used in Combilex RPX, GAM or EDI
    self.phonemes["O"] = ["v", "l", "m", "b", "r","v","vo", "v"] #"o" in "bomb" sort of "oo"
    self.phonemes["Or"] = ["v", "l", "m", "b", "r","v","vo", "v"] #Rhotic "o" as in GAM "board" - Not used in Combilex RPX and EDI
    #self.phonemes["@Ur"] = ["v", "l", "m", "b", "r","v","vo", "v"] #our - Not used in Combilex RPX, EDI or GAM
    self.phonemes["i"] = ["v", "l", "h", "f", "u","v","vo", "v"] #"ii" as in "-cy" and "-ry" ending
    #self.phonemes["iy"] = ["v", "s", "h", "f", "u","v","vo", "v"] #iy - Not used in Combilex RPX, GAM or EDI
    self.phonemes["I"] = ["v", "sh", "h", "f", "u","v","vo", "v"] #"i" as first i in "mini" (second is ii above)
    self.phonemes["@r"] = ["v", "sc", "m", "m", "u","v","vo", "v"] #@r - Rhotic @ as "e" in "moaner" - Not used in Combilex RPX and EDI  (yet somehow VCTK manages it? Perhaps it is a manually added word)
    self.phonemes["@"] = ["v", "sc", "m", "m", "u","v","vo", "v"] #@/THE schwa
    self.phonemes["V"] = ["v", "sh", "l", "m", "u","v","vo", "v"] #"u" in "strut", also current "uh" sound
    self.phonemes["U"] = ["v", "sh", "h", "b", "r","v","vo", "v"] #Short "u" as in "foot"
    self.phonemes["u"] = ["v", "l", "h", "b", "r","v","vo", "v"] #Long "u" as in "pool"
    self.phonemes["eI"] = ["v", "d", "m", "f", "u","v","vo", "v"] #ei
    self.phonemes["aI"] = ["v", "d", "l", "m", "u","v","vo", "v"] #ai
    #self.phonemes["aIr"] = ["v", "d", "l", "m", "u","v","vo", "v"] #Rhotic "ai" as in GAM "hire" - Not used in Combilex RPX and EDI
    self.phonemes["ae"] = ["v", "d", "l", "m", "u","v","vo", "v"] #"ae" as "i" in EDI "migrate" - Not used in Combilex RPX and GAM
    #self.phonemes["aer"] = ["v", "d", "l", "m", "u","v","vo", "v"] #Rhotic aer - Not used in Combilex RPX, EDI and GAM
    self.phonemes["OI"] = ["v", "d", "m", "b", "r","v","vo", "v"] #"oi" as in "point"
    #self.phonemes["OIr"] = ["v", "d", "m", "b", "r","v","vo", "v"] #Rhotic oi as in GAM "coir" - Not used in Combilex RPX and EDI
    self.phonemes["aU"] = ["v", "d", "l", "m", "u","v","vo", "v"] #"ow" sound as in "house"
    #self.phonemes["aUr"] = ["v", "d", "l", "m", "u","v","vo", "v"] # Rhotic "ow" - Not used in Combilex GAM, RPX or EDI
    #self.phonemes["i@"] = ["v", "d", "h", "f", "u","v","vo", "v"] #i@ - Not used in Combilex GAM, RPX or EDI
    self.phonemes["I@"] = ["v", "d", "h", "f", "u","v","vo", "v"] #"I@" sound as "ea" in "idea"
    self.phonemes["@@"] = ["v", "l", "m", "m", "u","v","vo", "v"] #"@@" as only vowel pronounced in "burse" in RPX and EDI (also used in GAM in some loan words e.g. "eu" in "peugot")
    self.phonemes["@@r"] = ["v", "l", "m", "m", "u","v","vo", "v"] #Rhotic "@@" as only vowel pronounced in "burse" in GAM - Not used in RPX and EDI
    #self.phonemes["Er"] = ["v", "sh", "m", "f", "u","v","vo", "v"] #er - Not used in combilex RPX, GAM or EDI
    self.phonemes["E@"] = ["v", "sh", "m", "f", "u","v","vo", "v"] #"eir" sound as "air" in "cairn"
    self.phonemes["U@"] = ["v", "d", "h", "b", "r","v","vo", "v"] #"u" part of "caricature" often in conjunction with "j" (caricat j U@ re)
    self.phonemes["#"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #Around utt silence
    self.phonemes["sil"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #silence
    self.phonemes["pau"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #pause
    #self.phonemes["sp"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #short pause - should preferably not exist
    self.phonemes["xx"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "xx"] #Pre-utt
    self.phonemes["novowel"] = ["c", "c", "c", "c", "c","xx","xx", "xx"] #If cur syll contains no vowel
    self.phonemes["UH"] = ["v", "sh", "l", "m", "u","v","vo", "v"] #"uh" sound - for testing if seperating gives better results

  #Returns the phonemes considered silence
  def get_sil_phonemes():
    return ["sil", "pau", "#"]

  def get_phoneme_feats(phoneme):
    return self.phonemes[phoneme]

  def get_phoneme_feats_dict(phoneme):
    p = self.phonemes[phoneme]
    features = {}
    #Vowel or consonant
    features["VOC"] = p[0]
    #Vowel Length
    features["VL"] = p[1]
    #Vowel Height
    features["VH"] = p[2]
    #Vowel Frontedness
    features["VF"] = p[3]
    #Vowel Roundedness
    features["VR"] = p[4]
    #Consonant Type
    features["CT"] = p[5]
    #Consonant Place of Articulation
    features["CA"] = p[6]
    #Voicing
    features["V"] = p[7]
    return features

  def get_phonemes():
    return self.phonemes.keys()

  def get_feature_lists():
    features = {}
    #Vowel or consonant
    features["VOC"] = ["v", "c", "xx"]
    #Vowel Length
    features["VL"] = ["sh", "l", "d", "sc", "c", "xx"]
    #Vowel Height
    features["VH"] = ["h", "m", "l", "c", "xx"]
    #Vowel Frontedness
    features["VF"] = ["f", "m", "b", "c", "xx"]
    #Vowel Roundedness
    features["VR"] = ["r", "u", "c", "xx"]
    #Consonant Type
    features["CT"] = ["s", "f", "af", "n", "l", "ap", "v", "xx"]
    #Consonant Place of Articulation
    features["CA"] = ["la", "a", "p", "ld", "d", "ve", "g", "vo", "xx"]
    #Voicing
    features["V"] = ["v", "u", "xx"]
    return features

  def is_vowel(phoneme):
    self.phonemes
    if self.phonemes[phoneme][7] == "v":
      return True
    else:
      return False
