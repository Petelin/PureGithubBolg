import os
import re
import shutil
from os.path import join, dirname, basename as filename, splitext
from urllib.request import pathname2url

import markdown2
from jinja2 import PackageLoader, Environment


class Post(object):
    def __init__(self, from_file):
        if not os.path.isfile(from_file): raise RuntimeError("not a file")
        self.fromfile = from_file
        self.destfile = join(dirname(self.fromfile.replace(root_dir, website_dir)),
                             splitext(filename(self.fromfile))[0] + ".html")
        self.url = pathname2url(self.destfile.split(website_dir)[1])
        self._html = None
        self._title = None

    @property
    def html(self):
        if not self._html:
            self._html = markdown2.markdown(open(self.fromfile).read(),
                                            extras=['fenced-code-blocks', 'footnotes'])
        return self._html

    @property
    def title(self):
        if not self._title:
            title = re.findall("<h2>(.*?)</h2>", self.html)
            self._title = title[0] if title else filename(self.destfile).rsplit(".")[0]
        return self._title

    def write(self):
        if not os.path.exists(dirname(self.destfile)):
            os.makedirs(dirname(self.destfile))
        with open(self.destfile, "w", encoding="utf-8", errors="xmlcharrefreplace") as fd:
            html = jinja_env.get_template("post.html").render(title=self.title, content=self.html)
            # print(html)
            fd.write(html)


def cover_all_post():
    """create posts html format and make up index.html"""
    post_basedir = join(root_dir, "post")
    postlist = []
    for root, dirs, files in os.walk(post_basedir):
        for f_name in files:
            post_path = join(root, f_name)
            p = Post(post_path)
            p.write()
            postlist.append(p)
    index_t = jinja_env.get_template("index.html")
    with open(join(website_dir, "index.html"), "w") as fd:
        fd.write(index_t.render(postlist=postlist))


def copy_all_static():
    """拷贝 static/* 到 设置的website文件夹下"""
    base_websit = join(root_dir, "static")
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
    """部署到github"""
    copy_all_static()
    cover_all_post()
    push_to_github()


root_dir = dirname(__file__)
jinja_env = Environment(loader=PackageLoader(__name__))

# 文件输出地址,确定已经git init,可以直接git push origin master
website_dir = "/Users/zhangxiaolin/Documents/github/Petelin.github.io"

# 博客名字
jinja_env.globals["title"] = "简简单单"

# 博客图标
jinja_env.globals["icon"] = "Yc.jgp"

# 直接添加名字和地址
jinja_env.globals["sociallist"] = (("github", "https://github.com/Petelin"),)

if __name__ == "__main__":
    develop()
