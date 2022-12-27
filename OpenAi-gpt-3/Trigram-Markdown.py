import sys
import re
import markdown

# Read the input file name from the command line
input_file = sys.argv[1]

# Initialize a dictionary to store the tri-grams and their counts
trigrams = {}

# Regular expression to match YAML front matter
front_matter_regex = r'^---\s*$'

# Read the contents of the input file
with open(input_file, 'r') as f:
    # Flag to indicate if we are currently in the YAML front matter
    in_front_matter = False
    
    # Store the lines of the file in a list
    lines = f.readlines()
    
# Convert the Markdown text to plain text
plain_text = markdown.markdown(''.join(lines))

# Split the plain text into lines
lines = plain_text.splitlines()

# Iterate through the lines of the file
for line in lines:
        # Split the line into words
        words = line.split()
        
        # Iterate through the words in the line
        for i in range(len(words)-2):
            # Extract the current tri-gram
            trigram = ' '.join(words[i:i+3])
            
            # Increment the count for this tri-gram in the dictionary
            if trigram in trigrams:
                trigrams[trigram] += 1
            else:
                trigrams[trigram] = 1

# Sort the trigrams by count in descending order
sorted_trigrams = sorted(trigrams.items(), key=lambda x: x[1], reverse=True)

# Print the trigrams and their counts
for trigram, count in sorted_trigrams:
    print(f'{trigram}: {count}')
