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
Rules for joining link with a sub link:
 * look for href
 for base URLs (no ~ sign):
 * if the sublink is: /<something> then it comes right after the base URL 
 * if the sublink is   <something> then it come at the end of curr URL
 * if the sublink is   /../<something> then it come at the end of curr URL
 * if the sublink is   /<something> then it come at the end of curr URL
 for home URLs (~):
 * if the sublink is: /<something> then it comes right after the base URL 
 * if the sublink is   <something> then it come at the end of curr URL
 * if the sublink is   /../<something> then it come at the end of curr URL
 * if the sublink is   /<something> then it come at the end of curr URL

* every ../ remove one dir that ends with /. which means if the last part in the URL doesnt end with '/' we dont count it
* general: if link ends with dir ('/') the page that show is the default 'index.html'


--- Tool's Functionality ---

Run:
python src/main/WebScanner.py

Main Operation:
the tool scanning over all cs faculty pages, starting with cs.technion.ac.il.
a page is cs faculty page if one of the following holds:
 * the url contains 'cs.technion' 
 * the title contains 'Comuter Science'
for every site home address it creates new dir and insert reports of bad pages of this site
a definition for site home address is either of the following:
 * http://cs.technion.ac.il/~<basic_string>
 * http://<basic_string>.cs.technion.ac.il

Debug Info:
 * the log of the last run is kept in logs/run.log
 * the error log is kept in logs/err.log
 * the sites addresses of cs are kept in logs/sites.txt
