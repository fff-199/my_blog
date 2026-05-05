from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from blog.models import Comment, Post


class CommentAjaxTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="u1", password="pass")
        self.post = Post.objects.create(
            title="t1",
            content="c1",
            author=self.user,
            is_published=True,
        )
        self.url = reverse("blog:add_comment_ajax", args=[self.post.pk])

    def test_create_top_level_comment_ok(self):
        res = self.client.post(
            self.url,
            data={"author_name": "a", "author_email": "a@example.com", "content": "hello"},
        )
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["pending"])
        self.assertIsNone(payload["parent_id"])
        self.assertTrue(Comment.objects.filter(post=self.post).exists())

    def test_honeypot_rejected(self):
        res = self.client.post(
            self.url,
            data={
                "author_name": "a",
                "author_email": "a@example.com",
                "content": "hello",
                "website": "spam",
            },
        )
        self.assertEqual(res.status_code, 400)
        payload = res.json()
        self.assertFalse(payload["ok"])

    def test_rate_limited(self):
        res1 = self.client.post(
            self.url,
            data={"author_name": "a", "author_email": "a@example.com", "content": "hello"},
            REMOTE_ADDR="1.1.1.1",
        )
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.post(
            self.url,
            data={"author_name": "a", "author_email": "a@example.com", "content": "hello2"},
            REMOTE_ADDR="1.1.1.1",
        )
        self.assertEqual(res2.status_code, 429)
        payload = res2.json()
        self.assertEqual(payload["error"], "rate_limited")

    def test_reply_to_approved_parent(self):
        parent = Comment.objects.create(
            post=self.post,
            author_name="p",
            author_email="p@example.com",
            content="parent",
            is_approved=True,
        )
        res = self.client.post(
            self.url,
            data={
                "author_name": "a",
                "author_email": "a@example.com",
                "content": "reply",
                "parent_id": parent.pk,
            },
        )
        self.assertEqual(res.status_code, 200)
        comment = Comment.objects.latest("id")
        self.assertEqual(comment.parent_id, parent.pk)

    def test_reply_ignores_unapproved_parent(self):
        parent = Comment.objects.create(
            post=self.post,
            author_name="p",
            author_email="p@example.com",
            content="parent",
            is_approved=False,
        )
        res = self.client.post(
            self.url,
            data={
                "author_name": "a",
                "author_email": "a@example.com",
                "content": "reply",
                "parent_id": parent.pk,
            },
        )
        self.assertEqual(res.status_code, 200)
        comment = Comment.objects.latest("id")
        self.assertIsNone(comment.parent_id)

