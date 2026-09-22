import mne
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("subject", type=int, help="Subject number")
parser.add_argument("run", type=int, help="Run number")
parser.add_argument("--raw", action="store_true",help="shows the raw signal")

args = parser.parse_args()

def load_data(subject, run):
    file_path = mne.datasets.eegbci.load_data(subject, run)[0]

    raw = mne.io.read_raw_edf(file_path, preload=True)

    return raw

raw = load_data(args.subject, args.run)
annotations = raw.annotations

if args.raw:
    raw.plot(block=True)