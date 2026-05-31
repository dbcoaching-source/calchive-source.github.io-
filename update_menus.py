#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_menus.py  --  CalcHive mega-menu batch updater

Replaces the hardcoded mega menu in every .html page with the new 35-tool
version (adds Social Security, Annuity vs Lump Sum, Roth Conversion, RMD,
and Mortgage Payoff vs Invest; updates the "30" counts to "35").

USAGE
    cd  <your calchive repo root>
    python3 update_menus.py            # update in place (writes .bak backups)
    python3 update_menus.py --dry-run  # preview what would change, touch nothing
    python3 update_menus.py /some/dir  # operate on a different folder

WHAT IT DOES
  * Finds the <div class="mega-overlay"> ... <div class="mega-menu"> block by
    walking div depth (robust to whitespace / minor markup differences).
  * Swaps in the NEW_MEGA block below.
  * Skips files that already contain "All 35 Free Calculators" (idempotent;
    leaves the 5 new tool pages untouched).
  * Skips and REPORTS any file where the block can't be located
    (e.g. a page with a custom header such as tools.html) so you can
    handle those by hand.
  * Writes <file>.bak before changing anything (unless --dry-run).

It does NOT touch the top header nav links or any hero copy. If your
home page or tools.html says "30 calculators" in body text, bump those
to "35" yourself -- see the note printed at the end.
"""
import os
import sys

NEW_MEGA = r"""<div class="mega-overlay" id="megaOverlay"></div>
<div class="mega-menu" id="megaMenu">
<div class="mega-inner">
<div class="mega-top">
  <span class="mega-title">All 35 Free Calculators</span>
  <div style="display:flex;align-items:center;gap:1.5rem">
    <a class="mega-all-link" href="/tools.html">Browse All Calculators &rarr;</a>
    <button class="mega-close" id="megaClose">&#x2715;</button>
  </div>
</div>
<div class="mega-grid">
<div class="mega-col"><h3>Home &amp; Mortgage</h3>
  <a href="/mortgage-calculator.html">Mortgage Calculator</a>
  <a href="/mortgage-refinance-calculator.html">Refinance Calculator</a>
  <a href="/mortgage-payoff-vs-invest-calculator.html">Payoff vs Invest</a>
  <a href="/rent-vs-buy-calculator.html">Rent vs Buy</a>
  <h3 style="margin-top:1rem">Loans</h3>
  <a href="/loan-calculator.html">Loan Calculator</a>
  <a href="/car-loan-calculator.html">Car Loan</a>
  <a href="/student-loan-calculator.html">Student Loan</a>
  <a href="/credit-card-payoff-calculator.html">Credit Card Payoff</a>
  <a href="/debt-snowball-calculator.html">Debt Snowball</a>
  <a href="/debt-to-income-calculator.html">Debt-to-Income</a>
</div>
<div class="mega-col"><h3>Savings &amp; Investing</h3>
  <a href="/compound-interest-calculator.html">Compound Interest</a>
  <a href="/savings-goal-calculator.html">Savings Goal</a>
  <a href="/savings-rate-calculator.html">Savings Rate</a>
  <a href="/emergency-fund-calculator.html">Emergency Fund</a>
  <a href="/investment-return-calculator.html">Investment Return</a>
  <a href="/dividend-calculator.html">Dividend Calculator</a>
  <a href="/roi-calculator.html">ROI Calculator</a>
  <a href="/401k-calculator.html">401k Calculator</a>
  <a href="/net-worth-calculator.html">Net Worth</a>
</div>
<div class="mega-col"><h3>Retirement</h3>
  <a href="/retirement-calculator.html">Retirement Calculator</a>
  <a href="/401k-calculator.html">401k Calculator</a>
  <a href="/pension-lump-sum-calculator.html">Pension: Lump Sum vs Monthly</a>
  <a href="/social-security-calculator.html">Social Security Age</a>
  <a href="/annuity-vs-lump-sum-calculator.html">Annuity vs Lump Sum</a>
  <a href="/roth-conversion-calculator.html">Roth Conversion</a>
  <a href="/rmd-calculator.html">RMD Calculator</a>
  <h3 style="margin-top:1rem">Tax &amp; Income</h3>
  <a href="/tax-bracket-calculator.html">Tax Bracket</a>
  <a href="/paycheck-calculator.html">Paycheck Calculator</a>
  <a href="/hourly-to-salary-calculator.html">Hourly to Salary</a>
  <a href="/salary-comparison-calculator.html">Salary Comparison</a>
</div>
<div class="mega-col"><h3>Budgeting</h3>
  <a href="/budget-planner.html">Budget Planner</a>
  <a href="/savings-goal-calculator.html">Savings Goal</a>
  <a href="/emergency-fund-calculator.html">Emergency Fund</a>
  <h3 style="margin-top:1rem">Business</h3>
  <a href="/break-even-calculator.html">Break Even</a>
  <a href="/invoice-generator.html">Invoice Generator</a>
  <a href="/roi-calculator.html">ROI Calculator</a>
</div>
<div class="mega-col"><h3>Other Tools</h3>
  <a href="/currency-converter.html">Currency Converter</a>
  <a href="/inflation-calculator.html">Inflation Calculator</a>
  <a href="/tip-calculator.html">Tip Calculator</a>
  <a href="/tools.html" style="color:#60a5fa;font-weight:600;margin-top:.5rem;display:block">View All 35 &rarr;</a>
</div>
</div>
</div>
</div>"""

START_MARKER = '<div class="mega-overlay"'
ALREADY_DONE = "All 35 Free Calculators"


def find_mega_block(html):
    """Return (start, end) char offsets covering the overlay + mega-menu divs,
    or None if the block can't be found. Uses div-depth counting so it doesn't
    depend on exact internal markup."""
    start = html.find(START_MARKER)
    if start < 0:
        return None
    pos = start
    end = None
    # Consume two consecutive sibling <div> elements: the overlay, then the menu.
    for _ in range(2):
        while pos < len(html) and html[pos] in " \n\r\t":
            pos += 1
        if not html.startswith("<div", pos):
            break
        depth = 0
        i = pos
        while i < len(html):
            nd = html.find("<div", i)
            cd = html.find("</div>", i)
            if cd == -1:
                return None
            if nd != -1 and nd < cd:
                depth += 1
                i = nd + 4
            else:
                depth -= 1
                i = cd + 6
                if depth == 0:
                    pos = i
                    break
        end = pos
    if end is None or end <= start:
        return None
    return (start, end)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    target = args[0] if args else "."

    files = sorted(f for f in os.listdir(target) if f.endswith(".html"))
    if not files:
        print("No .html files found in %s" % os.path.abspath(target))
        return

    updated, already, skipped = [], [], []
    for name in files:
        path = os.path.join(target, name)
        with open(path, "r", encoding="utf-8") as fh:
            html = fh.read()
        if ALREADY_DONE in html:
            already.append(name)
            continue
        span = find_mega_block(html)
        if not span:
            skipped.append(name)
            continue
        s, e = span
        new_html = html[:s] + NEW_MEGA + html[e:]
        if not dry:
            with open(path + ".bak", "w", encoding="utf-8") as bak:
                bak.write(html)
            with open(path, "w", encoding="utf-8") as out:
                out.write(new_html)
        updated.append(name)

    label = "WOULD UPDATE" if dry else "UPDATED"
    print("\n%s (%d):" % (label, len(updated)))
    for n in updated:
        print("   +", n)
    print("\nAlready had 35-tool menu, left alone (%d):" % len(already))
    for n in already:
        print("   =", n)
    if skipped:
        print("\n*** COULD NOT FIND MENU BLOCK -- handle by hand (%d):" % len(skipped))
        for n in skipped:
            print("   !", n)
    print("\nNote: this script only rewrites the dropdown mega menu. If your")
    print("home page or tools.html shows a '30 calculators' count or grid in")
    print("body text, update those to '35' (and add the 5 new tool cards to")
    print("tools.html) separately.")
    if dry:
        print("\nDRY RUN -- nothing was written. Re-run without --dry-run to apply.")
    else:
        print("\nDone. Backups saved as <file>.bak. Delete them once you've")
        print("confirmed the pages look right.")


if __name__ == "__main__":
    main()
