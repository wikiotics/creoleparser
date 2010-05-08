import genshi.builder as bldr
import dialects, core
import os

class Page(object):
    root = 'test_pages'
    def __init__(self,page_name):
        self.name = page_name

    def get_raw_body(self):
        f = open(os.path.join(self.root,self.name + '.txt'),'r')
        s = f.read()
        f.close()
        return s

    def exists(self):
        try:
            f = open(os.path.join(self.root,self.name + '.txt'),'r')
            f.close()
            return True
        except IOError:
            return False
        
        

def class_func(page_name):
    if not Page(page_name).exists():
        return 'nonexistent'

def path_func(page_name):
    if page_name == 'Home':
        return 'FrontPage'
    else:
        return page_name
    
def macro_func(name,arg_string,body,isblock):
    if name=='include':
        return include(arg_string)
    elif name=='include-source':
        return include_source(arg_string)
    elif name=='source':
        return source(body)
    elif name=='pre':
        return pre(body)
    elif name=='include-raw':
        return include_raw(arg_string)
    else:
        return '**' + arg_string + '**'

def include(page_name):
    page = Page(page_name.strip())
    return text2html.generate(page.get_raw_body())

def include_raw(page_name):
    page = Page(page_name.strip())
    return bldr.tag.pre(page.get_raw_body(),class_='plain')

def include_source(page_name):
    page = Page(page_name.strip())
    return bldr.tag.pre(text2html.render(page.get_raw_body()))

def source(string):
    if string is None:
        return 'None'
    return bldr.tag.pre(text2html.render(string))

def pre(string):
    return bldr.tag.pre(string)
    
dialect = dialects.Creole10(
    wiki_links_base_url='http://creoleparser.srcom.org/cgi-bin/creolepiki/',
    wiki_links_space_char='',
    use_additions=True,
    no_wiki_monospace=False,
    wiki_links_class_func=class_func,
    wiki_links_path_func=path_func,
    macro_func=macro_func)

text2html = core.Parser(dialect)


if __name__ == '__main__':
    
    text = Page('CheatSheetPlus').get_raw_body()
    f = open(os.path.join('test_pages','CheatSheetPlus.html'),'r')
    rendered = f.read()
    f.close()
    f = open(os.path.join('test_pages','template.html'),'r')
    template = f.read()
    f.close()
    
    assert template % text2html(text) == rendered

    

