from locust import HttpUser, task, between
import faker

fake = faker.Faker()

class CommonUser(HttpUser):

    @task(10)
    def get_product_id(self):
        self.client.get('/products/' + str(fake.random_int(3, 100000)), name='product_id')

    @task(1)
    def search(self):
        self.client.get('/search?q=' + fake.word(), name='product_search')

    wait_time = between(5, 15)
