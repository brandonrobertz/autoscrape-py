# Autoscrape

This is an automated scraper of structured data from interactive web pages. The
goal is to be able to point this scraper at any site with interactive search
forms, pages, etc., and both crawl the site and extract any structured data.
The initial prototype version will use brute force, then machine learning and,
finally, reinforcement learning. Note that while we could use other (Scala,
Clojure, Go) languages for this, Python was selected because of the large ML
and RL ecosystem.

