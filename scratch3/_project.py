#----- Getting projects

import json
import requests
from . import _user
from . import _exceptions
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class PartialProject:

    # This class is for unshared projects

    def __init__(self, **entries):

        self.shared = None

        self.__dict__.update(entries)

        if "_session" not in self.__dict__.keys():
            self._session = None
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        self._json_headers = self._headers
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"


    def download(self, *, filename=None, dir=""):
        try:
            if filename is None:
                filename = str(self.id)
            response = requests.get(f"https://projects.scratch.mit.edu/{self.id}")
            filename = filename.replace(".sb3", "")
            open(f"{dir}{filename}.sb3", 'wb').write(response.content)
        except Exception:
            raise(_exceptions.FetchError)

    def get_raw_json(self):
        return requests.get(f"https://projects.scratch.mit.edu/{self.id}/").json()

    def get_creator_agent(self):
        try:
            return requests.get(f"https://projects.scratch.mit.edu/{self.id}/").json()["meta"]["agent"]
        except Exception:
            raise(_exceptions.FetchError)

    def remixes(self, *, limit=None, offset=0):
        if limit is None:
            _projects = json.loads(requests.get(
                f"https://api.scratch.mit.edu/projects/{self.id}/remixes/?offset={offset}",
                headers = {
                    "x-csrftoken": "a",
                    "x-requested-with": "XMLHttpRequest",
                    "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                    "referer": "https://scratch.mit.edu",
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                }
            ).text)
        else:
            _projects = requests.get(
                f"https://api.scratch.mit.edu/projects/{self.id}/remixes/?limit={limit}&offset={offset}",
                headers = {
                    "x-csrftoken": "a",
                    "x-requested-with": "XMLHttpRequest",
                    "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                    "referer": "https://scratch.mit.edu",
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                }
            ).json()
        projects = []
        for project in _projects:
            projects.append(Project(
                author = project["author"]["username"],
                comments_allowed = project["comments_allowed"],
                description=project["description"],
                created = project["history"]["created"],
                last_modified = project["history"]["modified"],
                share_date = project["history"]["shared"],
                id = project["id"],
                thumbnail_url = project["image"],
                instructions = project["instructions"],
                remix_parent = project["remix"]["parent"],
                remix_root = project["remix"]["root"],
                favorites = project["stats"]["favorites"],
                loves = project["stats"]["loves"],
                remixes = project["stats"]["remixes"],
                views = project["stats"]["views"],
                title = project["title"],
                url = "https://scratch.mit.edu/projects/" + str(project["id"]),
                _session = self._session,
            ))
        return projects


class Project(PartialProject):


    def __str__(self):
        return self.title

    def update(self):
        if self._session is not None:
            project = requests.get(
                f"https://api.scratch.mit.edu/projects/{self.id}",
                headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
                    "x-token": self._session.xtoken,
                }
            ).json()
        else:
            project = requests.get(f"https://api.scratch.mit.edu/projects/{self.id}").json()
        if "code" in list(project.keys()):
            return False
        else:
            return self._update_from_dict(project)

    def _update_from_dict(self, project):
        try:
            self.id = int(project["id"])
        except KeyError:
            pass
        self.url = "https://scratch.mit.edu/projects/"+str(self.id)
        self.author = project["author"]["username"]
        self.comments_allowed = project["comments_allowed"]
        self.instructions = project["instructions"]
        self.notes=project["description"]
        self.created = project["history"]["created"]
        self.last_modified = project["history"]["modified"]
        self.share_date = project["history"]["shared"]
        self.thumbnail_url = project["image"]
        try:
            self.remix_parent = project["remix"]["parent"]
            self.remix_root = project["remix"]["root"]
        except Exception:
            self.remix_parent = None
            self.remix_root = None
        self.favorites = project["stats"]["favorites"]
        self.loves = project["stats"]["loves"]
        self.remix_count = project["stats"]["remixes"]
        self.views = project["stats"]["views"]
        self.title = project["title"]
        return True

    def get_author(self):
        try:
            return self._session.connect_user(self.author)
        except AttributeError:
            return _user.get_user(self.author)

    def comments(self, *, limit=40, offset=0):
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/comments/?limit={limit}&offset={offset}"
            ).json()
            if len(response) != 40:
                break
            offset += 40
            comments.append(r)
        return comments

    def get_comment_replies(self, *, comment_id, limit=40, offset=0):
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/comments/{comment_id}/replies?limit={limit}&offset={offset}"
            ).json()
            if len(response) != 40:
                break
            offset += 40
            comments.append(r)
        return comments

    def love(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers=self._headers,
            cookies=self._cookies,
        ).json()
        if r['userLove'] is False:
            self.love()

    def unlove(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()
        if r['userLove'] is True:
            self.love()

    def favorite(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()
        if r['userFavorite'] is False:
            self.love()

    def unfavorite(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()
        if r['userFavorite'] is False:
            self.love()


    def post_view(self):
        requests.post(
            f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/views/",
            headers=headers,
        )

    def turn_off_commenting(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        data = {
            "comments_allowed" : False
        }
        self._update_from_dict(requests.put(
            f"https://api.scratch.mit.edu/projects/{self.id}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(data)
        ).json())

    def turn_on_commenting(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        data = {
            "comments_allowed" : True
        }
        self._update_from_dict(requests.put(
            f"https://api.scratch.mit.edu/projects/{self.id}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(data)
        ).json())



    def toggle_commenting(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        data = {
            "comments_allowed" : not self.comments_allowed
        }
        self._update_from_dict(requests.put(
            f"https://api.scratch.mit.edu/projects/{self.id}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(data)
        ).json())

    def share(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        if self.shared is not True:
            requests.put(f"https://api.scratch.mit.edu/proxy/projects/{self.id}/share/",
                headers = self._json_headers,
                cookies = self._cookies,
            )

    def unshare(self):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        if self.shared is not False:
            requests.put(f"https://api.scratch.mit.edu/proxy/projects/{self.id}/unshare/",
                headers = self._json_headers,
                cookies = self._cookies,
            )

    def set_thumbnail(self, *, file):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        with open(file, "rb") as f:
            thumbnail = f.read()
        requests.post(
            f"https://scratch.mit.edu/internalapi/project/thumbnail/{self.id}/set/",
            data = thumbnail,
            headers = self._headers,
            cookies = self._cookies,
        )

    def delete_comment(self, *, comment_id):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/comment/{comment_id}/",
            headers = self._headers,
            cookies = self._cookies,
        ).headers

    def report_comment(self, *, comment_id):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/comment/{comment_id}/report",
            headers = self._headers,
            cookies = self._cookies,
        )

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        headers = self._json_headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        ).text


    def reply_comment(self, content, *, parent_id, commentee_id=""):
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)


    def set_title(self, text):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        r = requests.put(f"https://api.scratch.mit.edu/projects/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            data=json.dumps({"title":text})).json()
        return self._update_from_dict(r)

    def set_instructions(self, text):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        r = requests.put(f"https://api.scratch.mit.edu/projects/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            data=json.dumps({"instructions":text})).json()
        return self._update_from_dict(r)

    def set_notes(self, text):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(_exceptions.Unauthorized)
            return
        r = requests.put(f"https://api.scratch.mit.edu/projects/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            data=json.dumps({"description":text})).json()
        return self._update_from_dict(r)

    def studios(self):
        return requests.get(f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/studios").json()

    def ranks(self):
        return requests.get(f"https://scratchdb.lefty.one/v3/project/info/{self.id}").json()["statistics"]["ranks"]


# ------ #

def get_project(project_id):
    try:
        project = Project(id=int(project_id))
        if not project.update():
            project = PartialProject(id=int(project_id))
        return project
    except KeyError:
        return None
