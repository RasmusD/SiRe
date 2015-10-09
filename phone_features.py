import argparse

#Make the phone dct
global phones

phones = {}
#The meaning of each element of the list is
#[0] - VOC: Vowel (v) or Consonant (c)
#[1] - VL: Vowel length: short (sh) long (l) dipthong (d) schwa (sc) consonant (c)
#[2] - VH: Vowel height: high (h) mid (m) low (l) consonant (c)
#[3] - VF: Vowel frontness: front (f) mid (m) back (b) consonant (c)
#[4] - VL: Vowel lip round: Rounded (r) unrounded (u) consonant (c)
#[5] - CT: Consonant Type: stop (s) fricative (f) affricative (af) nasal (n) liquid (l) approximant (ap) vowel (v)
#[6] - CA: Consonant Place of Articulation: labial (la) alveolar (a) palatal (p) labio-dental (ld) dental (d) velar (ve) glottal (g) vowel (vo)
#[7] - V: Voicing: Voiced (v) unvoiced (u)
phones["p"] = ["c", "c", "c", "c", "c","s","la", "u"] #p
phones["t"] = ["c", "c", "c", "c", "c","s","a", "u"] #t
#phones["?"] = ["c", "c", "c", "c", "c","s","g", "v"] #glottal stop
phones["G"] = ["c", "c", "c", "c", "c","s","g", "v"] #glottal stop
phones["t^"] = ["c", "c", "c", "c", "c","ap","a", "v"] #t^ - not sure what else to call it to clarify, not used often in english at all
phones["g"] = ["c", "c", "c", "c", "c","s","ve", "v"] #g
phones["k"] = ["c", "c", "c", "c", "c","s","ve", "u"] #k
phones["m"] = ["c", "c", "c", "c", "c","n","la", "v"] #m
phones["b"] = ["c", "c", "c", "c", "c","s","la", "v"] #b
phones["d"] = ["c", "c", "c", "c", "c","s","a", "v"] #d
phones["x"] = ["c", "c", "c", "c", "c","f","ve", "u"] #not "ex" but the "ch" sound in "loch" (as Scots pronounce it)
phones["tS"] = ["c", "c", "c", "c", "c","af","p", "u"] #"ch" in e.g. "achieve"
phones["dZ"] = ["c", "c", "c", "c", "c","af","p", "v"] #"g" in e.g. "anthology"
phones["s"] = ["c", "c", "c", "c", "c","f","a", "u"] #s
phones["z"] = ["c", "c", "c", "c", "c","f","a", "v"] #z (not "zed" but "zee")
phones["S"] = ["c", "c", "c", "c", "c","f","p", "u"] #"sh" as in "ship"
phones["Z"] = ["c", "c", "c", "c", "c","f","p", "v"] #"g" as in "genre" - pronounced like "zh"
phones["f"] = ["c", "c", "c", "c", "c","f","ld", "u"] #f
phones["v"] = ["c", "c", "c", "c", "c","f","ld", "v"] #v
phones["T"] = ["c", "c", "c", "c", "c","f","d", "u"] #"th" as in "think"
phones["D"] = ["c", "c", "c", "c", "c","f","d", "v"] #the "th" in "that" but pronounced "dh"
phones["h"] = ["c", "c", "c", "c", "c","f","g", "u"] #h
phones["m!"] = ["c", "c", "c", "c", "c","n","la", "v"] #"m" in "-ism" ending of words
phones["n"] = ["c", "c", "c", "c", "c","n","a", "v"] #n
phones["n!"] = ["c", "c", "c", "c", "c","n","a", "v"] #"n" in "-tion" ending of words
phones["N"] = ["c", "c", "c", "c", "c","n","ve", "v"] #"ng" in "-ing" ending (when the g is not pronounced fully)
phones["l"] = ["c", "c", "c", "c", "c","l","a", "v"] #l
#phones["K"] = ["c", "c", "c", "c", "c","l","a", "u"] #ll - Not used in Combilex RPX, GAM or EDI
phones["lw"] = ["c", "c", "c", "c", "c","l","a", "v"] #"l" as in "double"
phones["l!"] = ["c", "c", "c", "c", "c","l","a", "v"] #"l" as in "dwindle"
phones["r"] = ["c", "c", "c", "c", "c","ap","a", "v"] #r
phones["j"] = ["c", "c", "c", "c", "c","l","p", "v"] #y - Why it is not just y in name I don't understand
phones["w"] = ["c", "c", "c", "c", "c","l","la", "v"] #w
#phones["W"] = ["c", "c", "c", "c", "c","f","la", "u"] #hw - Not used in Combilex RPX, GAM or EDI
phones["E"] = ["v", "sh", "m", "f", "u","v","vo", "v"] #e
phones["a"] = ["v", "sh", "l", "f", "u","v","vo", "v"] #a
phones["A"] = ["v", "l", "l", "b", "u","v","vo", "v"] #The second a in "advance" a long "aa"
#phones["Ar"] = ["v", "l", "l", "f", "f","v","vo", "v"] #ar - Not used in Combilex RPX, GAM or EDI
phones["@U"] = ["v", "d", "m", "b", "r","v","vo", "v"] #The "oa" in "float" pronounced more like "ou"
phones["o^"] = ["v", "l", "m", "b", "r","v","vo", "v"] #Often used in French loan-words as a pronounciation variant e.g. "ont" in "montmarte" when pronounced without the "nt"
phones["e^"] = ["v", "l", "m", "f", "r","v","vo", "v"] #Often used in French loan-words as a pronounciation variant e.g. "in" in "chargrin" when pronounced without the "n"
#phones["9^"] = ["v", "l", "l", "f", "r","n","vo", "v"] #Not used in Combilex RPX, GAM or EDI
phones["Q"] = ["v", "sh", "l", "b", "r","v","vo", "v"] #"o" in "pot"
#phones["QO"] = ["v", "l", "l", "b", "r","v","vo", "v"] #au - Not used in Combilex RPX, GAM or EDI
phones["O"] = ["v", "l", "m", "b", "r","v","vo", "v"] #"o" in "bomb" sort of "oo"
phones["Or"] = ["v", "l", "m", "b", "r","v","vo", "v"] #Rhotic "o" as in GAM "board" - Not used in Combilex RPX and EDI
#phones["@Ur"] = ["v", "l", "m", "b", "r","v","vo", "v"] #our - Not used in Combilex RPX, EDI or GAM
phones["i"] = ["v", "l", "h", "f", "u","v","vo", "v"] #"ii" as in "-cy" and "-ry" ending
#phones["iy"] = ["v", "s", "h", "f", "u","v","vo", "v"] #iy - Not used in Combilex RPX, GAM or EDI
phones["I"] = ["v", "sh", "h", "f", "u","v","vo", "v"] #"i" as first i in "mini" (second is ii above)
phones["@r"] = ["v", "sc", "m", "m", "u","v","vo", "v"] #@r - Rhotic @ as "e" in "moaner" - Not used in Combilex RPX and EDI  (yet somehow VCTK manages it? Perhaps it is a manually added word)
phones["@"] = ["v", "sc", "m", "m", "u","v","vo", "v"] #@/THE schwa
phones["V"] = ["v", "sh", "l", "m", "u","v","vo", "v"] #"u" in "strut", also current "uh" sound
phones["U"] = ["v", "sh", "h", "b", "r","v","vo", "v"] #Short "u" as in "foot"
phones["u"] = ["v", "l", "h", "b", "r","v","vo", "v"] #Long "u" as in "pool"
phones["eI"] = ["v", "d", "m", "f", "u","v","vo", "v"] #ei
phones["aI"] = ["v", "d", "l", "m", "u","v","vo", "v"] #ai
#phones["aIr"] = ["v", "d", "l", "m", "u","v","vo", "v"] #Rhotic "ai" as in GAM "hire" - Not used in Combilex RPX and EDI
phones["ae"] = ["v", "d", "l", "m", "u","v","vo", "v"] #"ae" as "i" in EDI "migrate" - Not used in Combilex RPX and GAM
#phones["aer"] = ["v", "d", "l", "m", "u","v","vo", "v"] #Rhotic aer - Not used in Combilex RPX, EDI and GAM
phones["OI"] = ["v", "d", "m", "b", "r","v","vo", "v"] #"oi" as in "point"
#phones["OIr"] = ["v", "d", "m", "b", "r","v","vo", "v"] #Rhotic oi as in GAM "coir" - Not used in Combilex RPX and EDI
phones["aU"] = ["v", "d", "l", "m", "u","v","vo", "v"] #"ow" sound as in "house"
#phones["aUr"] = ["v", "d", "l", "m", "u","v","vo", "v"] # Rhotic "ow" - Not used in Combilex GAM, RPX or EDI
#phones["i@"] = ["v", "d", "h", "f", "u","v","vo", "v"] #i@ - Not used in Combilex GAM, RPX or EDI
phones["I@"] = ["v", "d", "h", "f", "u","v","vo", "v"] #"I@" sound as "ea" in "idea"
phones["@@"] = ["v", "l", "m", "m", "u","v","vo", "v"] #"@@" as only vowel pronounced in "burse" in RPX and EDI (also used in GAM in some loan words e.g. "eu" in "peugot")
phones["@@r"] = ["v", "l", "m", "m", "u","v","vo", "v"] #Rhotic "@@" as only vowel pronounced in "burse" in GAM - Not used in RPX and EDI
#phones["Er"] = ["v", "sh", "m", "f", "u","v","vo", "v"] #er - Not used in combilex RPX, GAM or EDI
phones["E@"] = ["v", "sh", "m", "f", "u","v","vo", "v"] #"eir" sound as "air" in "cairn"
phones["U@"] = ["v", "d", "h", "b", "r","v","vo", "v"] #"u" part of "caricature" often in conjunction with "j" (caricat j U@ re)
phones["#"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #Around utt silence
phones["sil"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #silence
phones["pau"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #pause
#phones["sp"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "u"] #short pause - should preferably not exist
phones["xx"] = ["xx", "xx", "xx", "xx", "xx","xx","xx", "xx"] #Pre-utt
phones["novowel"] = ["c", "c", "c", "c", "c","xx","xx", "xx"] #If cur syll contains no vowel
#phones["0"] = ["c", "c", "c", "c", "c","xx","xx", "xx"] #Probably happens as vowel of syll by mistake some times
phones["UH"] = ["v", "sh", "l", "m", "u","v","vo", "v"] #"uh" sound - for testing if seperating gives better results

#Returns the phonemes considered silence
def get_sil_phonemes():
  return ["sil", "pau", "#"]

def get_phone_feats(phone):
  global phones
  return phones[phone]

def get_phoneme_feats_dict(phone):
  global phones
  p = phones[phone]
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

def get_phones():
  global phones
  return phones.keys()

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

def is_vowel(phone):
  global phones
  if phones[phone][7] == "v":
    return True
  else:
    return False
