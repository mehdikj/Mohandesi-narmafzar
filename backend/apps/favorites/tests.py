
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.identity.models import User
from apps.resources.models import Resource
from apps.favorites.models import Favorite


class FavoriteAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="TestPassword123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="TestPassword123",
        )

        self.resource = Resource.objects.create(
            title="Public Test Book",
            created_by=self.user1,
            status=Resource.Status.PUBLISHED,
            access_policy=Resource.AccessPolicy.PUBLIC,
        )

        self.draft_resource = Resource.objects.create(
            title="Draft Test Book",
            created_by=self.user1,
            status=Resource.Status.DRAFT,
            access_policy=Resource.AccessPolicy.PUBLIC,
        )

        self.list_url = reverse("favorite-list-create")

    def test_authenticated_user_can_add_favorite(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            self.list_url,
            {"resource": self.resource.id},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Favorite.objects.filter(
                user=self.user1,
                resource=self.resource,
            ).exists()
        )

    def test_user_can_only_see_own_favorites(self):
        Favorite.objects.create(
            user=self.user1,
            resource=self.resource,
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_duplicate_favorite_is_rejected(self):
        Favorite.objects.create(
            user=self.user1,
            resource=self.resource,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            self.list_url,
            {"resource": self.resource.id},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_favorite_draft_resource(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            self.list_url,
            {"resource": self.draft_resource.id},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_delete_own_favorite(self):
        Favorite.objects.create(
            user=self.user1,
            resource=self.resource,
        )

        self.client.force_authenticate(user=self.user1)

        delete_url = reverse(
            "favorite-delete",
            kwargs={"resource_id": self.resource.id},
        )

        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Favorite.objects.filter(
                user=self.user1,
                resource=self.resource,
            ).exists()
        )

    def test_user_cannot_delete_another_users_favorite(self):
        Favorite.objects.create(
            user=self.user1,
            resource=self.resource,
        )

        self.client.force_authenticate(user=self.user2)

        delete_url = reverse(
            "favorite-delete",
            kwargs={"resource_id": self.resource.id},
        )

        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Favorite.objects.filter(
                user=self.user1,
                resource=self.resource,
            ).exists()
        )

    def test_anonymous_user_cannot_access_favorites(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
