# Junior Tools Software Developer — Solution Henrique Matos

## Problems tackled and my rationale

It is desired for the tool to not be exhaustively detecting issues. The main scenario of having a developer checking critical issues in 15 minutes, in order to have the app deployed has been taking into consideration. Therefore, three check priorities made were conceived:
- Heavy Priority: critical issues that would break the app, rendering deployment completely unfeasible
- Mid Priority: warnings were the developer is able to understand non-breaking app fixes are to be made 
- Low Priority: information provided regarding metadata that is not in accordance to what is expected of it

Six areas of operation were detected, ranging from heavy to low priority.
1. Checking if any variable placeholders are missing (heavy-priority)
    - (CRITICAL) if a placeholder variable is missing, game-breaking artifacts may occur, leaving the app incomplete (due to code not loading what it should have been loaded) and the user frustrated due to broken components
2. Checking if no string is left empty, so that no localisation is missing (heavy-priority) 
    - (CRITICAL) missing text would leave users confused, from a usability standpoint; if a string is missing and if the code is not completely protected, the game component could break, leaving said part of the app unusable
3. Checking if any language keys have either changed or removed (mid-priority)
    - (WARNING) if a language has either been removed or a new one has been added (or even both at the same time), that could have been developer intent. Nevertheless, it was considered mid-priority due to assumptions made, as to be explained further in the document; could be deployed, assuming intent
5. Checking if any UUID keys have been removed (mid-priority);
    - (WARNING) removing UUID keys could be intentional, due to the phasing-out of a component. However, despite developer intent, a warning is to be triggered in order to alert and have the developer be sure intentions were met
6. Checking if the new .plist version is different, and higher (because a developer could've mistyped it to be lower) (low-priority)
    - (INFO) alerts regarding metada is not a priority to fix since it is assumed it does not directly intertwine with the game components
7. Checking if any UUID keys have been added (low-priority);
    - (INFO) if a new set of localisations is added, a new UUID will be consequently added

## Assumptions made

regarding enlgish and other stuff 



## Setup and Run 

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/main.py