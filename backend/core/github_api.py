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

    def fetch_user_contributions(self, username: str):
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
        return self.client.execute(query, variable_values=variables)
