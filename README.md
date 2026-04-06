# CP Solutions Hub

An interactive CLI to search and open your competitive programming solutions.

## Setup

1. **Install the one dependency:**
   ```bash
   pip install pyyaml
   ```

2. **Place `parse.py` and `index.py` in the same directory** (anywhere you like).

3. **Add frontmatter to your `.typ` files** (see spec below).

4. **Run:**
   ```bash
   python index.py /path/to/your/solutions
   # or if solutions/ is in the current dir:
   python index.py
   ```

---

## Frontmatter Spec

Add this block at the very top of each `.typ` file:

```typst
// ---
// title: Longest Increasing Subsequence
// source: Codeforces 1234A
// difficulty: 1800
// tags: dp, binary-search, greedy
// keywords: patience sorting, LIS, nlogn, segment tree
// ---
```

### Fields

| Field        | Type            | Description                                      |
|--------------|-----------------|--------------------------------------------------|
| `title`      | string          | Problem name. Falls back to folder name if absent.|
| `source`     | string          | Contest/platform and problem ID (e.g. `Codeforces 380C`, `USACO Dec22 Gold P1`) |
| `difficulty` | integer         | Numeric rating (e.g. Codeforces rating: 800–3500) |
| `tags`       | comma-separated | Algorithmic topics                               |
| `keywords`   | comma-separated | Solution-specific terms, techniques, data structures |

All fields are **optional**, but the more you fill in, the better the search.

---

## Folder Structure

Any structure works — the crawler finds all `.typ` files recursively:

```
content/
  codeforces-380C/
    solution.typ   ← frontmatter here
    solution.pdf
  usaco-dec22-gold-p1/
    solution.typ
    solution.pdf
  atcoder/
    abc123-f/
      main.typ
      main.pdf
```

The PDF in the **same folder** as the `.typ` file is opened automatically.

---

## Search Syntax

| Query                   | Meaning                              |
|-------------------------|--------------------------------------|
| `segment tree`          | Free text — matches title/source/tags/keywords |
| `tags:dp`               | Must have tag `dp`                   |
| `tags:dp,graph`         | Must have BOTH `dp` and `graph`      |
| `source:codeforces`     | Source contains "codeforces"         |
| `diff:1800`             | Exact difficulty 1800                |
| `diff:>1700`            | Difficulty strictly above 1700       |
| `diff:<2000`            | Difficulty strictly below 2000       |
| `diff:1600-1900`        | Difficulty in range [1600, 1900]     |

Combine freely:
```
search> tags:dp diff:>1700 source:codeforces knapsack
search> tags:graph,bfs diff:1200-1600
```

## Commands

| Command    | Action                          |
|------------|---------------------------------|
| `open <n>` | Open the nth result's PDF       |
| `typ <n>`  | Open the nth result's .typ file |
| `list`     | Show all problems               |
| `help`     | Show search syntax help         |
| `q`        | Quit                            |
