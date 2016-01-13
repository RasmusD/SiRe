##########################################################################
#Copyright 2016 Rasmus Dall                                              #
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

#A class for all prosody related methods.

from pos import is_festival_content
from error_messages import SiReError

#A simple method for accent prediction based on the simple intonation method of Festival (see http://www.festvox.org/docs/manual-2.4.0/festival_18.html#Simple-intonation)
#"It simply predicts accents on the stressed syllables on content words in poly-syllabic words, and on the only syllable in single syllable content words."
def simple_festival_accent_predict(utt):
  for word in utt.words:
    if is_festival_content(word.pos):
      if len(word.syllables) == 1:
        word.syllables[0].accent = 1
      else:
        for syll in word.syllables:
          if int(syll.stress) == 1:
            syll.accent = 1
          elif int(syll.stress) == 0 or int(syll.stress) == 2:
            syll.accent = 0
          else:
            raise SiReError("Syllable has invalid stress value({0})!".format(syll.stress))
    else:
      for syll in word.syllables:
        syll.accent = 0
