import os
import re

import pdfminer.utils
from pdfminer.high_level import extract_text


#==========================================================================
# obecny extraktor z pdf na txt
#==========================================================================
def ex_path(file_path):
    text = extract_text(file_path)
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s,.;:!?"\'()\-–—]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    return cleaned_text

#==========================================================================
# zkontroluje adresar a vrati true pokud v nem bude pdf
#==========================================================================

