# cs_web_scanner
Accessibility scanner for Technion cs sites



--- Instructions ---

1. before first run, execute from inside tool dir:
	./install
2. to execute the tool, Run:
	python src/main/Interface.py

see help for details.
3. to clean:
	./install clean


--- file structure ---

data:
data/mapper: mapper files output - list of sites and pages.
data/reports: the last DB produced by the accessbility checker.

logs:
 log.out and log.err files of the last run



--- environment ---

- python3

- for installing bs package on linux for python3:
    sudo pip install python3-beautifulsoup

--- Modules ---

WebScanner:

Main Operation:
* the tool scanning over all cs faculty pages, starting with cs.technion.ac.il.
	a page is cs faculty page if one of the following holds:
 * the url contains 'cs.technion' 
	for every site home address it creates new dir and insert reports of bad pages of this site
	a definition for site home address is either of the following:
 * http://cs.technion.ac.il/~<basic_string>
 * http://<basic_string>.cs.technion.ac.il


WebInspector:

*  takes the output file of the mapper (mapper_pages.txt), and copy
	it to private location, so mapper can work in paralell
* scan the file and produce report for every page in the list
* organize all report in DB that sits in data/inspector

