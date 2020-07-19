#!/usr/bin/python3

# This program converts the WWARA repeater database into a kml file for Google Earth.
# Copyright (C) 2020  Cody Nybo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse, os, sys, csv
import xml.etree.ElementTree as ET

def processCSV(csvFilename, folders):
	if (csvFilename == "-"):
		csvFile = sys.stdin.readlines()		# Read from stdin
	else:
		csvFile = open(csvFilename, "r")	# Read from input file
	
	reader = csv.reader(csvFile)
		
	# Skip the header lines
	next(reader, None)
	next(reader, None)
	
	for row in reader:
		# Read the fields from the CSV file
		repeater = {"codes":{}, "modes":{}}
		repeater["call"]         = row[7]										# H  Callsign
		repeater["city"]         = row[5]										# F  City
		repeater["coverageArea"] = row[6]										# G  Coverage area
		repeater["freqOut"]      = float(row[2])								# C  Output frequency
		repeater["freqIn"]       = float(row[3])								# D  Input frequency
		repeater["latitude"]     = float(row[34])								# AI Latitude
		repeater["longitude"]    = float(row[35])								# AJ Longitude
		repeater["sponsor"]      = row[8]										# I  Sponsor
		repeater["url"]          = row[33]										# AH URL
		
		# Repeater Access codes
		repeater["codes"]["ctcss"]    = row[9]									# J  CTCSS In
		repeater["codes"]["ctcssOut"] = row[10]									# K  CTCSS Out
		repeater["codes"]["dcs"]      = row[11]									# J  DCS
		repeater["codes"]["dmrCC"]    = row[19]									# T  DMR Color Code
		repeater["codes"]["ysfDSC"]   = row[21]									# V  YSF digital squelch code
		repeater["codes"]["p25NAC"]   = row[24]									# Y  P25 NAC
		repeater["codes"]["nxdnRAN"]  = row[27]									# AB NXDN NAC
		
		# Repeater Modes
		repeater["modes"]["WFM"]      = True if row[14] == 'Y' else False		# O  Wide FM
		repeater["modes"]["NFM"]      = True if row[15] == 'Y' else False		# P  Narrow FM
		repeater["modes"]["DSTAR_DV"] = True if row[16] == 'Y' else False		# Q  D-Star Digital Voice
		repeater["modes"]["DSTAR_DD"] = True if row[17] == 'Y' else False		# R  D-Star Digital Data
		repeater["modes"]["DMR"]      = True if row[18] == 'Y' else False		# S  DMR
		repeater["modes"]["YSF"]      = True if row[20] == 'Y' else False		# U  Yaesu System Fusion
		repeater["modes"]["P25"]      = True if row[22] == 'Y' else False		# W  P25 Phase 1
		repeater["modes"]["P25_P2"]   = True if row[23] == 'Y' else False		# X  P25 Phase 2
		repeater["modes"]["NXDN"]     = True if row[25] == 'Y' else False		# Z  NXDN Digital
		repeater["modes"]["NXDN_MIX"] = True if row[26] == 'Y' else False		# AA NXDN Mixed
		repeater["modes"]["ATV"]      = True if row[28] == 'Y' else False		# AC Amateur TV
		repeater["modes"]["DATV"]     = True if row[29] == 'Y' else False		# AD Digital Amateur TV
		
		
		# Make a string with all of the supported modes
		getModes(repeater)
		
		# Make a string with all the codes
		getCodes(repeater)
		
		# Get the offset type and band
		getOffset(repeater)
		
		# Add the repeater to the kml document
		addRepeater(repeater, folders)
	
	# Close file if not reading from stdin
	if (csvFilename != "-"):	
		csvFile.close()

def getModes(repeater):
	repeater["modeString"] = ""
	
	# Make a string with all of the supported modes
	nModes = 0
	if (repeater["modes"]["WFM"]):
		repeater["modeString"] = "WFM"
		nModes+=1
	
	if (repeater["modes"]["NFM"]):
		repeater["modeString"] += " / NFM" if nModes else "NFM"
		nModes+=1
		
	if (repeater["modes"]["DSTAR_DV"]):
		repeater["modeString"] += " / D-Star" if nModes else "D-Star"
		nModes+=1
		
	if (repeater["modes"]["DSTAR_DD"]):
		repeater["modeString"] += " / D-Star DD" if nModes else "D-Star Digital Data"
		nModes+=1
		
	if (repeater["modes"]["DMR"]):
		repeater["modeString"] += " / DMR" if nModes else "DMR"
		nModes+=1
		
	if (repeater["modes"]["YSF"]):
		repeater["modeString"] += " / YSF" if nModes else "YSF"
		nModes+=1
		
	if (repeater["modes"]["P25"]):
		repeater["modeString"] += " / P25" if nModes else "P25"
		nModes+=1
		
	if (repeater["modes"]["P25_P2"]):
		repeater["modeString"] += " / P25 Phase 2" if nModes else "P25 Phase 2"
		nModes+=1
		
	if (repeater["modes"]["NXDN"]):
		repeater["modeString"] += " / NXDN" if nModes else "NXDN"
		nModes+=1
		
	if (repeater["modes"]["ATV"]):
		repeater["modeString"] += " / Analog TV" if nModes else "Analog TV"
		nModes+=1
		
	if (repeater["modes"]["DATV"]):
		repeater["modeString"] += " / Digital TV" if nModes else "Digital TV"
		nModes+=1

def getCodes(repeater):
	# Make a string with all the codes
	nCodes = 0
	ctcssTx = repeater["codes"]["ctcss"]
	ctcssRx = repeater["codes"]["ctcssOut"]
	dcs     = repeater["codes"]["dcs"]
	cc      = repeater["codes"]["dmrCC"]
	dsc     = repeater["codes"]["ysfDSC"]
	nac     = repeater["codes"]["p25NAC"]
	ran     = repeater["codes"]["nxdnRAN"]
	
	repeater["code"] = ""
	
	if (ctcssTx != ''):
		repeater["code"] = ctcssTx
		nCodes += 1
		
	if (ctcssRx != ''):
		repeater["code"] += "/" + ctcssRx if nCodes else ctcssRx
		nCodes += 1
	
	if (dcs != ''):
		repeater["code"] += " / DCS: " + dcs if nCodes else "DCS: " + dcs
		nCodes += 1
		
	if (cc != ''):
		repeater["code"] += " / " + cc if nCodes else cc
		nCodes += 1
		
	if (dsc != ''):
		repeater["code"] += " / DSC: " + dsc if nCodes else "DSC: " + dsc
		nCodes += 1
		
	if (nac != ''):
		repeater["code"] += " / NAC: " + nac if nCodes else "NAC: " + nac
		nCodes += 1
		
	if (ran != ''):
		repeater["code"] += " / RAN: " + ran if nCodes else "RAN: " + ran

def getOffset(repeater):
	#  Get the repeater offset in KHz
	repeater["offset"] = int(repeater["freqIn"]*1000)-int(repeater["freqOut"]*1000)	
	
	# Get the offset type and band
	
	# 10 Meter
	if (repeater["freqOut"] >= 28.0 and repeater["freqOut"] <= 29.7):
		repeater["band"] = 0
		if (repeater["offset"] == -100):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 100):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
	
	# 6 Meter	
	elif (repeater["freqOut"] >= 50.0 and repeater["freqOut"] <= 54.0):
		repeater["band"] = 1
		if (repeater["offset"] == -1700):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 1700):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
	
	# 2 Meter	
	elif (repeater["freqOut"] >= 144.0 and repeater["freqOut"] <= 148.0):
		repeater["band"] = 2
		if (repeater["offset"] == -600):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 600):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
	
	# 1.25 Meter
	elif (repeater["freqOut"] >= 222.0 and repeater["freqOut"] <= 225.0):
		repeater["band"] = 3
		if (repeater["offset"] == -1600):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 1600):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
	
	# 70 CM
	elif (repeater["freqOut"] >= 420.0 and repeater["freqOut"] <= 450.0):
		repeater["band"] = 4
		if (repeater["offset"] == -5000):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 5000):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
	
	# 33 CM	
	elif (repeater["freqOut"] >= 902.0 and repeater["freqOut"] <= 928.0):
		repeater["band"] = 5
		if (repeater["offset"] == -25000):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 25000):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
	
	# 23 CM
	elif (repeater["freqOut"] >= 1240.0 and repeater["freqOut"] <= 1300.0):
		repeater["band"] = 6
		if (repeater["offset"] == -20000):
			repeater["ofsType"] = "-"
		elif (repeater["offset"] == 20000):
			repeater["ofsType"] = "+"
		elif (repeater["offset"] == 0):
			repeater["ofsType"] = ""
		else:
			repeater["ofsType"] = " Odd"
			
def createKML(doc, folders):
	bands = ["10M Repeaters", "6M Repeaters", "2M Repeaters", "1.25M Repeaters", "70CM Repeaters", "33CM Repeaters", "23CM Repeaters"]
	
	# Create the style section
	style      = ET.SubElement(doc,        "Style", id="IDLE")
	
	iconStyle  = ET.SubElement(style,      "IconStyle")
	scale      = ET.SubElement(iconStyle,  "IconStyle").text = "0.6"
	icon       = ET.SubElement(iconStyle,  "Icon")
	href       = ET.SubElement(icon,       "href").text = "https://www.repeaterbook.com/images/ham/gmapicon.png"
	
	labelStyle = ET.SubElement(style,      "LabelStyle")
	color      = ET.SubElement(labelStyle, "color").text = "ff00ff00"
	scale      = ET.SubElement(labelStyle, "scale").text = "0.7"
	name       = ET.SubElement(doc,        "name").text = "WWARA Repeaters"
	desc       = ET.SubElement(doc,        "description").text = \
	"Western Washington Repeaters.<br>Created with <a href='https://github.com/cmnybo/rptrlist2kml'>rptrlist2kml</a> using the <a href='https://www.wwara.org/'>WWARA</a> database"
	
	# Create folders for each band
	folders.append(ET.SubElement(doc,      "Folder"))
	folders.append(ET.SubElement(doc,      "Folder"))
	folders.append(ET.SubElement(doc,      "Folder"))
	folders.append(ET.SubElement(doc,      "Folder"))
	folders.append(ET.SubElement(doc,      "Folder"))
	folders.append(ET.SubElement(doc,      "Folder"))
	folders.append(ET.SubElement(doc,      "Folder"))
	
	# Set the folder names
	for i in range(0, 7):
		ET.SubElement(folders[i], "name").text = bands[i]

def addRepeater(r, f):
	# Create the description string
	description  = "<b>{:4.4f}{:1s} {:s}</b><br>".format(r["freqOut"], r["ofsType"], r["code"])
	description += "{:s} - {:s}<br>".format(r["city"].title(), r["coverageArea"].title())
	description += "Modes: {:s}<br>".format(r["modeString"])
	description += "Offset: {:4.2f} MHz<br>".format(float(r["offset"])/1000.0)
	if (r["url"] != ""):
		description += "Sponsor: <a href={:s}>{:s}</a>".format(r["url"], r["sponsor"])
	else:
		description += "Sponsor: {:s}".format(r["sponsor"])
	
	# Create a new placemark for the repeater
	pm    = ET.SubElement(f[r["band"]], "Placemark")
	name  = ET.SubElement(pm,    "name").text = r["call"]
	style = ET.SubElement(pm,    "styleUrl").text = "IDLE"
	desc  = ET.SubElement(pm,    "description").text = description
	point = ET.SubElement(pm,    "Point")
	coord = ET.SubElement(point, "coordinates").text = "{:f}, {:f}, 0".format(r["longitude"], r["latitude"])


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''\
This program converts the WWARA repeater list to a Google Earth KML file.
The current list can be downloaded from www.wwara.org/DataBaseExtract.zip

If the input file is "-", the input CSV will be read from STDIN.
If no output file is given, the output KML will be written to STDOUT.\
''', epilog='''
Example usage:
rptrlist2kml.py -i WWARA-rptrlist.csv Repeaters.kml''')

parser.add_argument("-i", metavar="Input", required=True, dest="infile", help="CSV Input File")
parser.add_argument("outfile", metavar="Output", nargs="?", help="KML Output File")
args = parser.parse_args()


folders = []																	# Array to hold the folder elements for each band
kml     = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")				# Create the root kml element
kmlDoc  = ET.SubElement(kml, "Document")										# Create the document element
tree    = ET.ElementTree(kml)													# Create the element tree

createKML(kmlDoc, folders)														# Create the empty kml document
processCSV(args.infile, folders)												# Process the CSV file and add the repeaters to the kml document

# Write the kml to the output file if set or stdout if no file is given
if (args.outfile is None):
	sys.stdout.write(ET.tostring(kml, encoding="unicode") + "\n")				# Write to stdout
else:
	tree.write(args.outfile)													# Write the tree to the output file

