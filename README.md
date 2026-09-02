# Singlife Travel Claim — UAT Tester (GUI)

A point-and-click web app for running the three known Singlife Travel Claim
UAT test scenarios — no terminal, no command-line flags. Pick a scenario,
optionally tweak the amount, press **Run test claim**, and watch it go.

This is the same automation as the `singlife_travel_claim.py` CLI script,
wrapped in a [Streamlit](https://streamlit.io) front end so non-technical
teammates can use it from a browser.

**UAT / test data only.** Hard-pinned to the UAT portal; refuses to start
otherwise. See `singlife_travel_claim.py`'s own docstring for the full
safety notes — nothing about that has changed here.

## Deploying it (one-time setup, ~10 minutes)

You'll need a free [GitHub](https://github.com) account and a free
[Streamlit Community Cloud](https://streamlit.io/cloud) account (sign in
there with your GitHub account — no separate signup).

1. **Create a new GitHub repository.** On github.com, click **New
   repository**. Name it whatever you like (e.g. `singlife-uat-tester`).
   It can be private — Streamlit Community Cloud can deploy from private
   repos once you've connected your GitHub account.
2. **Upload these files to that repository**, keeping them at the *root*
   of the repo (not inside a subfolder):
   - `app.py`
   - `singlife_travel_claim.py`
   - `requirements.txt`
   - `packages.txt`
   - `.streamlit/config.toml` (keep the `.streamlit` folder — GitHub's
     "Add file → Upload files" page preserves folder structure if you drag
     the whole folder in; otherwise create the file manually at that path)

   Easiest way if you're not familiar with git: on your new repo's GitHub
   page, click **Add file → Upload files**, then drag in this whole
   `streamlit_app` folder's contents.
3. Go to **[share.streamlit.io](https://share.streamlit.io)**, sign in,
   click **New app**, pick the repository you just created, and set:
   - **Main file path:** `app.py`
   - Leave everything else as default.
4. Click **Deploy**. The first deploy takes a few minutes — it's
   installing Python packages and the apt-level dependencies Chromium
   needs (from `packages.txt`).
5. Once it's up, you'll get a URL like
   `https://your-app-name.streamlit.app` — that's the link to share with
   your team. Bookmark it.

That's it — no server to manage, no ongoing cost on the free tier.

## Using it

1. Open the app's URL.
2. Pick a scenario: Medical Expense, Flight Delay, or Baggage Loss/Damage.
3. (Optional) Open **Advanced options** to override the claim amount(s),
   add a policy-number suffix, or fill-and-stop instead of submitting.
4. Click **Run test claim** and watch the live log. It typically takes
   1–3 minutes.
5. When it finishes, you'll see either a green "submitted successfully"
   confirmation with the policy number used, or — if something on the
   portal didn't behave as expected — a screenshot of exactly where it
   stopped, plus a "Technical details" section you can copy and send back
   for debugging.

## Things worth knowing

- **One run at a time.** If someone else is mid-run when you click Run,
  you'll get a "please wait" message instead of two browsers launching at
  once — the free hosting tier only has ~1 GB of memory, which is enough
  for one headless Chromium session comfortably but not two.
- **First run after being idle can be slow.** Streamlit Community Cloud
  puts inactive free apps to sleep; waking one up (and, if needed,
  re-downloading the Chromium browser into that fresh container) can add
  30–60 seconds before your first run of the day starts. Later runs in
  the same session are normal speed.
- **A run can take a couple of minutes and there's no hard cutoff on
  free Streamlit hosting** the way there is on serverless platforms like
  Vercel — that mismatch (Vercel's functions typically time out at
  10–60 seconds, well under what a full multi-step form fill needs) is
  exactly why this is built on Streamlit instead.
- **Policy numbers and insured names are randomised on every run** (see
  the main `README.md` for the CLI script) so repeat test runs are easy
  to tell apart in the UAT system — both are shown in the log and in the
  final result.
- If Merimen changes the portal's DOM/fields, this will need the same
  kind of selector updates as the CLI script — it's the same underlying
  automation code (`singlife_travel_claim.py`), just triggered from a web
  form instead of flags.

## Updating it later

Push a new commit to the same GitHub repo (e.g. replace `app.py` or
`singlife_travel_claim.py` with an updated version) — Streamlit Community
Cloud auto-redeploys on every push to the connected branch.
