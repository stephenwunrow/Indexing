# Process

`auth_index.py` is meant to read the bibliography and search for those names in the preceding text. Prints results.
Problems: does not account for "ibid," has not been tested, and does not create a file in index form. 

`scrip_index.py` searches the file for specific patterns, including verse references with and without book abbreviations. It compiles them into a tsv that needs to be checked manually, including adding book abbreviations when they are not present in the text. The checked file must be saved as 'first_proof_data.tsv'.
Problems: Cutting off when a footnote number is found occasionally cuts a whole page. Does not find every instance of individual references to chapters and verses.

`tsv_generate_index.py` pulls the data generated from `scrip_index.py`, sorts it, properly elides number ranges (for some styles), and prints an index. 
Problems: none that I'm aware of, but hasn't been tested extensively