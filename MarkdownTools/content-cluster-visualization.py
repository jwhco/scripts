

import os
import re
import sys
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# --- Configuration ---
ZETTEL_ROOT = "/home/hittjw/Documents/GitHub/obsidian/Zettelkasten"
N_CLUSTERS = 5

def extract_note_data(filepath):
    """
    Parses a markdown file for YAML tags, CamelCase hashtags, and body text.
    Returns a combined string of features and the filename.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (OSError, IOError) as e:
        sys.stderr.write(f"read_error: {filepath} - {e}\n")
        return None, None

    # 1. Extract YAML Tags
    yaml_tags = []
    yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        try:
            meta = yaml.safe_load(yaml_match.group(1))
            if meta and 'tags' in meta:
                tags = meta['tags']
                yaml_tags = tags if isinstance(tags, list) else [tags]
        except yaml.YAMLError:
            pass

    # 2. Extract CamelCase Hashtags (#DataScience, #NeuralNetworks)
    hashtags = re.findall(r'#([A-Z][a-z]+(?:[A-Z][a-z]+)+)', content)
    
    # 3. Clean Body (strip front matter)
    body = re.sub(r'^---\s*\n(.*?)\n---\s*\n', '', content, flags=re.DOTALL)
    
    # Concatenate features; tags are weighted by repetition
    feature_text = " ".join(map(str, yaml_tags)) + " " + " ".join(hashtags) + " " + body
    return feature_text.strip(), filepath.name

# --- Initialization ---
if not os.path.isdir(ZETTEL_ROOT):
    sys.stderr.write(f"directory_not_found: {ZETTEL_ROOT}\n")
    sys.exit(1)

data = []
# Case-insensitive search for .md files
files = list(Path(ZETTEL_ROOT).rglob('*.[mM][dD]'))

if not files:
    sys.stderr.write(f"no_files_found: {ZETTEL_ROOT} contains 0 markdown files.\n")
    sys.exit(1)

for path in files:
    text, name = extract_note_data(path)
    if text:
        data.append({'name': name, 'text': text})

if not data:
    sys.stderr.write("extraction_failed: No text content found in directory.\n")
    sys.exit(1)

df = pd.DataFrame(data)

# --- Vectorization & Clustering ---
# ngram_range=(1, 3) captures the requested trigrams
vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1, 3),
    max_features=1000
)

X = vectorizer.fit_transform(df['text'])

model = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
df['cluster'] = model.fit_predict(X)

# --- Dimensionality Reduction (PCA) ---
pca = PCA(n_components=2)
coords = pca.fit_transform(X.toarray())
df['x'], df['y'] = coords[:, 0], coords[:, 1]

# --- Visualization ---
plt.figure(figsize=(12, 8))
for i in range(N_CLUSTERS):
    cluster_slice = df[df['cluster'] == i]
    plt.scatter(cluster_slice['x'], cluster_slice['y'], label=f"Cluster {i}", alpha=0.7)

plt.title("Zettelkasten Content Clusters (PCA Projection)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# --- Cluster Summary ---
print("\n--- Top Identifiers per Cluster ---")
terms = vectorizer.get_feature_names_out()
centroids = model.cluster_centers_.argsort()[:, ::-1]

for i in range(N_CLUSTERS):
    top_terms = [terms[ind] for ind in centroids[i, :7]]
    print(f"Cluster {i}: {', '.join(top_terms)}")
    

