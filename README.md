# Literature Radar

Literature Radar is a Python 3.9+ service that checks a journal whitelist for the previous completed Monday-to-Monday window, filters and ranks relevant papers, translates titles, summarizes the strongest matches, emails a Markdown report, and rebuilds a GitHub Pages archive.

## Configuration

`config.yaml` is pre-filled with the email account, keywords, exclusions, journals, timezone, and summary limit. Later, edit that file on GitHub to update keywords or journals; the next scheduled run will use the changes.

Credentials are never stored in `config.yaml`. The program requires these environment variables:

- `EMAIL_AUTHORIZATION_CODE`
- `OPENALEX_API_KEY`
- `DEEPSEEK_API_KEY`

Rotate any credential that was previously committed or shared. Never paste a new credential into a tracked file.

## Local verification

Install Python 3.9, 3.10, or 3.11, then run:

```bash
py -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python test.py
```

`test.py` performs live SMTP authentication and small OpenAlex and DeepSeek requests. It does not send an email. Every check prints `PASS` or `FAIL` and the process exits with status 1 if any check fails.

Before running locally in PowerShell, set the three credentials for the current terminal session:

```powershell
$env:EMAIL_AUTHORIZATION_CODE = "your-new-qq-mail-authorization-code"
$env:OPENALEX_API_KEY = "your-new-openalex-key"
$env:DEEPSEEK_API_KEY = "your-new-deepseek-key"
```

Do not type the example words literally. Replace each quoted value with the corresponding new credential. Closing PowerShell clears these session-only values.

With the virtual environment active, run `python src/main.py` for a complete local delivery. This updates history before translating, summarizing, and emailing, so do not use the complete command merely as a connectivity test.

## GitHub deployment

1. Create a GitHub repository and push this directory to its default branch.
2. Open **Settings → Secrets and variables → Actions** and add the three repository secrets listed above.
3. Open **Actions**, enable workflows if prompted, select **Weekly Literature Radar**, and click **Run workflow** for the first manual run.
4. In **Settings → Pages**, set **Source** to **GitHub Actions**. The workflow publishes only `index.html` and `reports/`; it never publishes `config.yaml` or source files.
5. Leave Actions enabled. The workflow runs each Monday at 01:30 UTC, which is 09:30 in Beijing.

GitHub schedules can start several minutes late during periods of high load. The retrieval range remains an exact completed Monday-to-Monday window regardless of the actual start minute.

## Output and verification

- Weekly reports: `reports/weekly_report_YYYY-MM-DD.md`
- Persistent deduplication: `history.json`
- File logs: `logs/run_YYYY-MM-DD.log`
- Workflow logs: the run page under the repository's **Actions** tab
- Archive: `https://<github-user>.github.io/<repository>/`

After the first successful run, verify that the report arrived in the configured mailbox, the report and history were committed, and the GitHub Pages archive lists the new report.

## Troubleshooting

- **SMTP authentication fails:** confirm QQ Mail SMTP is enabled and the authorization code is still valid. QQ can revoke a code after a security event.
- **OpenAlex fails:** verify the API key, inspect the HTTP status in `logs/`, and rerun the workflow after a transient outage.
- **DeepSeek summaries are missing:** verify the key, account balance, endpoint, and model name. Papers without abstracts are intentionally not summarized.
- **Translations keep the English title:** Google Translate was unreachable; this is non-critical and is recorded as a warning.
- **No email is sent:** email delivery is critical, so the main process exits with code 1 and the workflow does not commit generated files.
- **The archive does not update:** inspect the commit step, ensure Actions has write permission, and confirm Pages deploys from the default branch root.

Exit codes are 0 for success, 1 for email failure, 2 for configuration/dependency loading failure, and 99 for any other unexpected failure.
