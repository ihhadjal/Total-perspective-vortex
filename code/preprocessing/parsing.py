import mne
import argparse
import matplotlib.pyplot as plt
import numpy as np
parser = argparse.ArgumentParser()

parser.add_argument("subject", type=int, help="Subject number")
parser.add_argument("run", type=int, help="Run number")
parser.add_argument("--raw", action="store_true",help="shows the raw signal")
parser.add_argument("--psd", action="store_true", help="visualizes the frequency content of continuos data")
parser.add_argument("--filter", action="store_true", help="filters the raw EEG")
parser.add_argument("--epochs", action="store_true", help="creates epochs")

args = parser.parse_args()

def load_data(subject, run):
    file_path = mne.datasets.eegbci.load_data(subject, run)[0]

    raw = mne.io.read_raw_edf(file_path, preload=True)

    return raw

raw = load_data(args.subject, args.run)

if args.raw is True and args.filter is False:
    raw.plot(block=True)

if args.psd is True and args.filter is False:
    spectrum = raw.compute_psd()
    spectrum.plot(average=True, picks="data", exclude="bads", amplitude=False)

    plt.show(block=True)




if args.filter:
    raw_filter = raw.copy()
    raw_filter.filter(8.0, 30.0)

    if args.raw:
        if args.psd is True or args.raw is True:
            raw_filter.plot(block=False)
        else:
            raw_filter.plot(block=True)
    if args.psd:
        copy_spectrum = raw_filter.compute_psd()
        copy_spectrum.plot(average=True, picks="data", exclude="bads", amplitude=False)
        plt.show(block=True)

    events, event_id = mne.events_from_annotations(raw_filter)


    event_dict = {
        "left": 2,
        "right": 3,
    }

    epochs = mne.Epochs(raw_filter, events, event_id=event_dict, tmin=0.0, tmax=4.0, baseline=None, preload=True)

    if args.epochs:
        epochs.plot(events=True, block=True)