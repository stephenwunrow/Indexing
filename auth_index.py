import re
import pdfplumber

def extract_bibliography_from_pdf(file_path):
    """Extract bibliography entries from the PDF using hanging indent positions."""
    bibliography_entries = []
    
    with pdfplumber.open(file_path) as pdf:
        bibliography_started = False
        current_entry = ""

        for page in pdf.pages:
            char_data = page.chars  # Extract each character with position information
            current_line = ""
            previous_x = None

            print(f"\n--- Processing Page {page.page_number} ---")

            for char in char_data:
                char_text = char['text']
                char_x = char['x0']  # x-coordinate
                char_y = char['top']  # y-coordinate


                # Check if "BIBLIOGRAPHY" has been found, trigger bibliography collection
                if "BIBLIOGRAPHY" in char_text:
                    bibliography_started = True
                
                if bibliography_started:
                    # Check x-coordinate to identify first line (hanging indent) or continuation line
                    if char_x == 108.05:  # First line of a new entry
                        if current_entry.strip():  # If there's content in the current entry, store it
                            bibliography_entries.append(current_entry.strip())
                        current_entry = current_line.strip()  # Start a new entry
                    elif char_x >= 144.05:  # Continuation line (indented)
                        current_entry += " " + current_line.strip()  # Append continuation line to current entry

                    current_line = char_text  # Build the current line
                    previous_x = char_x

            # Add any remaining entry after the loop
            if current_entry.strip():
                bibliography_entries.append(current_entry.strip())

    print("\nExtracted Bibliography Entries:")
    for i, entry in enumerate(bibliography_entries):
        print(f"{i + 1}. {entry}")
    
    return bibliography_entries

def extract_last_names(entries):
    """Extract last names from bibliography entries."""
    last_names = []
    
    for entry in entries:
        # Use regex to capture last names before commas
        match = re.match(r'([^_\n,]+), ', entry)
        if match:
            last_name = match.group(1).strip()
            last_names.append(last_name)
    
    return last_names

def search_pdf_for_last_names(file_path, last_names):
    """Search the PDF for each last name and log the page number where it is found."""
    search_results = {}
    
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            
            for last_name in last_names:
                pattern = fr"\b{last_name}\b"  # Search for the exact last name
                
                if re.search(pattern, text):
                    if last_name not in search_results:
                        search_results[last_name] = []
                    search_results[last_name].append(page_num)

    return search_results

def main(file_path):
    # Step 1: Extract bibliography entries from the PDF
    entries = extract_bibliography_from_pdf(file_path)
    
    # Step 2: Extract last names from bibliography entries
    last_names = extract_last_names(entries)
    
    print("\nExtracted Last Names:")
    print(last_names)
    
    # Step 3: Search the PDF for last names and get page numbers
    search_results = search_pdf_for_last_names(file_path, last_names)
    
    print("\nSearch Results:")
    for last_name, pages in search_results.items():
        pages_str = ', '.join(map(str, pages))
        print(f"Last Name: {last_name} found on pages: {pages_str}")

# Example usage
source_file = 'test.pdf'  # Replace with your actual PDF file path
main(source_file)
