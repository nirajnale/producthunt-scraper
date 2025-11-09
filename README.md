# 🧠 Product Hunt Scraper Suite

A **fully automated Product Hunt data extractor** built using `Selenium` and `undetected-chromedriver`.  
This suite includes three modular scrapers that work together to collect detailed product, maker, and launch data from Product Hunt — all executable via a single command.

---

## 📁 Project Structure

```
niraj-deliverables/
└── producthunt_scraper/
    ├── archive_scraper.py     # Stage 1 - Scrapes product listing archive
    ├── product_scraper.py     # Stage 2 - Extracts product details (website, makers)
    ├── profile_scraper.py     # Stage 3 - Extracts maker profile social links
    ├── run_all.py             # Runs all three scripts sequentially
    ├── requirements.txt       # Dependencies list
    └── README.md              # Project documentation
```

---

## 🚀 Overview

### Stage 1 — `archive_scraper.py`
- Scrapes Product Hunt **archive / All** tab for product cards.
- Captures: **Title, URL, Description, Tags, Votes** (as implemented in the script).  
- Saves output to `output1.csv`.

> Note: script does not currently extract product "headline" or "date" fields — it writes the fields listed above.

### Stage 2 — `product_scraper.py`
- Reads from `output1.csv`.  
- Visits each **product page**.  
- Collects **company Website** (from Product Hunt product page) and top **makers** (name + profile URL, up to 7).  
- **Keeps all original columns intact** (merges new fields into the existing rows).  
- Outputs to `output2.csv`.

### Stage 3 — `profile_scraper.py`
- Reads from `output2.csv`.  
- Visits each **maker profile page** on Product Hunt.  
- **Extracts links only from the profile "Links" section** (LinkedIn, Twitter/X, GitHub, YouTube, Instagram, Blog, Facebook, Telegram, Website).  
- Adds new columns for each maker’s social links in the format `Maker{n}_{Platform}` and inserts them after the corresponding `Maker{n}_Link` column.  
- Outputs to `output_final_<timestamp>.csv` (timestamped filename — e.g. `output_final_20251023_104501.csv`).

> Note: the profile scraper's current implementation only scrapes links from the "Links" section. It does *not* extract follower counts, headlines, or other profile metadata unless you add that logic.

---

## ⚙️ Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/<your-org>/niraj-deliverables.git
   cd niraj-deliverables/producthunt_scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional)** Set a Chrome user data directory in your environment (Windows example):
   ```powershell
   setx USER_DATA_DIR "C:\Users\<YourName>\AppData\Local\Google\Chrome\User Data"
   ```
   This helps reuse cookies and reduce login popups. Or edit the `USER_DATA_DIR` variable inside each script.

---

## 🖥️ Usage

### ▶️ Run all scrapers (Recommended)
To run the full pipeline in sequence:
```bash
python run_all.py
```
This will:
1. Run `archive_scraper.py` → produces `output1.csv`
2. Run `product_scraper.py` → reads `output1.csv`, produces `output2.csv`
3. Run `profile_scraper.py` → reads `output2.csv`, produces `output_final_<timestamp>.csv`

Each stage will automatically start after the previous one finishes. If you see a `ROW_LIMIT` in `profile_scraper.py` (useful for testing), remove or increase it to process the full dataset.

---

### 🧩 Run individually (optional)
```bash
python archive_scraper.py
python product_scraper.py
python profile_scraper.py
```

---

## 📊 Output Files

| Stage | Script | Output File Pattern | Description |
|:------|:--------|:---------------------|:-------------|
| 1 | archive_scraper.py | `output1.csv` | Product list from archive (Title, URL, Description, Tags, Votes) |
| 2 | product_scraper.py | `output2.csv` | Adds product Website and Maker columns; retains all original columns |
| 3 | profile_scraper.py | `output_final_<timestamp>.csv` | Final enriched CSV with social links (MakerX_Website, MakerX_Linkedin, ...) |

---

## 💡 Tips & Notes

- `undetected-chromedriver` helps reduce automation detection, but Product Hunt may still throttle or show captchas. Use a persistent Chrome profile (`USER_DATA_DIR`) to reduce friction.
- The scripts rely on CSS selectors and page structure — Product Hunt layout updates may break selectors; update them if scraping fails.
- `ROW_LIMIT` in `profile_scraper.py` is for testing. Set it to `None` or remove the `head()` line to process the full `output2.csv`.
- Consider adding exponential backoff or random delays if you plan to run at scale.

---

## 🧰 Troubleshooting

| Issue | Possible Fix |
|-------|---------------|
| Chrome opens and closes immediately | Ensure Chrome & `undetected-chromedriver` versions are compatible. Update packages. |
| No data saved / empty CSV | Check that the previous stage created the expected CSV (`output1.csv` → `output2.csv`). Increase wait times. |
| Missing columns in final file | Make sure you ran `product_scraper.py` (it merges and retains original columns). Also verify filenames are not overwritten. |
| `ROW_LIMIT` limiting rows | Remove or increase `ROW_LIMIT` in `profile_scraper.py` for full runs. |
| Encoding issues opening CSV in Excel | Open with UTF-8, or re-save using pandas with `encoding='utf-8-sig'`. |

---
## 🤝 Contributors

**Developed by:** Niraj Vijaysinh Nale 
