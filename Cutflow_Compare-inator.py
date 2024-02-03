from ROOT import *
from string import *
#to code work you have be in the same directory with the histout files.

dict = {
	#histogram to compare with the cutflow(the name written in adl file): name of the histout file (the file you see when you write "ls" in your terminal)
	"onshellWZ" : "ATLAS-SUSY-2019-09-onshell",
}

#regions to do comparison (this is for getting cutflow)
regions = ["SRWZ1","SRWZ2","SRWZ3","SRWZ4","SRWZ5","SRWZ6","SRWZ7","SRWZ8","SRWZ9","SRWZ10","SRWZ11","SRWZ12","SRWZ13","SRWZ14","SRWZ15","SRWZ16","SRWZ17","SRWZ18","SRWZ19","SRWZ20"]


for key in dict:
	f = TFile("histoOut-" + dict[key] + ".root")

	print("\n\n\n\n")
	print("*******Working on " + key)

	for region in regions:
		#histogramları çekiyoğ
		hc = f.Get(region + "/" + "cutflow") #cutflow yani bizim adl'nin sonucu histogram
		hp = f.Get(region + "/" + key) #elle yazılmış deneysel histogram

		if len(hc) - len(hp) != 1:
			print("*****WARNING: LENGTHS ARE NOT MATCHING*****", len(hc), len(hp))	


		# Obtain nbins from the CL output histogram
		# Note that CL histo automatically writes total #evts, so it has one more bin
		nbins = hc.GetXaxis().GetNbins()
		
		print("\n ====== Comparing "+hp.GetTitle()+" region "+ region + " :")
		print("\n *** Cumulative comparison - DF:")
		print("%55s :  %6s  %6s  %6s" % ("Selection", "CL", "Paper", "Error"))
		nctot = hc.GetBinContent(0+1)
		nptot = hp.GetBinContent(1)
		for i in range(1, nbins):
			label = hc.GetXaxis().GetBinLabel(i+1)
			nc = hc.GetBinContent(i+1)/nctot*100
			np = hp.GetBinContent(i)/nptot*100
			diff = 100*(nc - np) / np if np != 0 else 0 if nc == 0 else 99999999999
			print("%55s :  %4.2f  %4.2f  %4.2f" % (label, nc, np, diff))
		
		print("\n *** Relative comparison:")
		print("(In the first line no comparison is done.)")
		print("%55s :  %6s  %6s  %6s" % ("Selection", "CL", "Paper", "Error"))
		for i in range(1, nbins):
			label = hc.GetXaxis().GetBinLabel(i+1)
			if i == 1:
				nc = hc.GetBinContent(i+1) / nctot
				np = hp.GetBinContent(i) / nptot
				diff = 0
			else:
				nc = 100 * hc.GetBinContent(i+1) / hc.GetBinContent(i) if hc.GetBinContent(i) != 0 else 0
				np = 100 * hp.GetBinContent(i) / hp.GetBinContent(i-1) if hp.GetBinContent(i-1) != 0 else 0
				diff = 100*(nc - np) / np if np != 0 else 0 if nc == 0 else 99999999999
			print("%55s :  %4.2f  %4.2f  %4.2f" % (label, nc, np, diff))


		if len(hc) - len(hp) != 1:
			print("*****WARNING: LENGTHS ARE NOT MATCHING*****", len(hc), len(hp))
			
