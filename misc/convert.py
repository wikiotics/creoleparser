from creoleparser import text2html
intext = file('instructions.txt','r').read()
outtext = text2html(intext)
file('temp.html','w+').write(outtext)