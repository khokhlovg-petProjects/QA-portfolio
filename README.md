# QA automation portfolio

A test suite built the way I build them at work: three layers that fail for
different reasons, each able to run on its own, with reports that can be read
without reproducing the failure locally.

| Layer | What it covers | Target |
| --- | --- | --- |
| `tests/unit` | the assertion helpers the suite itself relies on | no I/O |
| `tests/api` | authentication, pagination, search, schema contracts | [dummyjson.com](https://dummyjson.com) |
| `tests/ui` | sign-in, catalogue, cart, checkout | [saucedemo.com](https://www.saucedemo.com) |

Stack: Python 3.12, pytest, Playwright, requests, pydantic, Allure, GitHub Actions.

## Running it

```bash
python -m venv .venv && . .venv/Scripts/activate   # Linux/macOS: . .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

pytest                 # everything
pytest -m unit         # instant, no network
pytest -m api
pytest -m ui
pytest -m smoke        # the minimum that has to pass first
pytest -n auto         # parallel
```

No `.env` is needed: every setting falls back to a default in `settings.py`, and
both target hosts publish the credentials this suite uses. Copy `.env.example`
to `.env` to point the suite somewhere else.

Allure results are written to `allure-results` on every run:

```bash
allure serve allure-results
```

## How it is put together

```
pages/      page objects, one class per screen, locators built in __init__
api/        HTTP client (client.py) and response schemas (models.py)
utils/      the domain assertions: fuzzy transcript matching, tone matching
tests/      unit / api / ui, mirroring the layers above
conftest.py session-wide configuration, auth reuse, failure evidence
settings.py one place for every URL, credential and timeout
```

A few decisions worth explaining, since they are the ones I would be asked
about:

**Web-first assertions, no sleeps.** UI checks go through Playwright's
`expect`, which retries until the condition holds or the budget runs out. The
budget is set once in `conftest.py` rather than per test, so there is no
`time.sleep` anywhere and no per-test timeout bikeshedding.

**Logging in once per session.** `storage_state` signs in a single time and
saves the session to disk; every other UI test starts from a context that
restores it. Authentication has its own tests, so paying for it before each of
the others only buys wall-clock time.

**Evidence is collected by a hook, not by the tests.** A failing assertion never
reaches cleanup code, and a screenshot taken after the context closes is empty,
so `pytest_runtest_makereport` grabs the screenshot, the URL and the DOM at the
moment of failure and attaches all three to the report. The API client attaches
each request and response as it happens, for the same reason.

**Models are projections, not one big schema.** `GET /products/{id}` and
`PUT /products/{id}` return different field sets, so `Product` holds the
intersection and `CatalogueProduct` extends it with what only the read
endpoints return. One permissive model covering both would have to make real
fields optional and would stop catching their absence.

**Unknown response fields are allowed, missing ones are not.** Failing because
the API added a field is noise; failing because a field the suite depends on
disappeared or changed type is the entire point.

**Page objects hand back page objects.** `cart.checkout()` returns a
`CheckoutInformationPage`, so a test that navigates wrongly breaks at the type
level rather than by timing out against a locator that was never going to
resolve. Where an action can legitimately fail, there are two methods:
`login` promises the catalogue, `submit_credentials` promises nothing.

## The `utils` layer

`utils/asr.py` and `utils/tones.py` are the parts closest to what I do for a
living, which is testing a VoIP and media platform.

Speech recognition never returns the same string twice for the same audio, so
comparing transcripts with `==` produces tests that fail for reasons unrelated
to the feature. `utils/asr.py` normalises both sides and compares them with a
configurable similarity threshold, and reports the score and both normalised
forms on failure instead of "strings differ".

Tone detection is approximate in the same way: an FFT bin lands a few hertz off
the nominal frequency, so `utils/tones.py` matches within a tolerance and never
by equality. `identify_tone` requires both frequencies of a call-progress pair,
because a lone 480 Hz is ambiguous between ringback and busy and guessing
between them would turn a detection bug into a passing test.

These are also the most densely tested part of the repository, since a bug in
an assertion helper either hides regressions or invents them.

## CI

`.github/workflows/tests.yml` runs the unit layer first as a fast gate, then
API and UI in parallel. UI runs across Chromium and Firefox with `fail-fast`
off, in parallel via `pytest-xdist`, with traces and video retained on failure.
Allure results and Playwright artifacts are uploaded for every job.

## Notes on the fixture hosts

DummyJSON simulates writes rather than persisting them, so the mutation tests
assert on the response contract and not on reading the record back; asserting
persistence would be testing the fixture host. The write tests say so where it
matters.

If the Playwright CDN is unreachable and the browser download fails, the suite
also runs against a locally installed browser:

```bash
pytest -m ui --browser-channel msedge
```
