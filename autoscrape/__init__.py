"""
COMMAND        Logical Control Flow Step
--------       -------------------------------------------------------------------
INIT                     initialize & get entry point
                                     │
                                     ↓
                                 load page    🠤───────────────────┐
                                     │                            │
SELECT_LINK (index)                  │            click a link based on likelihood
                                     │               of finding a search form
                                     ↓                            │
             ┌────🠦 look for search form (possibly classifier) ───┘
             │                       │
             │                       │ FOUND
             │                       ↓
             │         identify forms on page that require input
             │     (begin with config then move to heuristic then ML)
             │                       │
             │                       ↓
             │      initialize iterators for required inputs
             │      (begin with config/brute force, then RL)
             │                       │
             │                       ↓
             └─────── are we at the end of our iterators?
                YES                  │
                                     ↓
INPUT (index, chars)     enter data into form inputs 🠤───────┐
                                     │                       │
                                     ↓                       │
SUBMIT (index)          submit form and load next page       │
                                     │                       │
                                     ↓                       │
                     ┌──────🠦 scrape the page                │
                     │               │                       │
                     │               ↓                       │
                     │     look for a next button ───────────┘
                     │         (classifier)        NOT FOUND
                     │               │
                     │               │ YES
                     │               ↓
SELECT_LINK (index)  └─── click the next button & load page
"""

class AutoScraper(object):
    pass

