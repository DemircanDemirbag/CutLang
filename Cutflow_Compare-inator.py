from ROOT import *
from string import *
#to code work you have be in the same directory with the histout files.

dict = { #(this is for getting the model we provide)
	#histogram to compare with the cutflow (the name you give under the countsformat "process SRWZ5, ..."): name of the histout file(the name you see when you press ls) 
	"SRWZ5" : "test2",
	"bbX-200-500" : "bbX-si200-500" 
}

#regions to do comparison (this is for getting cutflow)
regions = ["SRWZ5", "Resolved-200-350-2b"]


for key in dict:
	f = TFile("histoOut-" + dict[key] + ".root")

	print("\n\n\n\n")
	print("*******Working on " + key)

	for region in regions:
		#histogramları çekiyoğ
		hc = f.Get(region + "/" + "cutflow") #cutflow the result of our adl file
		hp = f.Get(region + "/" + key) #the histogram write by hand, related to the paper

		if len(hc) - len(hp) != 1:
			print("*****WARNING: LENGTHS ARE NOT MATCHING*****", len(hc), len(hp))


		# Obtain nbins from the CL output histogram
		# Note that CL histo automatically writes total #evts, so it has one more bin
		nbins = hc.GetXaxis().GetNbins()
		
		print("\n ====== Comparing "+hp.GetTitle()+" :")
		print("\n *** Cumulative comparison - DF:")
		print("%55s :  %6s  %6s  %6s" % ("Selection", "CL", "Paper", "Error"))
		nctot = hc.GetBinContent(0+1)
		nptot = hp.GetBinContent(1)
		for i in range(1, nbins):
			label = hc.GetXaxis().GetBinLabel(i+1)
			nc = hc.GetBinContent(i+1)/nctot*100
			np = hp.GetBinContent(i)/nptot*100
			diff = 100*(nc - np) / np
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
				diff = 100*(nc - np) / np
			print("%55s :  %4.2f  %4.2f  %4.2f" % (label, nc, np, diff))


		if len(hc) - len(hp) != 1:
			print("*****WARNING: LENGTHS ARE NOT MATCHING*****", len(hc), len(hp))
			
