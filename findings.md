# Findings: "localisations_1_2_1.plist" Audit

## Summary: DO NOT SHIP 1.2.1
The file "localisations_1_2_1.plist" is <b>not safe to ship</b> in its current state. Running the tool against the live baseline (1.2.0) flagged a <b>Critical</b> issues alongside other moderate structural issues and changes and some lesser-important content that needs confirmation from Design and Localisation teams before release.

## 1. Highest-Risk Issues ("CRITICAL")

Found automatically by "HeavyPriorityChecks":

- Broken "%u" Placeholder and, due to similar origin, flagged malformed "%" token ("ru" in 2b827952-8d1a-4c31-9283-8753d1fc51be):
    - 1.2.0: "До начала %u"
    - 1.2.1: "До начала %..."
    - Impact: The "u" placeholder was dropped, leaving a bare "%" followed by "...". Depending on formatting, this will either crash the client at runtime or render broken text.

- Empty Translation ("it" in "2b827952-8d1a-4c31-9283-8753d1fc51be"):  
    - 1.2.0: ""Inizio tra %u...""
    - 1.2.1: (Empty "<string></string>")
    - Impact: Italian players will see a blank prompt for countdown purposes.


## 2. Warnings Requiring Release Sign-Off ("MODERATE")

Found automatically by "MidPriorityChecks": these may be intentional product decisions, but require human verification before shipping:

- Language Swapped Across All Keys ("es" removed, "jp" added):  
    - Spanish ("es") was present in all 3 keys in "1.2.0" and has been completely removed in "1.2.1", while Japanese ("jp") was added across all keys. If dropping Spanish was unintentional, Spanish players will fall back to English or missing text.
    - Removed UUID ("7a794655-44e9-49d6-99c6-df936bec3fcc" — "Play as Guest"):  
    Entirely removed in "1.2.1". Needs confirmation that the guest login UI flow was deprecated in the client; otherwise, the login screen button will break.


## 3. Low-Priority Info and Changes ("NON-CRITICAL" fixes)

- Intentional Fix Not Flagged as an Error ("fr" in "2b827952-8d1a-4c31-9283-8753d1fc51be"):  
    - In "1.2.0", French had a broken placeholder (""Commence dans % ...""). In "1.2.1", it was fixed to ""Commence dans %u..."". The tool validates "1.2.1" against the "en-US" truth rather than blindly flagging line diffs, therefore this fix cleanly passes without generating false-positive noise for the releaser. 
- Version Metadata has not been increased:  
    - The "<key>version</key>" in "localisations_1_2_1.plist" is still set to "1.2.0".
- Added UUIDs:  
    - "9bb069bc-a70c-45ce-875b-225f8ccef615" and "1981dc5a-a6b8-4fd3-be04-052522e08c86" were added.


## 4. Proposed Team Workflow

To catch these issues without slowing down LiveOps releases, I recommend integrating this tool in two stages:

1. Automated Jenkins PR/Pre-Merge Stage ("--fail-on critical"):
- Add a Jenkins pipeline stage that triggers automatically whenever a branch or Pull Request modifies `.plist` files
    - since the tool exits with code "1" on Critical issues and "2" on malformed XML, broken placeholders, empty strings, or missing per-UUID language entries will have the build failed by Jenkins immediately, and give the author exact line feedback, disallowing the PR
    - there could also be an option to "--fail-on moderate" if desired, as to make sure no issues other than (NON-CRITICAL) are able to pass through the validation pipeline

2.   Monday Morning Release Checklist:  
- During the (assumed) 15-minute pre-release check, the releaser reviews the CLI summary output (or CI job log) specifically to eyeball the (MODERATE) section (confirming whether removed UUIDs or dropped languages match the release notes) before hitting deploy.
    - the (INFO) part can also be considered important. For example, the releaser may want to change the version number and check if the new UUIDs have been added 