import argparse
import sys
from checks.heavy_priority_checks import HeavyPriorityChecks
from checks.mid_priority_checks import MidPriorityChecks
from checks.low_priority_checks import LowPriorityChecks
from checks.load_loc_docs import LoadLocDocs

# ANSI Terminal Colors
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

XQUERY_LOC = "//key[following-sibling::*[1][self::string]]/text()"
XQUERY_VER_NR = "/plist/dict/key[.='version']/following-sibling::string[1]/text()"


def parse_args():
    parser = argparse.ArgumentParser(description="Localization pre-flight check.")
    parser.add_argument(
        "--current", default="../docs/localisations_1_2_0.plist", help="Path to base version"
    )
    parser.add_argument(
        "--new", default="../docs/localisations_1_2_1.plist", help="Path to candidate version"
    )
    parser.add_argument(
        "--icons", default="./xml_icon_checks.json", help="Path to icon/placeholder JSON"
    )
    parser.add_argument(
        "--fail-on",
        choices=["critical", "moderate", "any"],
        default="critical",
        help="Severity threshold that triggers a non-zero exit code.",
    )
    return parser.parse_args()


def print_section(title, color, items):
    if not items:
        return
    print(f"\n{BOLD}{color}=== {title} ({len(items)} found) ==={RESET}")
    for item in items:
        indented = item.replace("\n", f"\n    ")
        print(f"  {color}•{RESET} {indented}")


def main():
    args = parse_args()

    docs = LoadLocDocs(args.current, args.new)
    doc_curr = docs.get_current_ver()
    doc_new = docs.get_new_ver()

    ##Initializing the 3 check scripts
    low = LowPriorityChecks(doc_curr, doc_new)
    mid = MidPriorityChecks(doc_curr, doc_new)
    heavy = HeavyPriorityChecks(doc_curr, doc_new)

    ##Executing checks
    #Low priority check
    new_version, status = low.compare_version_number(XQUERY_VER_NR)
    validate_key_diff_low = low.validate_key_diff()
    #Mid priority check
    removed, added = mid.compare_unique_localisations(XQUERY_LOC)
    validate_key_diff_mid = mid.validate_key_diff()
    #High priority check
    uuid_key_nr = heavy.get_uuid_key_counter(doc_new) 
    erratic = heavy.validate_erratic_placeholder()
    missing_pairs = heavy.validate_empty_string_loc()
    mismatched = heavy.validate_key_loc_number(doc_new, uuid_key_nr)

    ##Set the feedbacks
    heavy.set_feedback(mismatched, missing_pairs, erratic)
    mid.set_feedback(removed, added, validate_key_diff_mid)
    low.set_feedback(new_version, status, validate_key_diff_low)

    ##Collecting feedback from the checks
    critical_issues = getattr(heavy, "feedback", [])
    moderate_issues = getattr(mid, "feedback", [])
    low_issues = getattr(low, "feedback", [])

    ##Output full report
    print(f"\n{BOLD}Localization Audit Report{RESET}")
    print("-" * 30)

    print_section("CRITICAL ISSUES (Blockers)", RED, critical_issues)
    print_section("MODERATE ISSUES (Warnings)", YELLOW, moderate_issues)
    print_section("NON-CRITICAL ISSUES (Info)", BLUE, low_issues)

    has_critical = bool(critical_issues)
    has_moderate = bool(moderate_issues)
    has_low = bool(low_issues)

    if not (has_critical or has_moderate or has_low):
        print(f"\n{GREEN}{BOLD}✓ All localization checks passed successfully.{RESET}\n")
        sys.exit(0)

    ##Determine failure code based on threshold (how critical the feedback is)
    should_fail = (
        (args.fail_on == "critical" and has_critical)
        or (args.fail_on == "moderate" and (has_critical or has_moderate))
        or (args.fail_on == "any" and (has_critical or has_moderate or has_low))
    )

    if should_fail:
        print(f"\n{RED}{BOLD}DEPLOYMENT REJECTED:{RESET} Issues exceed the threshold (`--fail-on={args.fail_on}`).\n")
        sys.exit(1)
    else:
        print(f"\n{YELLOW}{BOLD}DEPLOYMENT PERMITTED WITH WARNINGS.{RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()