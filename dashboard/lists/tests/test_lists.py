#-*- coding: utf-8 -*-
import json
from datetime import date, timedelta
from django.test import LiveServerTestCase
#from selenium.webdriver.firefox.webdriver import WebDriver
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.translation import ugettext as _
from rest_framework import status
from dashboard.lists.factory_classes import ListFactory, ListFactoryShareWithUsers
from dashboard.tasks.factory_classes import TagFactory, TaskFactory
from dashboard.tasks.models import Tag, Task
from dashboard.tasks.factory_classes import TaskWithTagsAndStepsFactory
from users.factory_classes import UserFactory
from users.models import User
from dashboard.lists.models import List, ShareListPending
from .mixins import UpdateListMixin
# create list


class CreateListTest(TestCase):

    def setUp(self):
        self.john = UserFactory.create(username="john", email="john@example.com")
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        self.url = reverse("list-list")

    def test_create_list(self):
        list_name = "List 1"
        response = self.client.post(self.url, json.dumps({"name": list_name}), follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mylist = List.objects.get(name=list_name, is_inbox=False)
        self.assertEqual(mylist.owner.pk, self.john.pk)
        self.assertEqual([user.pk for user in mylist.share_with.all()], [self.john.pk])
        self.assertEqual(mylist.name, list_name)

    def test_create_sublist(self):
        parent_list = ListFactory.create(owner=self.john, color="#b679b2")
        list_name = "child_list"
        response = self.client.post(self.url, json.dumps({"name": list_name, "ancestor": parent_list.pk}),
                                    follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        child_list = List.objects.get(name=list_name)
        self.assertEqual(child_list.name, list_name)
        self.assertEqual(child_list.ancestor, parent_list)

    def test_craete_list_with_sharelist_non_user(self):
        email = "test@test.com"
        list_name = "List 1"
        response = self.client.post(self.url, json.dumps({"name": list_name,  "share_with": [{'email': email}]}),
                                    follow=True, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShareListPending.objects.filter(email=email, list=List.objects.get(name=list_name)).exists())


class EditListTest(UpdateListMixin, TestCase):
    """
        Testing view to edit list
    """
    def setUp(self):
        self.user = UserFactory.create()
        self.team_mate = UserFactory.create()
        self.enemy = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.user)
        self.list_1_1 = ListFactoryShareWithUsers.create(ancestor=self.list_1, owner=self.user)
        self.list_1_1_1 = ListFactoryShareWithUsers.create(ancestor=self.list_1_1, owner=self.user)
        self.list_2 = ListFactoryShareWithUsers.create(owner=self.user)
        self.assertTrue(self.client.login(email=self.user.email, password="pass"))

    def test_edit_ancestor(self):
        put_dict = self._create_list_dictionary(self.list_1_1)
        put_dict.update({"ancestor": self.list_2.pk})
        url = reverse("list-detail", kwargs={'pk': self.list_1_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_list_1_1 = List.objects.get(id=self.list_1_1.pk)
        self.assertEqual(new_list_1_1.ancestor, self.list_2)

    def test_edit_ancestor_fail(self):
        """
            This test result in failure because inbox cannot have children lists
        """
        put_dict = self._create_list_dictionary(self.list_1_1)

        put_dict.update({"ancestor": self.user.inbox_pk})
        url = reverse("list-detail", kwargs={'pk': self.list_1_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        new_list_1_1 = List.objects.get(id=self.list_1_1.pk)
        self.assertEqual(new_list_1_1.ancestor, self.list_1)

    def test_edit_list_without_ancestor(self):
        put_dict = self._create_list_dictionary(self.list_2)
        put_dict.update({"name": "new_name"})
        url = reverse("list-detail", kwargs={'pk': self.list_2.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_list_2 = List.objects.get(id=self.list_2.pk)
        self.assertEqual(new_list_2.name, "new_name")

    def test_edit_list_default_parameters_for_task(self):
        put_dict = self._create_list_dictionary(self.list_2)
        put_dict.update({"default_priority": "C"})
        put_dict.update({"default_finish_date": '1'})
        put_dict.update({"default_type_finish_date": '1'})
        url = reverse("list-detail", kwargs={'pk': self.list_2.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_list_2 = List.objects.get(id=self.list_2.pk)
        self.assertEqual(new_list_2.default_priority, "C")
        self.assertEqual(new_list_2.default_finish_date, 1)
        self.assertEqual(new_list_2.default_type_finish_date, 1)
        task_date = date.today() + timedelta(1)
        self.assertEqual(new_list_2.task_finish_date(),  task_date.strftime("%d-%m-%Y"))

    def test_sharing_list_and_child_list(self):
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": [{'id': str(self.team_mate.id)}]})
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(map(int, self.list_1.share_with.all().values_list("id", flat=True))),
                             [self.user.id, self.team_mate.id])

    def test_sharing_list(self):
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": [{'id': str(self.team_mate.id)}]})
        url = reverse("list-detail", kwargs={'pk': self.list_1_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(map(int, self.list_1_1.share_with.all().values_list("id", flat=True))),
                             [self.user.id, self.team_mate.id])

    def test_unsharing_list(self):
        self.list_1.share_with.add(self.team_mate)
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": []})
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(map(int, self.list_1.share_with.all().values_list("id", flat=True))), [self.user.id])

    def test_unsharing_list_moving_task(self):
        task_team_mate = TaskFactory.create(owner=self.team_mate, task_list=self.list_1)
        self.list_1.share_with.add(self.team_mate)
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": []})
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(map(int, self.list_1.share_with.all().values_list("id", flat=True))), [self.user.id])

    def test_delete_list_pass(self):
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deleted_list = List.objects.get(id=self.list_1.pk)
        self.assertFalse(deleted_list.is_active)

    def test_delete_list_not_permission(self):
        list_enemy = ListFactoryShareWithUsers.create(owner=self.enemy)
        url = reverse("list-detail", kwargs={'pk': list_enemy.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deleted_list = List.objects.get(id=list_enemy.pk)
        self.assertTrue(deleted_list.is_active)

    def test_delete_inbox_fail(self):
        url = reverse("list-detail", kwargs={'pk': self.user.inbox_pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deleted_list = List.objects.get(id=self.user.inbox_pk)
        self.assertTrue(deleted_list.is_active)

    def test_sharing_list_non_user(self):
        email = "new_email@example.com"
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": [{'email': email}]})
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ShareListPending.objects.filter(email=email, list=self.list_1).exists())



class SubListDetailsTest(TestCase):
    """
        Testowanie widoków do wyświetlania podlist
    """
    def setUp(self):
        self.user = UserFactory.create()
        self.list_1 = ListFactory.create(name="list 1", owner=self.user)
        self.list_1_1 = ListFactory.create(name="list 1 1", ancestor=self.list_1, owner=self.user)
        self.list_1_2 = ListFactory.create(name="list 1 2", ancestor=self.list_1, owner=self.user)
        self.list_1_2_1 = ListFactory.create(name="list 1 2 1", ancestor=self.list_1_2, owner=self.user)
        self.list_1_3 = ListFactory.create(name="list 1 3", ancestor=self.list_1, owner=self.user)
        self.assertTrue(self.client.login(email=self.user.email, password="pass"))

    def test_sublist_details(self):
        url = reverse('list-sublists', kwargs={'pk': self.list_1.pk})
        response = self.client.get(url, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 3)
        for mylist in result:
            list_object = List.objects.get(id=mylist["id"])
            self.assertEqual(list_object.ancestor, self.list_1)

    def test_child_level(self):
        url = reverse('list-list')
        response = self.client.get(url, {"child_level": 0}, follow=True, content_type="application/json")
        result = json.loads(response.content.decode('utf-8'))
        #two because we have inbox
        self.assertEqual(len(result), 2)

        response = self.client.get(url, {"child_level": 1}, follow=True, content_type="application/json")
        result = json.loads(response.content.decode('utf-8'))
        # four lists and one inbox
        self.assertEqual(len(result), 5)

    def test_child_level_with_sharing_list(self):
        #extra data in database
        user2 = UserFactory.create()

        self.list_2 = ListFactoryShareWithUsers.create(owner=user2, name="list 2", share_with=[user2])
        self.list_2_1 = ListFactoryShareWithUsers.create(name="list 2_1", ancestor=self.list_2, owner=user2,
                                                         share_with=[user2, self.user])
        self.list_3 = ListFactoryShareWithUsers.create(name="list 3", owner=user2,
                                                       share_with=[user2])
        self.list_3_1 = ListFactoryShareWithUsers.create(name="list 3_1", ancestor=self.list_3, owner=user2,
                                                         share_with=[user2])
        self.list_3_1_1 = ListFactoryShareWithUsers.create(name="list 3_1_1", ancestor=self.list_3_1, owner=user2,
                                                           share_with=[user2, self.user])

        url = reverse('list-list')
        response = self.client.get(url, {"child_level": 0}, follow=True, content_type="application/json")
        result = json.loads(response.content.decode('utf-8'))
        #TR: Zmienna result powinna zawierać 2 listy (lista_1 i inbox) oraz listy 2_1 i 3_1_1
        self.assertEqual(len(result), 4)

    def test_child_level_with_sharing_list_part2(self):
        #extra data in database
        user2 = UserFactory.create()

        self.list_2 = ListFactoryShareWithUsers.create(owner=user2, name="list 2", share_with=[user2])
        self.list_2_1 = ListFactoryShareWithUsers.create(name="list 2_1", ancestor=self.list_2, owner=user2,
                                                         share_with=[user2, self.user])
        self.list_3 = ListFactoryShareWithUsers.create(name="list 3", owner=user2,
                                                       share_with=[user2])
        self.list_3_1 = ListFactoryShareWithUsers.create(name="list 3_1", ancestor=self.list_3, owner=user2,
                                                         share_with=[user2, self.user])
        self.list_3_1_1 = ListFactoryShareWithUsers.create(name="list 3_1_1", ancestor=self.list_3_1, owner=user2,
                                                           share_with=[user2])

        url = reverse('list-list')
        response = self.client.get(url, {"child_level": 0}, follow=True, content_type="application/json")
        result = json.loads(response.content.decode('utf-8'))
        #TR: Zmienna result powinna zawierać 2 listy (lista_1 i inbox) oraz listy 2_1 i 3_1
        self.assertEqual(len(result), 4)

    def test_inbox_is_first(self):
        url = reverse('list-list')
        response = self.client.get(url, {"child_level": 1}, follow=True, content_type="application/json")
        result = json.loads(response.content.decode('utf-8'))[0]
        self.assertEqual(result['is_inbox'], True)

    def test_serialized_sublist(self):
        """
        TR: Test sprawdza, czy podlisty są dobrze serializowane i czy są uwzględnianie uprawnienia
        """
        user2 = UserFactory.create()
        url = reverse('list-list')
        self.list_3 = ListFactoryShareWithUsers.create(name="list 3", owner=user2,
                                                       share_with=[user2, self.user])
        self.list_3_1 = ListFactoryShareWithUsers.create(name="list 3_1", ancestor=self.list_3, owner=user2,
                                                         share_with=[user2, self.user])
        self.list_3_1_1 = ListFactoryShareWithUsers.create(name="list 3_1_1", ancestor=self.list_3_1, owner=user2,
                                                           share_with=[user2, self.user])
        #This list is only User2
        self.list_3_1_2 = ListFactoryShareWithUsers.create(name="list 3_1_2", ancestor=self.list_3_1, owner=user2,
                                                           share_with=[user2])
        self.list_3_1_3 = ListFactoryShareWithUsers.create(name="list 3_1_3", ancestor=self.list_3_1, owner=user2,
                                                           share_with=[user2, self.user])

        self.list_3_2 = ListFactoryShareWithUsers.create(name="list 3_2", ancestor=self.list_3, owner=user2,
                                                         share_with=[user2, self.user])
         #This list is only User2
        self.list_3_3 = ListFactoryShareWithUsers.create(name="list 3_3", ancestor=self.list_3, owner=user2,
                                                         share_with=[user2])
        self.list_3_4 = ListFactoryShareWithUsers.create(name="list 3_4", ancestor=self.list_3, owner=user2,
                                                         share_with=[user2, self.user])
        response = self.client.get(url, {"child_level": 0}, follow=True, content_type="application/json")
        result = json.loads(response.content.decode('utf-8'))
        # result[1] it is list 3

        self.assertEqual(self.list_3.name, result[2]['name'])
        # List 3 should contain three serialized lists (list 3_1, list 3_2 and list 3_3) in key lists
        self.assertEqual(len(result[1]['lists']), 3)
        # List 3_1 should contain two serialized lists (list 3_1_1 i list 3_1_3) in key lists
        self.assertEqual(self.list_3_1.name, result[2]["lists"][0]['name'])
        self.assertEqual(len(result[2]["lists"][0]['lists']), 2)


class ShareWithDetailsTest(TestCase):
    """
        Testowanie widoków do wyświetlania użytkowników z którymi lista jest współdzielona
    """
    def setUp(self):
        self.user = UserFactory.create()
        self.list_1 = ListFactory.create(owner=self.user)
        self.assertTrue(self.client.login(email=self.user.email, password="pass"))

    def test_sharewith_detail(self):
        url = reverse('list-sharewithlist', kwargs={'pk': self.list_1.pk})
        response = self.client.get(url, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), len(self.list_1.share_with.all()))
        for user in result:
            user_object = User.objects.get(id=user['id'])
            self.assertIn(user_object, self.list_1.share_with.all())

    def test_method_is_shared_with_user(self):
        """ Testowanie metody is_shared_with_user
        """
        self.assertEqual(self.list_1.is_shared_with_user(self.user), True)


class TagsListTest(TestCase):
    """
        Do serializacji listy należy dodać tagi do wszystkich zadań przypisanych do tej listy, które zostały dodane
        przez zalogowanego użytkownika

    """
    def setUp(self):
        self.james = UserFactory.create(username="James")
        self.assertTrue(self.client.login(email=self.james.email, password="pass"))
        self.user = UserFactory.create()
        self.list_1 = ListFactory.create(owner=self.james)
        self.list_1_1 = ListFactory.create(owner=self.james, ancestor=self.list_1)
        self.list_1_1_1 = ListFactory.create(owner=self.james, ancestor=self.list_1_1)
        tag1 = TagFactory.create(name="work 1", author=self.james)
        tag2 = TagFactory.create(name="home 1", author=self.james)
        tag3 = TagFactory.create(name="focus 1", author=self.james)
        tag4 = TagFactory.create(name="tag for list 2", author=self.james)
        tag5 = TagFactory.create(name="enemy", author=self.user)
        self.tags_list = [tag1, tag2, tag3, tag4]
        for _ in range(5):
            TaskWithTagsAndStepsFactory.create(task_list=self.list_1, owner=self.james, author=self.james,
                                                finish_date=None, tags=self.tags_list)
        TaskWithTagsAndStepsFactory.create(task_list=self.list_1_1, owner=self.james, author=self.james,
                                           finish_date=None, tags=[Tag.objects.get(name="tag for list 2")])

    def test_serialized_list(self):

        url = reverse('list-detail', kwargs={'pk': self.list_1.pk})
        response = self.client.get(url, follow=True, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result['tags']), 4)
        for tag in result['tags']:
            self.assertTrue(tag['name'] in ["work 1", "home 1", "focus 1", "work", "home", "focus", "tag for list 2"])

    def test_serialized_list_task_counter(self):
        TaskFactory.create(owner=self.james, author=self.user, task_list=self.list_1_1)
        TaskFactory.create(owner=self.james, author=self.user, task_list=self.list_1_1)
        TaskFactory.create(owner=self.james, author=self.user, task_list=self.list_1_1_1)

        url = reverse('list-detail', kwargs={'pk': self.list_1.pk})
        response = self.client.get(url, follow=True, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(int(result['tasks_counter']), 9)  # 3 from this test and 6 from setUp

        url = reverse('list-detail', kwargs={'pk': self.list_1_1.pk})
        response = self.client.get(url, follow=True, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(int(result['tasks_counter']), 4)  #3 from this test and 1 from setUp

        url = reverse('list-detail', kwargs={'pk': self.list_1_1_1.pk})
        response = self.client.get(url, follow=True, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(int(result['tasks_counter']), 1)  #only one from this test


class DeleteorLeaveList(TestCase):

    def setUp(self):

        self.owner = UserFactory.create()
        self.sheared = UserFactory.create()
        self.list = ListFactoryShareWithUsers.create(owner=self.owner, name="list", share_with=[self.sheared])

    def test_delete_list_by_owner(self):
        self.assertTrue(self.client.login(email=self.owner.email, password="pass"))
        url = reverse("list-detail", kwargs={'pk': self.list.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deleted_list = List.objects.get(id=self.list.pk)
        self.assertFalse(deleted_list.is_active)

    def test_leave_list(self):
        self.assertTrue(self.client.login(email=self.sheared.email, password="pass"))
        url = reverse("list-detail", kwargs={'pk': self.list.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deleted_list = List.objects.get(id=self.list.pk)
        self.assertTrue(deleted_list.is_active)
        self.assertFalse(deleted_list.is_shared_with_user(self.sheared))
