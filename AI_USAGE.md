# AI Usage Report

## Usage
Used the following tools:

- Github Copilot (agentic)
    - auto-completing purposes in prototype.ipynb and mid-priority and low-priority classes
    - speeding-up testing to better understand what path to pursue
    - regular expressions auto-complete
- Claude
    - explaining what placeholders are most commonly used in xml for variable usage in hypothetical applications
    - xpath query explaining and fixing, fine-tuning terminal colors and usability, feedback readability in the high-priority class (too much information was being received through dicts and lists in the set_feedback function)
    - cleaning up some classes that were becoming too convoluted, helping me with modularity
    - for the README I wanted to provide options for the broken documents and organize the expected output a bit better

## Moments

Discarded:
- Convoluted code
    - provided very complex checks that were redundant and non-modular in already existing functions
        - eg.,: Claude proposed a long menu of extra checks (whitespace, rename translations - ja vs jp -, untranslated copy), a full old-vs-new classification matrix and a findings-object refactor, which was rejected because the brief says not to be exhaustive here
- The first update to the "set_feedback" function, in the high priority class, was not making sense according to the returns fetched from other functions

Accepted:
- Modularity-based suggestions:
    - although by itself, it provided complex code, when asked to modularize it helped (eg., suggesting feedback handling without the - now removed - booleans I was using, passing them into a simple function and terminal feedback on the main.py)

## Verifying output

1. Validating by myself the code given - sometimes something felt off and convoluted, it tried to bring too many checks
    - the assignment itself asked for the checks to not be overly extensive, and some code was checking everything in a truly exhaustive way

2. Checked auto-complete suggestions from Github Copilot, detecting that some outputs from Claude lacked deeper context from my workspace 


## Notes and Surprises

- I wrote the broken file by hand, so I know exactly which defects are seeded and can check that the tool finds each one. Claude could help, but I wanted to break it intentionally

- Claude suggested the comparison against the en-US reference for the strings, in order to strengthen the placeholder-missing checks. This came as a great suggestion, when validating a bug on my "%" validation regex

- Claude pointed out that a space in the flags part of my placeholder regex made "50% discount" parse as a valid "%d" placeholder ("% d"), so a stray percent sign was silently accepted. I removed the space and now "50% discount" is reported as a stray "%". For a .plist file it has to be "%%". It flags as intended, in "Assumptions" (README.md)

