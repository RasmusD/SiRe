import sys, argparse

# This is essentially a python version of the flite/lang/cmu_lex.c function cmu_syl_boundary for determining syllable boundaries in an utt.
# Here used to split a word's phones into syllables.
def syllabify(line):
  word = line.pop(0)
  sylls = []
  c_syll = []
  # For reasons unknown the flite/festival functions take their input in reverse
  # So we do that here because it was easier after having realised that's what they
  # were doing and I'd already written the function.
  stress = list(reversed([x for x in line if x in ["0", "1", "2"]]))
  phones = list(reversed([x for x in line if x not in ["0", "1", "2"]]))
  ln_phon = len(phones)-1
  # Only words with no vowel has no stress markers so just having one is suitable.
  if stress == []:
    stress.append("0")
  for i, p in enumerate(phones):
    # Add current phone
    c_syll.append(p)
    # If we are at the last phone finish the syll and break.
    if i == ln_phon:
      sylls.append((list(reversed(c_syll)), stress.pop(0)))
      c_syll = []
    # If there is not a vowel left continue.
    elif has_vowel_left(phones[i+1:]) == False:
      continue
    # If we have a vowel in the syllable.
    elif has_vowel_in_syll(c_syll) == True: 
      # So we have a vowel, if the next is a vowel there is a boundary.
      if is_vowel(phones[i+1]):
        sylls.append((list(reversed(c_syll)), stress.pop(0)))
        c_syll = []
      # If there is exactly one phone left we know it is not a vowel (from above test) so we are not done yet.
      elif i+1 == ln_phon:
        continue
      # So there is a vowel left and multiple phones
      else:
        # So we check sonority
        ps = sonority(p)
        ns = sonority(phones[i+1])
        nns = sonority(phones[i+2])
        # If the next two are increasingly sonorous this is a boundary
        # Rasmus - I'm not sure why this makes sense but this is the Flite implementation.
        if ps <= ns and ns <= nns:
          sylls.append((list(reversed(c_syll)), stress.pop(0)))
          c_syll = []
  return word, list(reversed(sylls))

# Based on cmu_sonority in flite/lang/cmu_lex.c - perhaps clearer in festival/src/arch/festival/Phone.cc ph_sonority (they are equal)
def sonority(phone):
  # Vowels
  if is_vowel(phone):
    return 5
  # Glides/liquids
  elif phone in ["w", "y", "l", "r"]:
    return 4
  # Nasals
  elif phone in ["n", "m", "ng"]:
    return 3
  # Voiced obstruents
  elif phone in ["b", "d", "dh", "g", "jh", "v", "z", "zh"]:
    return 2
  # Anything else
  else:
    return 1


def is_vowel(phone):
  # A vowel in CMUdict starts witgh any one of these
  if phone[0] in ["a", "e", "i", "o", "u"]:
    return True
  else:
    return False

def has_vowel_left(ls):
  return has_vowel_in_list(ls)

def has_vowel_in_syll(ls):
  return has_vowel_in_list(ls)

def has_vowel_in_list(ls):
  for p in ls:
    if is_vowel(p):
      return True
  return False 

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Syllabify and format CMUDict (0.7b equivalent) into the SiRe dict format (which is really the Combilex surface form form).')
  parser.add_argument('inpath', type=str, help="The input file.")
  parser.add_argument('outpath', type=str, help="The output filepath.")
  args = parser.parse_args()
  
  infile = [x.lower() for x in open(args.inpath, "r").readlines()]
  
  outfile = open(args.outpath, "w")
  
  outfile.write("############################\n")
  outfile.write("This CMUdict has been modified automaticelly by the SiRe script syllabifyCMUdict.py by Rasmus Dall, 2016.\n")
  outfile.write("############################\n")

  for l in infile:
    if ";;;" != l[:3]:
      #Fix pronunciation variants
      l = l.replace("(1)", "")
      l = l.replace("(2)", "")
      l = l.replace("(3)", "")
      #Pre split stress
      l = l.split()
      for i, p in enumerate(l):
        if i != 0:
          if p[-1] in ["0", "1", "2"]:
            tmp = p[-1]
            p = p[:-1]
            p = p + " " + tmp
            l[i] = p
      word, sylls = syllabify(" ".join(l).split())
      # We just don't want to deal with words starting in "
      if word[0] == "\"":
        word = word[1:]
      outfile.write("(\"{0}\" none (".format(word))
      for i, syll in enumerate(sylls):
        outfile.write("(({0}) {1})".format(" ".join(syll[0]), syll[1]))
        if i+1 != len(sylls):
          outfile.write(" ")
      outfile.write("))\n")
    else:
      # We keep the header
      outfile.write(l)
    
  outfile.close()
