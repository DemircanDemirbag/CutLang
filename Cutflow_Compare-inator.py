import ROOT
from ROOT import TFile

# To run this code, you must be in the same directory as the histout files.
# Note that depending on your root installation the code may end with a ROOT crash, but this is ok since the code is ended :)

hist_dict = {
	# Histogram to compare with the cutflow (the name written in the ADL file): name of the histout file (the file you see when you write "ls" in your terminal)
	"TChi200160": "histoOut-test.root",
}

# Regions to do comparison (this is for getting cutflow)
regions = ["twolEwkLowMet","twolEwkHighMet"]

# Create a canvas to draw on
canvas = ROOT.TCanvas("canvas", "Overlay of Histograms", 800, 600)

for key in hist_dict:
	f = TFile(hist_dict[key])

	print("\n\n\n\n")
	print("*******Working on " + key)

	for region in regions:
		# Get histograms
		hc = f.Get(region + "/" + "cutflow")  # Cutflow histogram (ADL result)
		hp = f.Get(region + "/" + key)  # Manually written experimental histogram

		if hc.GetNbinsX() - hp.GetNbinsX() != 1:
			print("*****WARNING: LENGTHS ARE NOT MATCHING*****", hc.GetNbinsX(), hp.GetNbinsX())

		# Obtain nbins from the CL output histogram
		nbins = hc.GetXaxis().GetNbins()

		print("\n ====== Comparing " + hp.GetTitle() + " region " + region + " :")
		print("\n *** Cumulative comparison - DF:")
		print("%55s :  %6s  %6s  %6s" % ("Selection", "CL", "Paper", "Error"))
		nctot = hc.GetBinContent(1)
		nptot = hp.GetBinContent(1)
		for i in range(1, nbins):
			label = hc.GetXaxis().GetBinLabel(i + 1)
			nc = hc.GetBinContent(i + 1) / nctot * 100
			np = hp.GetBinContent(i) / nptot * 100
			diff = 100 * (nc - np) / np if np != 0 else 0 if nc == 0 else float('inf')
			print("%55s :  %4.2f  %4.2f  %4.2f" % (label, nc, np, diff))

		print("\n *** Relative comparison:")
		print("(In the first line no comparison is done.)")
		print("%55s :  %6s  %6s  %6s" % ("Selection", "CL", "Paper", "Error"))
		for i in range(1, nbins):
			label = hc.GetXaxis().GetBinLabel(i + 1)
			if i == 1:
				nc = hc.GetBinContent(i + 1) / nctot
				np = hp.GetBinContent(i) / nptot
				diff = 0
			else:
				nc = 100 * hc.GetBinContent(i + 1) / hc.GetBinContent(i) if hc.GetBinContent(i) != 0 else 0
				np = 100 * hp.GetBinContent(i) / hp.GetBinContent(i - 1) if hp.GetBinContent(i - 1) != 0 else 0
				diff = 100 * (nc - np) / np if np != 0 else 0 if nc == 0 else float('inf')
			print("%55s :  %4.2f  %4.2f  %4.2f" % (label, nc, np, diff))

		if hc.GetNbinsX() - hp.GetNbinsX() != 1:
			print("*****WARNING: LENGTHS ARE NOT MATCHING*****", hc.GetNbinsX(), hp.GetNbinsX())




		#We draw cutlang's cutflow, and shade overshoots and undershoots. We do not draw paper's cutflow explicitely. Red marks are error lines of the Cutlang.

		canvas.Clear()
		# Remove the useless offset of the cutflow histogram
		nbins = hc.GetNbinsX()
		xmin = hc.GetXaxis().GetXmin()
		xmax = hc.GetXaxis().GetXmax()
		bin_width = (xmax - xmin) / nbins
		hist1 = ROOT.TH1F("hist1", hc.GetTitle(), nbins - 1, xmin , xmax-1)
		for i in range(1, nbins):
			hist1.SetBinContent(i, hc.GetBinContent(i+1)) 
			hist1.GetXaxis().SetBinLabel(i, hc.GetXaxis().GetBinLabel(i + 1))

		hist2 = hp

		hist1.SetStats(0)
		hist2.SetStats(0)


		# Calculate the scaling factor to normalize the first bin of hist2 to hist1
		first_bin_hist1 = hist1.GetBinContent(1)
		first_bin_hist2 = hist2.GetBinContent(1)

		if first_bin_hist2 != 0:
			scale_factor = first_bin_hist1 / first_bin_hist2
		else:
			scale_factor = 1  # Avoid division by zero

		# Scale the second histogram
		hist2.Scale(scale_factor)

		
		# Draw the first histogram
		hist1.SetLineColor(ROOT.kBlue)
		hist1.Draw()

		# Draw the second histogram with transparency
		hist2.SetLineColor(ROOT.kRed)
		hist2.SetFillColorAlpha(ROOT.kRed, 0.5)
		hist2.Draw("SAME")

		# Create histograms for the overlap and non-overlapping regions
		hist_overlap = hist1.Clone("overlap")
		hist_overlap.SetFillColor(ROOT.kGreen)
		hist_overlap.SetFillStyle(3001)

		hist_nonoverlap_high = hist1.Clone("nonoverlap_high")
		hist_nonoverlap_high.SetFillColor(ROOT.kRed)
		hist_nonoverlap_high.SetFillStyle(3004)

		hist_nonoverlap_low = hist1.Clone("nonoverlap_low")
		hist_nonoverlap_low.SetFillColor(ROOT.kBlue)
		hist_nonoverlap_low.SetFillStyle(3005)

		# Calculate the content for the overlap and non-overlapping regions
		for i in range(1, hist_overlap.GetNbinsX()):
			bin_content_1 = hist1.GetBinContent(i)
			bin_content_2 = hist2.GetBinContent(i)

			overlap_content = min(bin_content_1, bin_content_2)
			hist_overlap.SetBinContent(i, overlap_content)

			if bin_content_1 > bin_content_2:
				hist_nonoverlap_high.SetBinContent(i, bin_content_1)
				hist_nonoverlap_low.SetBinContent(i, 0)
			else:
				hist_nonoverlap_high.SetBinContent(i, 0)
				hist_nonoverlap_low.SetBinContent(i, bin_content_2)

		# Draw the non-overlapping regions
		hist_nonoverlap_high.Draw("SAME")
		hist_nonoverlap_low.Draw("SAME")

		# Draw the overlap
		hist_overlap.Draw("SAME")

		# Add legend with custom entries
		legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
		legend.AddEntry(hist_overlap, "Overlap (Green)", "f")
		legend.AddEntry(hist_nonoverlap_high, "Red: CutLang Overshoots", "f")
		legend.AddEntry(hist_nonoverlap_low, "Blue: CutLang Undershoots", "f")
		legend.Draw()

		# Update and save the canvas
		canvas.Update()
		canvas.SaveAs(key + "_" + region + ".png")

	# Close the ROOT file
	f.Close()
