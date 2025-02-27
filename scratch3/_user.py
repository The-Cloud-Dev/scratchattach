#----- Getting users

import json
import requests
from . import _project
from . import _exceptions

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class User:

    def __init__(self, **entries):
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

    def __str__(self):
        return str(self.username)

    def update(self):
        try:

            response = json.loads(requests.get(f"https://api.scratch.mit.edu/users/{self.username}/").text)
            self.id = response["id"]
            self.scratchteam = response["scratchteam"]
            self.join_date = response["history"]["joined"]
            self.about_me = response["profile"]["bio"]
            self.wiwo = response["profile"]["status"]
            self.country = response["profile"]["country"]
            self.icon_url = response["profile"]["images"]["90x90"]
        except Exception:
            raise(_exceptions.UserNotFound)

    def message_count(self):

        return json.loads(requests.get(f"https://api.scratch.mit.edu/users/{self.username}/messages/count/", headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3c6 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',}).text)["count"]

    def featured_data(self):
        # featured data
        try:
            response = json.loads(requests.get(f"https://scratch.mit.edu/site-api/users/all/{self.username}/").text)
            return {
                "label":response["featured_project_label_name"],
                "project":
                        dict(
                            id=str(response["featured_project_data"]["id"]),
                            author=response["featured_project_data"]["creator"],
                            thumbnail_url="https://"+response["featured_project_data"]["thumbnail_url"][2:],
                            title=response["featured_project_data"]["title"]
                        )
                    }
        except Exception:
            return None

    def follower_count(self):
        # follower count
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/followers/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Followers (")[1]
        text = text.split(")")[0]
        return int(text)

    def following_count(self):
        # following count
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/following/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Following (")[1]
        text = text.split(")")[0]
        return int(text)

    def followers(self, *, limit=40, offset=0):
        followers = []
        response = requests.get(
            f"https://api.scratch.mit.edu/users/{self.username}/followers/?limit={limit}&offset={offset}").json()
        while not len(response) == 0 and not len(followers) > limit:
            for follower in response:
                followers.append(User(
                    id = follower["id"],
                    name = follower["username"],
                    scratchteam = follower["scratchteam"],
                    join_date = follower["history"]["joined"],
                    icon_url = follower["profile"]["images"]["90x90"],
                    status = follower["profile"]["status"],
                    bio = follower["profile"]["bio"],
                    country = follower["profile"]["country"]
                ))
            if len(followers) == limit:
                break
        return followers

    def following(self, *, limit=40, offset=0):
        following = []
        response = requests.get(
            f"https://api.scratch.mit.edu/users/{self.username}/following/?limit={limit}&offset={offset}").json()
        while not len(response) == 0 and not len(following) > limit:
            for following_user in response:
                following.append(User(
                    id = following_user["id"],
                    name = following_user["username"],
                    scratchteam = following_user["scratchteam"],
                    join_date = following_user["history"]["joined"],
                    icon_url = following_user["profile"]["images"]["90x90"],
                    status = following_user["profile"]["status"],
                    bio = following_user["profile"]["bio"],
                    country = following_user["profile"]["country"]
                ))
            if len(following) == limit:
                break
        return following

    '''def get_comments(self, *, page=1):
        response = requests.get(f"https://scratch.mit.edu/site-api/comments/user/{self.z}/?page=1")'''

    def is_following(self, user):
        return requests.get(f"https://following-check.1tim.repl.co/api/{self.username}/?following={user}").json()["following"]

    def is_followed_by(self, user):
        return requests.get(f"https://following-check.1tim.repl.co/api/{user}/?following={self.username}").json()["following"]

    def project_count(self):
        return len(self.projects())

    def projects(self, *, limit=None, offset=0):
        if limit is None:
            _projects = json.loads(requests.get(
                f"https://api.scratch.mit.edu/users/{self.username}/projects/?offset={offset}",
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
                f"https://api.scratch.mit.edu/users/{self.username}/projects/?limit={limit}&offset={offset}",
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
            projects.append(_project.Project(
                _session = self._session,
                author = self.username,
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
                url = "https://scratch.mit.edu/projects/"+str(project["id"])
            ))
        return projects

    def favorites(self, *, limit=None, offset=0):
        if limit is None:
            _projects = json.loads(requests.get(
                f"https://api.scratch.mit.edu/users/{self.username}/favorites/?offset={offset}",
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
                f"https://api.scratch.mit.edu/users/{self.username}/favorites/?limit={limit}&offset={offset}",
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
            projects.append(_project.Project(
                _session = self._session,
                author = self.username,
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
                url = "https://scratch.mit.edu/projects/"+str(project["id"])
            ))
        return projects

    def toggle_commenting(self):
        requests.post(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/toggle-comments/",
            headers = headers,
            cookies = self._cookies
        )

    def set_bio(self, text):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(dict(
                comments_allowed = True,
                id = self.username,
                bio = text,
                thumbnail_url = self.icon_url,
                userId = self.id,
                username = self.username
            ))
        )

    def set_wiwo(self, text):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(dict(
                comments_allowed = True,
                id = self.username,
                status = text,
                thumbnail_url = self.icon_url,
                userId = self.id,
                username = self.username
            ))
        )

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        )

    def reply_comment(self, content, *, parent_id, commentee_id=""):
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def follow(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/followers/bob/add/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def unfollow(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/followers/bob/remove/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def delete_comment(self, *, comment_id):
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/del/",
            headers = headers,
            cookies = self._cookies,
            data = json.dumps({"id":str(comment_id)})
        )

    def report_comment(self, *, comment_id):
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/rep/",
            headers = headers,
            cookies = self._cookies,
            data = json.dumps({"id":str(comment_id)})
        )

    def comments(self, *, limit=20, page=1):
        return requests.get(
            f"https://scratch-comments-api.sid72020123.repl.co/user/?username={self.username}&limit={limit}&page={page}"
        ).json()

    def stats(self):
        try:
            stats= requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]
            stats.pop("ranks")
        except Exception:
            stats = {"loves":-1,"favorites":-1,"comments":-1,"views":-1,"followers":-1,"following":-1}
        return stats

    def ranks(self):
        try:
            return requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]["ranks"]
        except Exception:
            return {"country":{"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0},"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0}


# ------ #

def get_user(username):
    try:
        user = User(username=username)
        user.update()
        return user
    except KeyError:
        return None
