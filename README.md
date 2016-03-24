# cs_web_scanner
Accessibility scanner for Technion cs website


--- file structure ---
tmp:
    sites: addresses of cs sites that can be directed from cs.technion.ac.il


--- environment ---
- python3
- for installing bs package on linux for python3:
    sudo pip install python3-beautifulsoup

--- Modules ---

WebScanner:
- 


--- Tool's Functionality ---
the tool scanning the web tree, starting with cs.technion.ac.il. and stop if:
 * it reached a page outside cs faculty
 * it already visited this page
for every site home address it creates new dir and insert reports of bad pages of this site
a definition for site home address is either of the following:
 * http://cs.technion.ac.il/~<basic_string>
 * http://<basic_string>.cs.technion.ac.il

