# Roadmap

This started out as a separation from the original beanhub importer due to frustrations with its fixed
extractors. The first goal was to allow extractors to be any importable python path.


Due to my workflow, there are some obvious improvements that can be made:

- [ ] Make it faster. Which might even mean a rewrite in Golang (or shudder, Rust).
- [ ] Change the config structure so that it is only a list of file globs, the associated extractor, and the associated import rules.
- [ ] When marshalling the rules in the configuration, uniquely identify rules that have no name
- [ ] When generating a transaction identify which rule was used to generate it
- [ ] Provide a Fava extension to facilitate various tasks:
  - [ ] When opening a transaction postings in the Journal, provide a UI to allow the user to use information
        in the transaction to quickly update or create a new rule.
  - [ ] Provide a UI to allow the user to view and edit rules in Fava
  - [ ] Provide a UI to allow the user to view the source documents.
  - [ ] When viewing a rule in fava allow the user to select some/all source documents to test the rule.
- [ ] Refactor how matchers are sourced so that custom ones can be provided by the user.
