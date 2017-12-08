# -*- coding: utf-8 -*-
import os
import json
from django.test import LiveServerTestCase
from users.factory_classes import UserFactory
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.conf import settings
from emails.models import Email
from users.models import User, Message
from users.utils import thumbnail_size
from rest_framework import status
from PIL import Image
from dashboard.tasks.models import Tag
from dashboard.lists.models import List, ShareListPending
from dashboard.lists.factory_classes import ListFactory, ListFactoryShareWithUsers
from dashboard.tasks.factory_classes import TagFactory, TaskWithTagsAndStepsFactory
from ..serializers import UserSerializer

class CreateUserWithInboxTestCase(TestCase):
    def setUp(self):
        pass

    def test_create_user_and_inbox(self):
        self.assertEqual(0, List.objects.all().count())
        john = UserFactory.create(username="john", email="john@example.com")
        john_list = List.objects.get(owner=john, is_inbox=True)
        self.assertTrue(john in john_list.share_with.all())
        self.assertNotEqual(john.registration_key, "0000000000000000000000000000000000000000")

    def test_serialized_user_with_inbox_pk(self):
        john = UserFactory.create(username="john", email="john@example.com")
        john_list = List.objects.get(owner=john, is_inbox=True)
        self.assertEqual(john_list.pk, john.inbox_pk)

    def test_method_all_lists_pk(self):
        john = UserFactory.create(username="john", email="john@example.com")
        list1 = ListFactory.create(owner=john)
        list2 = ListFactory.create(owner=john)
        list3 = ListFactory.create(owner=john)
        lists_pk = set()
        lists_pk.add(list1.pk)
        lists_pk.add(list2.pk)
        lists_pk.add(list3.pk)
        lists_pk.add(john.inbox_pk)

        self.assertSetEqual(set(john.all_lists_pk), lists_pk)

    def test_create_user_sharing_pending_list(self):
        email = "new_user@wp.pl"
        john = UserFactory(username="john", email="john@example.com")
        list1 = ListFactory.create(owner=john)
        list2 = ListFactory.create(owner=john)
        sharing_list_pending1 = ShareListPending()
        sharing_list_pending1.email = email
        sharing_list_pending1.list = list1
        sharing_list_pending1.user = john
        sharing_list_pending1.save()
        sharing_list_pending2 = ShareListPending()
        sharing_list_pending2.email = email
        sharing_list_pending2.list = list2
        sharing_list_pending2.user = john
        sharing_list_pending2.save()
        new_user = UserFactory.create(username="new_user", email=email)
        self.assertEqual(new_user.all_team_mates().count(), 1)
        self.assertTrue(new_user.is_team_mate(john.id))
        list1 = List.objects.get(id=list1.pk)
        list2 = List.objects.get(id=list2.pk)
        self.assertTrue(list1.is_shared_with_user(new_user))
        self.assertTrue(list2.is_shared_with_user(new_user))



class LoginUser(TestCase):
    def setUp(self):
        self.username_john = "john"
        self.pass_john = "pass"
        self.email_john = "john@example.com"
        self.john = UserFactory(username=self.username_john, email=self.email_john)

    def test_bad_password(self):
        response = self.client.post(reverse("login-login"), {"email": self.email_john, "password": "bad_password"})
        self.assertEqual(response.status_code, 400)

    def test_bad_password_next_good_password(self):
        """Bug #158"""
        response = self.client.post(reverse("login-login"), {"email": self.email_john, "password": "bad_password"})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("login-login"), {"email": self.email_john, "password": self.pass_john})
        self.assertEqual(response.status_code, 200)


class GetUserTestCase(TestCase):
    def setUp(self):
        self.john = UserFactory(username="john", email="john@example.com")
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def test_get_user_with_id(self):
        #adding when sharing tasks will be active
        pass

    def test_get_authenticated_user(self):
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.john.pk}))
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["username"], self.john.username)
        self.assertEqual(result["email"], self.john.email)
        self.assertEqual(result["avatar_url"], self.john.avatar_url())
        self.assertEqual(result["id"], self.john.id)

    def test_get_authenticated_user_after_logout(self):
        self.client.logout()
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.john.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TeamCasesTestCase(TestCase):
    def setUp(self):
        #create users
        self.bill = UserFactory.create(username="bill", is_superuser=True, is_staff=True)
        self.tom = UserFactory.create(username="tom")
        self.kate = UserFactory.create(username="kate")

        self.greg = UserFactory.create(username="greg")
        #create team
        ListFactoryShareWithUsers.create(name="List 1", owner=self.bill, share_with=[self.bill, self.tom, self.kate])

        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))

    def test_users_list(self):
        response = self.client.get(reverse("user-teamlist", kwargs={"pk": self.bill.pk}))
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result), 2)
        my_set = {self.tom.pk, self.kate.pk}
        result_set = {result[0]['id'], result[1]['id']}
        self.assertSetEqual(result_set, my_set)

    def test_check_user(self):
        response = self.client.post(reverse("user-checkteammember", kwargs={"pk": self.bill.pk}), {"email": self.tom.email})
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result['email'], self.tom.email)
        self.assertEqual(result["username"], self.tom.username)

    def test_check_non_user(self):
        response = self.client.post(reverse("user-checkteammember", kwargs={"pk": self.bill.pk}), {"email": "test@test.com"})
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result['email'], "test@test.com")
        self.assertEqual(result["status"], "pending")


class UserTagsTestCase(TestCase):
    def setUp(self):
        self.bill = UserFactory.create(username="bill")
        self.james = UserFactory.create(username="james")
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))

    def test_add_new_tag_valid(self):
        tag_name = "tag 1"
        response = self.client.post(reverse("tag-list"), {"name": tag_name})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.filter(name=tag_name, author=self.bill).count(), 1)

    def test_add_new_tag_invalid(self):
        tag_counter = Tag.objects.filter(author=self.bill).count()
        response = self.client.post(reverse("tag-list"), {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(tag_counter, Tag.objects.filter(author=self.bill).count())

    def test_delete_tag(self):
        tag = TagFactory.create(name="Tag 1", author=self.bill)
        tag_counter = Tag.objects.filter(author=self.bill).count()
        response = self.client.delete(reverse("tag-detail", args=[tag.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(tag_counter, Tag.objects.filter(author=self.bill).count() + 1)

    def test_edit_tag(self):

        tag = TagFactory.create(name="Tag 1", author=self.bill)
        tag_counter = Tag.objects.filter(author=self.bill).count()
        response = self.client.put(reverse("tag-detail", args=[tag.id]), json.dumps({"name": "Tag 2"}),
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tag_counter, Tag.objects.filter(author=self.bill).count())
        tag = Tag.objects.get(id=tag.id)
        self.assertEqual(tag.name, "Tag 2")

    def test_edit_tag_invalid(self):

        tag = TagFactory.create(name="Tag 1", author=self.james)
        tag_counter = Tag.objects.filter(author=self.bill).count()
        response = self.client.put(reverse("tag-detail", args=[tag.id]), json.dumps({"name": "Tag 2"}),
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(tag_counter, Tag.objects.filter(author=self.bill).count())
        tag = Tag.objects.get(id=tag.id)
        self.assertEqual(tag.name, "Tag 1")

    def test_tags_list(self):
        TagFactory.create(name="Tag 1", author=self.bill)
        TagFactory.create(name="Tag 2", author=self.bill)
        TagFactory.create(name="Tag 3", author=self.bill)
        tags_list_name = [tag.name for tag in Tag.objects.filter(author=self.bill)]
        response = self.client.get(reverse("tag-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        for tag in result:
            self.assertTrue(tag['name'] in tags_list_name)
        self.assertEqual(len(result), Tag.objects.filter(author=self.bill).count())

    def test_tags_serialization_with_tasks_counter(self):
        tag1 = TagFactory.create(name="Tag 1", author=self.bill)
        tag2 = TagFactory.create(name="Tag 2", author=self.bill)
        tag3 = TagFactory.create(name="Tag 3", author=self.bill)
        bill_inbox = List.objects.get(id=self.bill.inbox_pk)
        TaskWithTagsAndStepsFactory.create(owner=self.james, author=self.bill, task_list=bill_inbox, tags=[tag1, tag2])
        TaskWithTagsAndStepsFactory.create(owner=self.james, author=self.bill, task_list=bill_inbox, tags=[tag2])
        TaskWithTagsAndStepsFactory.create(owner=self.james, author=self.bill, task_list=bill_inbox, tags=[tag3, tag1])
        TaskWithTagsAndStepsFactory.create(owner=self.james, author=self.bill, task_list=bill_inbox, tags=[tag1])
        TaskWithTagsAndStepsFactory.create(owner=self.james, author=self.bill, task_list=bill_inbox, tags=[tag1, tag2,
                                                                                                           tag3])
        response = self.client.get(reverse("tag-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode("utf-8"))
        for tag in result:
            if tag['name'] == tag1.name:
                self.assertEqual(tag['tasks_counter'], 4)
            elif tag['name'] == tag2.name:
                self.assertEqual(tag['tasks_counter'], 3)
            elif tag['name'] == tag3.name:
                self.assertEqual(tag['tasks_counter'], 2)
            else:
                self.assertEqual(tag['tasks_counter'], 0)

    def test_unique_tags_user(self):
        TagFactory.create(name="Tag 1", author=self.bill)
        tag_counter_old = Tag.objects.filter(author=self.bill).count()
        response = self.client.post(reverse("tag-list"), {"name": "Tag 1"})
        result = json.loads(response.content.decode("utf-8"))
        tag_counter_new = Tag.objects.filter(author=self.bill).count()
        self.assertEqual(tag_counter_new, tag_counter_old)
        self.assertEqual(result['name'], "Tag 1")

class EditUserTestCase(TestCase):

    def setUp(self):
        self.bill = UserFactory.create(username="bill")
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))
        self.test_data_path = os.path.join(os.path.dirname(__file__), "data")
        Image.init()

    def _upload_helper(self, filename):
        f = open(os.path.join(self.test_data_path, filename), "rb")
        response = self.client.post(reverse('user-changeavatar', kwargs={"pk": self.bill.pk}), {
            'file': f,
        }, follow=True)
        f.close()
        return response

    def _remove_avatars(self, user):
        for size in settings.DEFAULT_AVATAR_SIZES:
            sufix = "%sx%s" % (str(size[0]), str(size[1]))
            name = thumbnail_size(user.avatar.name, sufix)  # add sufix to name
            os.remove(settings.MEDIA_ROOT + '/' + name)

    def _create_json_object(self, user):
        pass

    def test_change_password(self):
        new_password = "new_pass"
        response = self.client.put(reverse("user-changepassword", kwargs={"pk": self.bill.pk}),
                                   json.dumps({"password": "pass", "new_password": new_password,
                                               "repeat_new_password": new_password}),
                                   follow=True, content_type='application/json')
        bill = User.objects.get(id=self.bill.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(bill.check_password(new_password))

    def test_change_password_bad_requests(self):
        response = self.client.put(reverse("user-changepassword", kwargs={"pk": self.bill.pk}),
                                   json.dumps({"password": "pass", "new_password": "bad_password",
                                               "repeat_new_password": "nothing"}),
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        bill = User.objects.get(id=self.bill.id)
        self.assertTrue(bill.check_password("pass"))

        response = self.client.put(reverse("user-changepassword", kwargs={"pk": self.bill.pk}),
                                   json.dumps({"password": "bad_password", "new_password": "bad_password",
                                               "repeat_new_password": "bad_password"}),
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        bill = User.objects.get(id=self.bill.id)
        self.assertTrue(bill.check_password("pass"))

    def test_change_username(self):
        new_username = "new_username"
        serialized_user = UserSerializer(self.bill).data
        serialized_user.update({'username': new_username})
        response = self.client.put(reverse("user-detail", kwargs={"pk": self.bill.pk}),
                               json.dumps(serialized_user),
                               follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bill = User.objects.get(id=self.bill.id)
        self.assertEqual(bill.username, new_username)

    def test_change_email(self):
        new_email = "new_email@email.com"
        serialized_user = UserSerializer(self.bill).data
        serialized_user.update({'email': new_email})
        response = self.client.put(reverse("user-detail", kwargs={"pk": self.bill.pk}),
                               json.dumps(serialized_user),
                               follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bill = User.objects.get(id=self.bill.id)
        self.assertEqual(bill.email, new_email)

    def test_change_email_bad_request(self):
        new_email = "new_email"
        serialized_user = UserSerializer(self.bill).data
        serialized_user.update({'email': new_email})
        response = self.client.put(reverse("user-detail", kwargs={"pk": self.bill.pk}),
                               json.dumps(serialized_user),
                               follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        bill = User.objects.get(id=self.bill.id)
        self.assertEqual(bill.email, self.bill.email)

    def test_send_message_to_board(self):
        """
            Test send message to board
        """
        new_message = "Testing testing testing testing testing testing"
        response = self.client.put(reverse("user-send_message_to_board"),
                               json.dumps({"message": new_message}),
                               follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Message.objects.get().message, new_message)
        self.assertEqual(Message.objects.get().user.id, self.bill.id)
        email = Email.objects.get(email=settings.ADMINS[0][1])
        self.assertGreaterEqual(email.body.find(new_message), 0)

    def test_change_avatar(self):
        """
            Change user avatar
        """
        response = self._upload_helper("avatar_test_default.jpg")
        self.assertEqual(response.status_code, 200)
        bill = User.objects.get(id=self.bill.id)
        os.path.isfile(settings.MEDIA_ROOT + bill.avatar.name)
        self._remove_avatars(bill)


class ForgotPasswordTestCase(TestCase):

    def setUp(self):
        self.bill = UserFactory.create(username="bill")
        self.client = Client(enforce_csrf_checks=False)

    def test_send_new_password(self):
        response = self.client.post(reverse("user-forgot_password"), {"email": self.bill.email}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Email.objects.all().count(), 1)
        bill = User.objects.get(email=self.bill.email)
        self.assertFalse(bill.check_password("pass"))

    def test_send_new_password_non_existing_user(self):
        response = self.client.post(reverse("user-forgot_password"), {"email": "nonexisting_email@example.com"},
                                    follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Email.objects.all().count(), 0)
        self.assertTrue(self.bill.check_password("pass"))