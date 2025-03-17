import pdfplumber
import re
import csv

# Input and output file names
input_pdf = "test.pdf"
output_tsv = "Raw_Scripture_Index.tsv"
page_count = 0

# Define regex patterns
chapter_verse_pattern = r"\b(?:chapter|verse|Chapter|Verse|chapters|verses|Chapters|Verses) [\d–]+\b"

# Valid names and abbreviations from SBL Handbook of Style
valid_names = {
    "Genesis", "Gen", "Exodus", "Exod", "Leviticus", "Lev", "Numbers", "Num",
    "Deuteronomy", "Deut", "Joshua", "Josh", "Judges", "Judg", "Ruth", "Ruth",
    "1 Samuel", "1 Sam", "2 Samuel", "2 Sam", "1 Kings", "1 Kgs", "2 Kings", "2 Kgs",
    "1 Chronicles", "1 Chron", "2 Chronicles", "2 Chron", "Ezra", "Ezra", "Nehemiah", "Neh",
    "Esther", "Est", "Job", "Job", "Psalms", "Ps", "Proverbs", "Prov", "Ecclesiastes", "Eccl",
    "Song of Solomon", "Song", "Isaiah", "Isa", "Jeremiah", "Jer", "Lamentations", "Lam",
    "Ezekiel", "Ezek", "Daniel", "Dan", "Hosea", "Hos", "Joel", "Joel", "Amos", "Amos",
    "Obadiah", "Obad", "Jonah", "Jon", "Micah", "Mic", "Nahum", "Nah", "Habakkuk", "Hab",
    "Zephaniah", "Zeph", "Haggai", "Hag", "Zechariah", "Zech", "Malachi", "Mal",
    "Matthew", "Matt", "Mark", "Luke", "John", "Acts", "Romans", "Rom", 
    "1 Corinthians", "1 Cor", "2 Corinthians", "2 Cor", "Galatians", "Gal", "Ephesians", "Eph", 
    "Philippians", "Phil", "Colossians", "Col", "1 Thessalonians", "1 Thess", "2 Thessalonians", 
    "2 Thess", "1 Timothy", "1 Tim", "2 Timothy", "2 Tim", "Titus", "Phlm", "Hebrews", "Heb", 
    "James", "Jas", "1 Peter", "1 Pet", "2 Peter", "2 Pet", "1 John", "2 John", "3 John", "Jude", "Rev", 
    "Tobit", "Tob", "Judith", "Jdt", "Additions to Esther", "Add Esth", "Wisdom of Solomon", "Wis", 
    "Sirach", "Sir", "Baruch", "Bar", "Letter of Jeremiah", "Ep Jer", "Prayer of Azariah", "Pr Azar", 
    "Susanna", "Sus", "Bel and the Dragon", "Bel", "1 Maccabees", "1 Macc", "2 Maccabees", "2 Macc", 
    "3 Maccabees", "3 Macc", "4 Maccabees", "4 Macc", "4 Ezra", "1 Esdras", "1 Esd", "2 Esdras", "2 Esd", 
    "Prayer of Manasseh", "Pr Man", "Psalm 151", "Ps 151", "1 Enoch", "1 En", "2 Enoch", "2 En", 
    "3 Enoch", "3 En", "Sibylline Oracles", "Sib Or", "Psalms of Solomon", "Ps Sol", "Odes of Solomon", 
    "Odes Sol", "Testament of Abraham", "T Abr", "T Abr A", "T Abr B", "Testament of Isaac", "T Isa", "Testament of Jacob", 
    "T Jac", "Testament of the Twelve Patriarchs", "T 12 Patr", "Testament of Levi", "T Levi", 
    "Testament of Judah", "T Jud", "Testament of Joseph", "T Jos", "Testament of Benjamin", "T Benj", 
    "Testament of Moses", "T Mos", "Testament of Solomon", "T Sol", "Life of Adam and Eve", "LAE", 
    "Apocalypse of Abraham", "Apoc Abr", "Apocalypse of Moses", "Apoc Mos", "Ascension of Isaiah", 
    "Ascen Isa", "2 Baruch", "2 Bar", "3 Baruch", "3 Bar", "Greek Apocalypse of Baruch", "Gk Apoc Bar", 
    "Letter of Aristeas", "Let Aris", "Martyrdom of Isaiah", "Mart Isa", "Lives of the Prophets", 
    "Lives Prop", "Apocryphon of Ezekiel", "Apoc Ezek", "Vision of Ezra", "Vis Ezra", 
    "Apocalypse of Zephaniah", "Apoc Zeph"
}

# Create regex for book references dynamically
valid_names_regex = r"(?:{})* *?[\d–]+:[\d–:, ]*".format("|".join(re.escape(name) for name in valid_names))

# Regex for unattached chapter:verse references (not preceded by a valid name)
unattached_verse_pattern = r"(?:{}) [\d–]+(?![:\d–])".format("|".join(re.escape(name) for name in valid_names))

# Use PDF index as the page number (1-based instead of 0-based)
with pdfplumber.open(input_pdf) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):  # Start counting from 1
        page_count += 1  # Increment counter

# Function to filter results by valid names
def filter_results(results):
    filtered = []
    for result in results:
        words = result.split()
        if any(word in valid_names for word in words):
            filtered.append(result)
    return filtered

# Extract text and process
data = []

with pdfplumber.open(input_pdf) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):  # Start counting from 1
        print(f"Processing page {page_number}...")
        text = page.extract_text()
        if not text:
            continue
        
        # Get the first few lines to check for a page number
        lines = text.split("\n")
        current_page_number = page_number  

        # Extract words with position metadata
        words = page.extract_words()
        if words:
            footnote_threshold = min(
                w["top"] for w in words if "size" in w and w["size"] < 9
            ) if any("size" in w and w["size"] < 9 for w in words) else float("inf")

            main_text_lines = []
            text_started = False  

            for line in lines:
                if text_started:
                    if re.match(r"^\d+\s", line):  
                        break  
                elif line.strip():  
                    text_started = True  

                if any(
                    c["top"] < footnote_threshold for c in page.chars if c["text"] in line
                ):
                    main_text_lines.append(line)

            main_text = " ".join(main_text_lines)
            main_text = re.sub('– ', '–', main_text)

        # Find all matches with their positions
        matches = []

        for pattern in [chapter_verse_pattern, valid_names_regex, unattached_verse_pattern]:
            for match in re.finditer(pattern, main_text):
                match_text = match.group()  # Get the matched text
                match_text = match_text.strip()
                match_text = re.sub(r'[: ,]$', '', match_text)
                match_text = re.sub(r'[: ,]$', '', match_text)
                if re.match(r"Hebrews \d{2,}", match_text) and int(match_text.split()[1]) > 20:
                    continue  # Skip this match
                if re.match(r'.*::.*', match_text):
                    continue
                matches.append((match.start(), match_text))  # Append the updated text instead of the original

        # Sort matches by their order in the text
        matches.sort(key=lambda x: x[0])

        # Store results, keeping elements in order
        if matches:
            data.append([page_number] + [m[1] for m in matches])

# Write results to TSV
with open(output_tsv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(data)

print(f"Extraction complete. Results saved in {output_tsv}.")
