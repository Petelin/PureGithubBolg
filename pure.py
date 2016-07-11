import os
import re
import shutil
import urllib.request
from os.path import join

from jinja2 import PackageLoader, Environment
import markdown2



class Post(object):
    def __init__(self, fullpath):
        if not os.path.isfile(fullpath): raise RuntimeError("not a file")
        self.fullpath = fullpath
        self.filename_with_suffix = os.path.basename(fullpath)
        self.filename = self.filename_with_suffix.split('.')[0]
        self.relativepath = os.path.dirname(fullpath).lstrip(join(basedir, "post"))
        self.dest_file = join(website_dir, self.relativepath, self.filename + ".html")
        self.url = urllib.request.pathname2url(self.dest_file.split(website_dir)[1])
        self.title = self.filename

    def change_to_html(self):
        html = markdown2.markdown( open(self.fullpath).read(), extras=['fenced-code-blocks'])
        # print(html)
        return html

    def write_html(self, html,title):
        if not os.path.exists(os.path.dirname(self.dest_file)):
            os.makedirs(os.path.dirname(self.dest_file))
        with open(self.dest_file, "w",
                  encoding="utf-8",
                  errors="xmlcharrefreplace") as fd:
            html = jinja_env.get_template("post.html").render(title=title,content=html)
            # print(html)
            fd.write(html)


def cover_all_post():
    """create posts html format and make up index.html"""
    post_basedir = join(basedir, "post")

    for root, dirs, files in os.walk(post_basedir):
        postlist = []
        for f_name in files:
            post_path = join(root, f_name)
            p = Post(post_path)
            html = p.change_to_html()
            # 文档标题
            title = re.findall("<h2>(.*?)</h2>", html)
            if title:
                p.title = title[0]
            p.write_html(html,title)
            postlist.append(p)
        index_t = jinja_env.get_template("index.html")
        with open(join(website_dir, "index.html"), "w") as fd:
            fd.write(index_t.render(postlist=postlist))


def copy_all_static():
    """copy static/* to website"""
    base_websit = join(basedir, "static")
    for root, dirs, files in os.walk(base_websit):
        relative_path = root.split(base_websit)[1].strip("/")
        for filename in files:
            if not os.path.exists(join(website_dir, relative_path)):
                os.makedirs(join(website_dir, relative_path))
            shutil.copy(join(root, filename),
                        join(website_dir, relative_path, filename))


def push_to_github():
    os.system("""cd %s && git add * && git commit -m "update" && git push origin master""" % website_dir)


def develop():
    copy_all_static()
    cover_all_post()
    push_to_github()


basedir = os.path.dirname(__file__)
jinja_env = Environment(loader=PackageLoader(__name__))
website_dir = "/Users/zhangxiaolin/Documents/github/Petelin.github.io"
jinja_env.globals["title"] = "简简单单"
jinja_env.globals["icon"] = "Yc.jgp"
jinja_env.globals["sociallist"] = (("github", "https://github.com/Petelin"),)

if __name__ == "__main__":
    develop()
