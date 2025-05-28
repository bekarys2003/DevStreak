# core/github_api.py

from datetime import datetime, timedelta, timezone
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

class GitHubAPIClient:
    def __init__(self, token: str):
        self.client = Client(
            transport=RequestsHTTPTransport(
                url="https://api.github.com/graphql",
                headers={"Authorization": f"Bearer {token}"},
                verify=True,
                retries=3,
            ),
            fetch_schema_from_transport=True
        )
    def fetch_user_contribution_calendar(self, username: str, days: int = 365):
        """
        Returns a list of dicts [{date: 'YYYY-MM-DD', count: int}, ...]
        for the last `days` days (including today).
        """
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days-1)
        end = now

        query = gql("""
        query($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from, to: $to) {
              contributionCalendar {
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """)

        variables = {
            "login": username,
            "from": start.isoformat(),
            "to": end.isoformat(),
        }
        result = self.client.execute(query, variable_values=variables)
        days_data = []
        weeks = result["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for week in weeks:
            for day in week["contributionDays"]:
                days_data.append({
                    "date": day["date"],
                    "count": day["contributionCount"]
                })
        # sort by date ascending
        days_data.sort(key=lambda d: d["date"])
        return days_data


    def fetch_user_contributions(self, username: str):
        """
        Total contributions ever (all-time).
        If you only care about today, use fetch_user_daily_contributions().
        """
        query = gql(
            """
            query ($login: String!) {
              user(login: $login) {
                contributionsCollection {
                  contributionCalendar {
                    totalContributions
                  }
                }
              }
            }
            """
        )
        variables = {"login": username}
        # remove that stray dot—you want to return the result of execute()
        return self.client.execute(query, variable_values=variables)

    def fetch_user_daily_contributions(self, username: str):
        """
        Returns how many commits, PRs, and reviews the user made *today* (UTC).
        """
        # compute UTC midnight of today and tomorrow
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        query = gql(
            """
            query ($login: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                  totalCommitContributions
                  totalPullRequestContributions
                  totalPullRequestReviewContributions
                }
              }
            }
            """
        )
        variables = {
            "login": username,
            "from": start.isoformat(),
            "to": end.isoformat(),
        }
        result = self.client.execute(query, variable_values=variables)
        # drill into the response
        coll = result["user"]["contributionsCollection"]
        return {
            "commits": coll["totalCommitContributions"],
            "pull_requests": coll["totalPullRequestContributions"],
            "reviews": coll["totalPullRequestReviewContributions"],
        }
