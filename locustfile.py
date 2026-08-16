from locust import HttpUser, task, between

class CampusApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def get_complaints_unauth(self):
        self.client.get("/api/v1/complaints/")
