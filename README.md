# CTL AI Regulation Atlas

A cumulative, student-coded register of how jurisdictions govern artificial intelligence, published by the
Centre for Technology and Law (CTL), Symbiosis Law School, Nagpur, as part of the Value Added Course on
AI Ethics and Legal Responsibility.

Each jurisdiction is a *plate*. A plate records, one row per legal instrument, what the instrument is, whom it
binds, what it requires, who enforces it, and the single most consequential gap in it, followed by a
plate-level synthesis: the governance model, the institutional map, two convergences with the wider atlas,
two gaps, and the coders' assumptions and limitations. Every plate names the students who coded its first version; the atlas is maintained and updated by the
Centre for Technology and Law, Symbiosis Law School, Nagpur.

**Release:** v1.0 (2026 cohort). **Last updated:** November 2026.

## Plates in this release

| Code | Jurisdiction | Governance model | Instruments | Binding | Soft law | Proposed | Contributors |
|---|---|---|---|---|---|---|---|
| EU | European Union | Comprehensive statute | 10 | 6 | 3 | 1 | 10 |
| IN | India | Hybrid | 12 | 5 | 4 | 3 | 16 |
| CN | China | Hybrid | 7 | 7 | 0 | 0 | 4 |
| JP | Japan | Soft-law-led | 9 | 3 | 6 | 0 | 3 |
| NG | Nigeria | Hybrid | 5 | 3 | 1 | 1 | 1 |

43 instruments in all. The remaining jurisdictions on the coverage list appear on the map marked
"coming soon".

## Repository layout

```
index.html                 the atlas (single page; map, plates, synthesis, citation)
data/jurisdictions.json    the coverage list shown on the map
data/plates/<code>.json    one file per coded plate: Part A instruments and Part B synthesis
data/atlas-register.csv    every instrument in one table, for cross-plate comparison (generated)
tools/build.py             validates the plates and regenerates the data embedded in index.html
```
## Citing a plate

> &lt;Contributors&gt;, '&lt;Jurisdiction&gt;' in *CTL AI Regulation Atlas*, v 1.0 (Centre for Technology and Law,
> Symbiosis Law School Nagpur 2026).

Note: Each plate page shows the full citation with its contributors. Contributors are listed alphabetically on each plate. Codings follow the CTL codebook as designed by Dr. Anshuman Sahoo, the VAC facilitator and faculty-in-charge of the Centre for Technology and Law. 
