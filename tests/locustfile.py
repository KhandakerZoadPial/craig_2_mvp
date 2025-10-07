from locust import HttpUser, task, between

class WebServiceUser(HttpUser):
    wait_time = between(1, 3)

    @task 
    def login_task(self):
        user_credentials = {
            "email": "test@test.com",
            "password": "helloworld"
        }
        
        login_url = "/api/user_service/me_view/"
        headers = {"Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5MzEwNjMwLCJpYXQiOjE3NTkzMTAwMzAsImp0aSI6IjM3MDBjMTUyY2U5ODQ4MGU5M2U0ZWZhOTQ2MWE0YzFjIiwidXNlcl9pZCI6IjEifQ.PUAv8xWwRUUSkvFHrp1q9yEn8DwoWkUcHa4PHPkp5eA"}
        self.client.get(login_url, headers=headers)