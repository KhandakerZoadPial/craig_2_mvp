from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    # host = "http://127.0.0.1:8000"

    @task # This decorator marks a method as a task to be executed by the user
    def test_user_endpoint(self):
        """
        This task simulates a user hitting your gateway, which then
        proxies the request to the user_service.
        """
        endpoint_url = "/api/user_service/test_endpoint/"
        
        # self.client is a pre-made requests-like session for making HTTP calls
        self.client.get(endpoint_url)

        # If you needed to test a POST request, it would look like this:
        # self.client.post("/api/user_service/some_other_endpoint/", json={"id": 1, "name": "test"})