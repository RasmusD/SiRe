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
from error_messages import SiReError

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
  def get_sil_phonemes(self):
    return ["sil", "pau", "#"]

  def get_phoneme_feats(self, phoneme):
    return self.phonemes[phoneme]

  def get_phoneme_feats_dict(self, phoneme):
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

  def get_phonemes(self):
    return self.phonemes.keys()

  def get_feature_lists(self):
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

  #Note that is_consonant and is_vowel are not completely opposite as silence phones are considered neither.
  #I.e. if you want to check if something is a vowel do not do is_consonant(phone) == False as this will also
  #Apply to silence.
  def is_vowel(self, phoneme):
    if self.phonemes[phoneme][0] == "v":
      return True
    else:
      return False

  def is_consonant(self, phoneme):
    if self.phonemes[phoneme][0] == "c":
      return True
    else:
      return False
  
  #Checks if a phoneme exist in the present set.
  #If fail is True it will fail if it is not.
  def is_phoneme(self, phoneme, fail=False):
    if phoneme in self.phonemes:
      return True
    else:
      if fail:
        raise SiReError("Phoneme ({0}) not a valid phoneme!".format(phoneme))
      return False


class CMUPhonemes(CombilexPhonemes):
    def __init__(self):
        # Initialise it as a combilex phoneset
        super(CombilexPhonemes, self).__init__()
        # Clear the combilex phones
        self.phonemes = {}
        # Insert the CMUDict ones/arpabet
        #The meaning of each element of the list is
        #[0] - VOC: Vowel (v) or Consonant (c)
        #[1] - VL: Vowel length: short (sh) long (l) dipthong (d) schwa (sc) consonant (c)
        #[2] - VH: Vowel height: high (h) mid-high (mh) mid (m) mid-low (ml) low (l) consonant (c)
        #[3] - VF: Vowel frontness: front (f) mid (m) back (b) consonant (c)
        #[4] - VL: Vowel lip round: Rounded (r) unrounded (u) consonant (c)
        #[5] - CT: Consonant Type: stop (s) fricative (f) affricative (af) nasal (n) liquid (l) approximant (ap) vowel (v)
        #[6] - CA: Consonant Place of Articulation: labial (la) alveolar (a) palatal (p) labio-dental (ld) dental (d) velar (ve) glottal (g) vowel (vo)
        #[7] - V: Voicing: Voiced (v) unvoiced (u)
        self.phonemes["aa"] = ["v", "sh", "l", "b", "u", "v", "vo", "v"] #AA    odd       AA D
        self.phonemes["ae"] = ["v", "sh", "ml", "f", "u", "v", "vo", "v"] #AE    at        AE T
        self.phonemes["ah"] = ["v", "sc", "m", "m", "u", "v", "vo", "v"] # AH    hut       HH AH T <- Rasmus: I don't like this one, it covers both the Schwa and ^ IPA symbols and it is terribly broad. Here written as schwa.
        self.phonemes["ao"] = ["v", "sh", "ml", "b", "r", "v", "vo", "v"] # AO    ought     AO T
        self.phonemes["aw"] = ["v", "d", "l", "m", "u", "v", "vo", "v"] # AW    cow       K AW        <- Rasmus: This is set as a low high mid-vowel though arguably it is moving from low to high, front to back.
        self.phonemes["ay"] = ["v", "d", "l", "m", "u", "v", "vo", "v"] # AY    hide      HH AY D     <- Rasmus: This is set as a low height vowel though arguably it is moving from low to high.
        self.phonemes["b"] = ["c", "c", "c", "c", "c", "s", "la", "v"] #b
        self.phonemes["ch"] = ["c", "c", "c", "c", "c", "af", "p", "u"] # CH    cheese    CH IY Z
        self.phonemes["d"] = ["c", "c", "c", "c", "c", "s", "a", "v"] #d
        self.phonemes["dh"] = ["c", "c", "c", "c", "c", "f", "d", "v"] #DH    thee      DH IY
        self.phonemes["eh"] = ["v", "sh", "ml", "f", "u", "v", "vo", "v"] # EH    Ed        EH D
        self.phonemes["er"] = ["v", "sh", "ml", "v", "u", "v", "vo", "v"] # ER    hurt      HH ER T
        self.phonemes["ey"] = ["v", "d", "mh", "f", "u", "v", "vo", "v"] # EY    ate       EY T      <- Rasmus: This is set as a mid-high vowel though arguably it is moving from mid-high to high.
        self.phonemes["f"] = ["c", "c", "c", "c", "c","f","ld", "u"] #f
        self.phonemes["v"] = ["c", "c", "c", "c", "c","f","ld", "v"] #v
        self.phonemes["g"] = ["c", "c", "c", "c", "c","s","ve", "v"] #g
        self.phonemes["hh"] = ["c", "c", "c", "c", "c","f","g", "u"] #h
        self.phonemes["ih"] = ["v", "s", "h", "f", "u","v","vo", "v"] # IH    it        IH T
        self.phonemes["iy"] = ["v", "l", "h", "f", "u","v","vo", "v"] # IY    eat       IY T
        self.phonemes["jh"] = ["c", "c", "c", "c", "c","af","p", "v"] # JH    gee       JH IY
        self.phonemes["k"] = ["c", "c", "c", "c", "c","s","ve", "u"] #k
        self.phonemes["l"] = ["c", "c", "c", "c", "c","l","a", "v"] #l
        self.phonemes["m"] = ["c", "c", "c", "c", "c","n","la", "v"] #m
        self.phonemes["n"] = ["c", "c", "c", "c", "c","n","a", "v"] #n
        self.phonemes["ng"] = ["c", "c", "c", "c", "c","n","ve", "v"] #"ng" in "-ing" ending (when the g is not pronounced fully)
        self.phonemes["ow"] = ["v", "d", "mh", "b", "r","v","vo", "v"] # OW    oat       OW T      <- Rasmus: This is set as a rounded vowel though arguably it is moving from rounded to unrounded.
        self.phonemes["oy"] = ["v", "d", "ml", "b", "r","v","vo", "v"] # OY    toy       T OY      <- Rasmus: This is set as a rounded back mid-low vowel though arguably it is moving from rounded back mid-low to unrounded front high.
        self.phonemes["p"] = ["c", "c", "c", "c", "c", "s", "la", "u"] #p 
        self.phonemes["r"] = ["c", "c", "c", "c", "c", "l","a", "v"] # R     read      R IY D    <- In combilex this is an approximant but in arpabet/cmudict a liquid. To distinguish it from l it has here only the id.
        self.phonemes["s"] = ["c", "c", "c", "c", "c","f","a", "u"] #s
        self.phonemes["sh"] = ["c", "c", "c", "c", "c","f","p", "u"] # SH    she       SH IY
        self.phonemes["t"] = ["c", "c", "c", "c", "c", "s", "a", "u"] #t
        self.phonemes["th"] = ["c", "c", "c", "c", "c","f","d", "u"] # TH    theta     TH EY T AH
        self.phonemes["uh"] = ["v", "s", "h", "b", "r","v","vo", "v"] # UH    hood      HH UH D
        self.phonemes["uw"] = ["v", "l", "h", "b", "r","v","vo", "v"] # UW    two       T UW
        self.phonemes["w"] = ["c", "c", "c", "c", "c","l","la", "v"] #w
        self.phonemes["y"] = ["c", "c", "c", "c", "c","l","p", "v"] # Y     yield     Y IY L D
        self.phonemes["z"] = ["c", "c", "c", "c", "c","f","a", "v"] # Z     zee       Z IY
        self.phonemes["zh"] = ["c", "c", "c", "c", "c","f","p", "v"] # ZH    seizure   S IY ZH ER
        self.phonemes["#"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #Around utt silence
        self.phonemes["sil"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #silence
        self.phonemes["pau"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #pause
        #self.phonemes["sp"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #short pause - should preferably not exist
        self.phonemes["xx"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "xx"] #Pre-utt
        self.phonemes["novowel"] = ["c", "c", "c", "c", "c","xx","xx", "xx"] #If cur syll contains no vowel
        self.phonemes["UH"] = ["v", "sh", "l", "m", "u","v","vo", "v"] #"uh" sound - for testing if seperating gives better results