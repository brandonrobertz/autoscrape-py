"""
                   given (initial page), load it
                               │
                               ↓
              look for search form (possibly classifier)
                               │
                               ↓
               identify forms on page that require input
           (begin with config then move to heuristic then ML)
                               │
                               ↓
              initialize iterators for required inputs
              (begin with config/brute force, then RL)
                               │
                               ↓
                   enter data into form inputs
                               │
                               ↓
                  submit form and load next page
                               │
                               ↓
           ┌──────────🠦 scrape the page
           │                   │
           │                   ↓
           │         look for a next button
           │             (classifier)
           │                   │
           │                   ↓ YES
           └─────── click the next button & load page
"""
class AutoScraper(object):
    pass
