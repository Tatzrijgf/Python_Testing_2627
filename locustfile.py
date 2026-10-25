from locust import HttpUser, task, between

class GudlftPerformanceTest(HttpUser):
    # Simule un temps de réflexion humain entre 1 et 3 secondes entre chaque action
    wait_time = between(1, 3)

    @task(3)
    def test_public_endpoints(self):
        """Teste le chargement des pages publiques (Cible : < 5 secondes)."""
        # Page d'accueil
        self.client.get("/")
        # Tableau des points public (Exigence de la Phase 2)
        self.client.get("/points")

    @task(2)
    def test_secretary_login_and_view(self):
        """Simule l'authentification et l'accès au tableau de bord."""
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task(1)
    def test_purchase_places(self):
        """Simule une mise à jour d'achat de places (Cible : < 2 secondes)."""
        self.client.post("/purchasePlaces", data={
            "club": "Simply Lift",
            "competition": "Fall Classic",
            "places": "1"
        })
