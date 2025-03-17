import re
import csv

def sort_references(ref):
    """Sorts references according to chapter and verse, handling ranges correctly."""
    match = re.match(r'(\d+)(–\d+)?(:)(\d+)(–\d+)?', ref)

    if not match:
        # Handle cases like "14" or "14–15" (chapter only, or chapter range)
        chapter_match = re.match(r'(\d+)(–\d+)?', ref)
        if chapter_match:
            chapter = int(chapter_match.group(1))  # Chapter number
            return (chapter, 0, 0)  # Only chapter, no verse

        return (float('inf'), '', float('inf'))  # Place unrecognized formats last
    
    chapter = int(match.group(1))  # Chapter number
    verse_start = int(match.group(4))  # Starting verse number
    verse_end = int(match.group(5)[1:]) if match.group(5) else verse_start  # Ending verse, if any

    return (chapter, verse_start, verse_end)

def combine_page_ranges(pages):
    """Combines sequential page numbers into ranges using en-dashes and proper elision."""
    pages = sorted(pages)
    ranges = []
    start = pages[0]
    prev = pages[0]

    for num in pages[1:]:
        if num == prev + 1:
            prev = num
        else:
            ranges.append(format_range(start, prev))
            start = prev = num
    
    ranges.append(format_range(start, prev))
    
    return ", ".join(ranges)

def format_range(start, end):
    """Formats a page range according to elision rules."""
    if start == end:
        return str(start)
    
    if start < 100 and end < 100:  # Both numbers are two-digit
        if start // 10 == end // 10:  # Same hundred
            if 10 <= start <= 19 or 10 <= end <= 19:  # Teens keep full form
                return f"{start}–{end}"
            return f"{start}–{end % 10}"
    
    if start // 100 == end // 100:  # Same hundred
        if 10 <= start % 100 <= 19 or 10 <= end % 100 <= 19:  # Teens keep full form
            return f"{start}–{end % 100}"
        elif start // 10 == end // 10:
            return f"{start}–{end % 10}"
        return f"{start}–{end % 100}"
    
    return f"{start}–{end}"

def create_index(file_path, output_file):
    processed_references = []
    skipped_references = []  # Track skipped references

    # Open and read the TSV file
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')

        for row in reader:
            if not row or not row[0].isdigit():  # Skip empty lines or invalid page numbers
                continue

            page = int(row[0])  # First column is the page number

            for reference in row[1:]:
                reference = reference.strip()
                if not reference:  # Skip empty reference
                    continue
                if reference.count(' ') < 1:  # If the reference doesn't include a book or page info
                    skipped_references.append(reference)  # Add to skipped references
                else:
                    processed_references.append((page, reference))  # Add to valid references

    # Process references and group them by book
    references_dict = {}
    for page, reference in processed_references:
        book, _, ref = reference.rpartition(' ')  # Split at the last space
        if book and ref:
            if book not in references_dict:
                references_dict[book] = {}
            references_dict[book].setdefault(ref, set()).add(page)  # Add page number to set for unique pages

    # Sort and format output
    index_output = []
    for book, refs in sorted(references_dict.items()):
        index_output.append(f"{book}")
        for ref, pages in sorted(refs.items(), key=lambda x: sort_references(x[0])):
            page_ranges = combine_page_ranges(sorted(pages))  # Convert set to sorted list and merge ranges
            index_output.append(f"\t{ref}\t{page_ranges}")

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(index_output))

    print(f"Index successfully written to {output_file}")

    # Print skipped references
    if skipped_references:
        print("\nSkipped references (not included in the output):")
        for ref in skipped_references:
            print(ref)
    else:
        print("\nNo references were skipped.")


# Specify the input and output file paths
input_file = 'first_proof_data.tsv'
output_file = 'tsv_indexed_data.txt'

# Generate the index
create_index(input_file, output_file)
