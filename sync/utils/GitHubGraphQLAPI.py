from datetime import datetime
from typing import Optional, List

import requests
from dateutil.parser import parse


class GitHubGraphQLAPI:
    def __init__(self, api_token: str):
        self._api_token = api_token

    def _graphql_query(self, query: str) -> Optional[dict]:
        query = {"query": query}

        response = requests.post(
            url="https://api.github.com/graphql",
            headers={
                "Authorization": f"bearer {self._api_token}",
                "Content-Type": "application/json",
            },
            json=query
        )

        if response.ok:
            return response.json()
        else:
            return None

    def _query_repository(self, owner: str, name: str, query: str) -> Optional[dict]:
        params = "owner: \"{}\", name: \"{}\"".format(owner, name)
        _query = "query { repository(%s) { %s } }" % (params, query)
        result = self._graphql_query(_query)

        try:
            data = result.get("data")
            repository = data.get("repository")
            return repository
        except AttributeError:
            return None

    def get_sponsor_url(self, owner: str, name: str) -> List[str]:
        repository = self._query_repository(
            owner=owner,
            name=name,
            query="fundingLinks { platform url }"
        )
        if repository is None:
            return list()

        links = list()
        funding_links = repository["fundingLinks"]

        for item in funding_links:
            if item["platform"] == "GITHUB":
                name = item["url"].split("/")[-1]
                links.append(f"https://github.com/sponsors/{name}")
            else:
                links.append(item["url"])

        return links

    def get_homepage_url(self, owner: str, name: str) -> Optional[str]:
        repository = self._query_repository(
            owner=owner,
            name=name,
            query="homepageUrl"
        )
        if repository is None:
            return None

        homepage_url = repository["homepageUrl"]
        if homepage_url != "":
            return homepage_url
        else:
            return None

    def get_pushed_at(self, owner: str, name: str) -> Optional[datetime]:
        repository = self._query_repository(
            owner=owner,
            name=name,
            query="pushedAt"
        )
        if repository is None:
            return None

        try:
            return parse(repository["pushedAt"])
        except TypeError:
            return None
