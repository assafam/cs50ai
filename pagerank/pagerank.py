import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = dict()

    if len(corpus[page]):
        # All pages can be visited with probability '1 - damping_factor'
        damping_prob = (1 - damping_factor) / len(corpus)
        for k in corpus.keys():
            pages[k] = damping_prob

        # Linked pages can be also visited with probability damping_factor
        linked_prob = damping_factor / len(corpus[page])
        for link in corpus[page]:
            pages[link] += linked_prob
    else:
        # For pages with no links, next page is a random choice with equal probability 
        random_prob = 1 / len(corpus)
        for k in corpus.keys():
            pages[k] = random_prob
    
    assert 0.99 < sum(pages.values()) < 1.01

    return pages


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_visits = dict()
    for k in corpus.keys():
        page_visits[k] = 0

    # Choose first page at random
    page = random.choice(list(corpus.keys()))
    page_visits[page] += 1

    # Choose other pages according to the transition model
    for _ in range(n - 1):
        transition_prob = transition_model(corpus, page, damping_factor)
        page = random.choices(list(transition_prob.keys()), list(transition_prob.values()))[0]
        page_visits[page] += 1

    # Calculate PageRank
    page_rank = {p: page_visits[p] / n for p in page_visits.keys()}
    assert 0.99 < sum(page_rank.values()) < 1.01

    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    DIFF_THRESHOLD = 0.001

    # Assign initial PageRank score
    page_rank = dict()
    initial_score = 1 / len(corpus)
    for k in corpus.keys():
        page_rank[k] = initial_score

    # Update PageRank scores
    damping_update_factor = (1 - damping_factor) / len(corpus)
    while True:
        new_page_rank = dict()
        for page in corpus.keys():
            new_page_rank[page] = damping_update_factor

            for linking_page in corpus.keys():
                if page in corpus[linking_page]:
                    new_page_rank[page] += damping_factor * page_rank[linking_page] / len(corpus[linking_page])
                elif not len(corpus[linking_page]):
                    # A page without links is interpreted as having links to every page in the corpus
                    new_page_rank[page] += damping_factor * page_rank[linking_page] / len(corpus.keys())

        # Stop looping when updates converge
        last_update = True
        for page in corpus.keys():
            if abs(new_page_rank[page] - page_rank[page]) > DIFF_THRESHOLD:
                last_update = False

        page_rank = new_page_rank
        if last_update:
            break

    assert 0.99 < sum(page_rank.values()) < 1.01

    return page_rank


if __name__ == "__main__":
    main()
