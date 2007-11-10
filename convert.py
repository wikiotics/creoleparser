from creoleparser import creole_to_xhtml
intext = file('instructions.txt','r').read()
outtext = creole_to_xhtml(intext)
file('temp.html','w+').write(outtext)