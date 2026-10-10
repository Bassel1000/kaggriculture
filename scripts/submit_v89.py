"""Submit v89 to the Kaggriculture competition."""
import os

token_path = os.path.expanduser("~/.kaggle/access_token")
if os.path.exists(token_path):
    os.environ["KAGGLE_API_TOKEN"] = open(token_path).read().strip()

from kaggle.api.kaggle_api_extended import KaggleApi  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAR = os.path.join(ROOT, "build", "submission_v89.tar.gz")

MSG = ("v89: keep v88's verified step normalization (seat-1 bleed fix), "
       "pasture ramp OFF (live: 27-30 wasted builds/game, stranded animals "
       "persisted, pre-ship ablation -$55k), space gate reverted to v87 "
       "loose (tight gate blocked expansion buys on deficit boards). "
       "Mirror-safe, dormant vs v87 locally, panel 8-0 c95/spar.")

api = KaggleApi()
api.authenticate()
res = api.competition_submit(TAR, MSG, "kaggriculture")
print("SUBMIT RESULT:", res)
