# UK graduate pay, as a landscape

An interactive 3D map of the UK where every university is a glowing spike. Spike height is the median pay of its graduates for the degree you pick. Press play to watch the spikes grow from 1 to 3 to 5 years after graduating.

## What you can do

- **Spin and zoom.** Drag to spin. Pinch (or Ctrl-scroll) to zoom. Shift-drag or two fingers moves the map.
- **Switch degree.** Computer science, Economics, Maths, Business (incl. accounting & finance), Law, Engineering, Medicine, Nursing, Psychology, English and Creative arts are chips. The other 24 subjects are in a menu.
- **Vs UK average.** Recolours spikes by whether each university beats the national median for that subject.
- **Tap a spike** to see that university's median, the middle-half pay range, growth over 1/3/5 years, and its nearest rival across town.
- **Ranking table.** Every university for the chosen degree, highest pay first.

## Live demo

[Explore UK Graduate Pay](https://arikhanacademic-cpu.github.io/uk_grad_pay/)

## Run it

The page loads its data with `fetch`, so it needs to be served rather than opened as a file:

```bash
python -m http.server
# then open http://localhost:8000
```

To put it online, turn on **GitHub Pages** for this repo (Settings → Pages → Deploy from branch → `main` / root).

## Data

| File | What it is |
| --- | --- |
| `data/leo_earnings_2022-23.csv` | Median, lower-quartile and upper-quartile annual pay by university, subject (CAH level 2) and years after graduating. |
| `data/leo_national_2022-23.csv` | UK-wide median pay per subject and years after graduating. |
| `data/campus_positions.csv` | Approximate main-campus lat/lon, short name and Russell Group flag. **Hand-entered, not official.** |
| `data/uk_outline.json` | UK and Ireland coastline from Natural Earth (public domain). |

Pay figures come from the Department for Education’s **LEO graduate outcomes, provider-level data**: UK-domiciled first-degree graduates, all graduates, 2022–23 tax year, higher education institutions only. Source: explore-education-statistics.service.gov.uk.

### Rebuilding the data

1. Download the LEO provider-level zip and put it in `raw/` (it’s about 53 MB, so it isn’t committed).
2. Run:

```bash
pip install pandas
python scripts/build_data.py raw/leo-graduate-outcomes-provider-level-data_2022-23.zip
```

Campus positions live in `scripts/campuses.py`. Add an entry there for any new university.

## Caveats

- The 1, 3 and 5-year steps are three different graduating classes (2020–21, 2018–19, 2016–17) measured in the same tax year, not one group followed over time.
- A missing spike means the course was too small for the DfE to publish earnings.
- Pay reflects where graduates work (London pays more), their backgrounds and entry grades, not only the teaching.
- Accounting and finance are counted inside Business and management in this data.
- Distance and multi-site providers (Open University, University of London, BPP, University of Law, UCEM) are left off the map.
