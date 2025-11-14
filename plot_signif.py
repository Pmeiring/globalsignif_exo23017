#!/usr/bin/env python3
import os
import numpy as np
import ROOT

input_file= "max_significance_per_toy.npy"
plot_path = "./signif_tmp.png"
max_local = 4.01 # maximum observed local significance

if __name__ == '__main__':

    # Check input file and prepare output folder
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found. Run compute_max_significance.py first.")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    # Load entries
    sig = np.load(input_file)
    sig = sig[np.isfinite(sig)]  # remove NaNs or infs
    n_entries = len(sig)
    n_high = np.sum(sig > max_local)

    print(f"Loaded {n_entries} toy entries.")
    print(f"Mean significance: {np.mean(sig):.3f}")
    print(f"Median significance: {np.median(sig):.3f}")
    print(f"Max significance: {np.max(sig):.3f}")
    print(f"Number of entries > {max_local}: {n_high}")

    # Fill histogram
    n_bins = 60
    sig_max = 20# np.max(sig)
    hist = ROOT.TH1F("hist", "Distribution of Max Significance per Toy", n_bins, 0, sig_max)
    for s in sig:
        hist.Fill(s)

    # Set style
    ROOT.gStyle.SetOptStat(0)
    hist.SetLineColor(ROOT.kBlue+1)
    hist.SetLineWidth(2)
    hist.GetXaxis().SetTitle("Max significance across all mass points")
    hist.GetYaxis().SetTitle("Toy count (log scale)")
    hist.SetTitle("")

    # Create canvas
    c = ROOT.TCanvas("c", "Max Significance", 800, 800)
    c.SetLogy()

    # Draw histogram
    hist.Draw("HIST")
    hist.Draw("SAME")  # ensure line style applied

    # Add text annotation
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextAlign(31+13)  # right-top
    text.SetTextFont(42)
    text.SetTextSize(0.04)
    text.DrawLatex(0.2, 0.93, f"Total entries: {n_entries:,}")

    # Save plot
    c.SaveAs(plot_path)
    print(f"✅ Plot saved to {plot_path}")
