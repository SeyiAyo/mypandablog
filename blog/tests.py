from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import Post, Category, Comment, Newsletter, SavedPost, PostView
from .forms import CommentForm, NewsletterForm, PostForm
from .utils import get_sentiment, recommend_posts, get_client_ip

NO_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_category(title="Tech", slug=None, description=""):
    return Category.objects.create(
        title=title,
        slug=slug or slugify(title),
        description=description,
    )


def make_post(category, title="Hello World", status=Post.ACTIVE, featured=False, slug=None, content="", intro=""):
    return Post.objects.create(
        title=title,
        slug=slug or slugify(title),
        category=category,
        status=status,
        featured=featured,
        content=content,
        intro=intro,
    )


# ===========================================================================
# Model Tests
# ===========================================================================

class CategoryModelTests(TestCase):

    def test_str(self):
        cat = make_category("Django")
        self.assertEqual(str(cat), "Django")

    def test_slug_auto_generated(self):
        cat = Category.objects.create(title="My Category")
        self.assertEqual(cat.slug, "my-category")

    def test_slug_preserved_if_provided(self):
        cat = Category.objects.create(title="My Category", slug="custom-slug")
        self.assertEqual(cat.slug, "custom-slug")

    def test_get_absolute_url(self):
        cat = make_category("Tech", slug="tech")
        self.assertEqual(cat.get_absolute_url(), "/category/tech/")

    def test_ordering_alphabetical(self):
        make_category("Zebra")
        make_category("Alpha")
        titles = list(Category.objects.values_list("title", flat=True))
        self.assertEqual(titles, sorted(titles))


class PostModelTests(TestCase):

    def setUp(self):
        self.cat = make_category()

    def test_str(self):
        post = make_post(self.cat, title="Test Post")
        self.assertEqual(str(post), "Test Post")

    def test_slug_auto_generated(self):
        post = Post.objects.create(title="Auto Slug Post", category=self.cat, status=Post.ACTIVE)
        self.assertEqual(post.slug, "auto-slug-post")

    def test_slug_not_overwritten_on_save(self):
        post = make_post(self.cat, slug="keep-me")
        post.title = "Changed Title"
        post.save()
        self.assertEqual(post.slug, "keep-me")

    def test_meta_title_auto_populated(self):
        post = make_post(self.cat, title="A" * 70)
        self.assertEqual(post.meta_title, ("A" * 70)[:60])

    def test_meta_description_auto_populated_from_intro(self):
        post = make_post(self.cat, intro="Short intro text")
        self.assertEqual(post.meta_description, "Short intro text")

    def test_meta_description_truncated_to_160(self):
        post = make_post(self.cat, intro="X" * 200)
        self.assertLessEqual(len(post.meta_description), 160)

    def test_get_absolute_url(self):
        post = make_post(self.cat, title="Hello URL", slug="hello-url")
        self.assertEqual(post.get_absolute_url(), f"/{self.cat.slug}/hello-url/")

    def test_reading_time_minimum_one(self):
        post = make_post(self.cat, content="Few words")
        self.assertEqual(post.reading_time, 1)

    def test_reading_time_calculated(self):
        words = " ".join(["word"] * 400)
        post = make_post(self.cat, content=words)
        self.assertEqual(post.reading_time, 2)

    def test_default_status_draft(self):
        post = Post.objects.create(title="Draft Post", category=self.cat)
        self.assertEqual(post.status, Post.DRAFT)

    def test_ordering_newest_first(self):
        p1 = make_post(self.cat, title="First", slug="first")
        p2 = make_post(self.cat, title="Second", slug="second")
        posts = list(Post.objects.values_list("title", flat=True))
        self.assertEqual(posts[0], "Second")


class CommentModelTests(TestCase):

    def setUp(self):
        self.cat = make_category()
        self.post = make_post(self.cat)

    def test_str(self):
        comment = Comment.objects.create(
            post=self.post, name="Alice", email="alice@example.com", contents="Great!"
        )
        self.assertIn("Alice", str(comment))
        self.assertIn(self.post.title, str(comment))

    def test_default_is_approved_true(self):
        comment = Comment.objects.create(
            post=self.post, name="Bob", email="bob@example.com", contents="Nice."
        )
        self.assertTrue(comment.is_approved)


class NewsletterModelTests(TestCase):

    def test_str(self):
        n = Newsletter.objects.create(email="user@example.com")
        self.assertEqual(str(n), "user@example.com")

    def test_unique_email(self):
        Newsletter.objects.create(email="dup@example.com")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Newsletter.objects.create(email="dup@example.com")


class SavedPostModelTests(TestCase):

    def setUp(self):
        cat = make_category()
        self.post = make_post(cat)

    def test_str(self):
        sp = SavedPost.objects.create(post=self.post, ip_address="127.0.0.1")
        self.assertIn(self.post.title, str(sp))

    def test_unique_together(self):
        SavedPost.objects.create(post=self.post, ip_address="1.2.3.4")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            SavedPost.objects.create(post=self.post, ip_address="1.2.3.4")


class PostViewModelTests(TestCase):

    def setUp(self):
        cat = make_category()
        self.post = make_post(cat)

    def test_str(self):
        pv = PostView.objects.create(post=self.post, ip_address="1.2.3.4", session_key="abc123")
        self.assertIn(self.post.title, str(pv))


# ===========================================================================
# Form Tests
# ===========================================================================

class CommentFormTests(TestCase):

    def test_valid_form(self):
        form = CommentForm(data={"name": "Alice", "email": "alice@example.com", "contents": "Hello!"})
        self.assertTrue(form.is_valid())

    def test_missing_name(self):
        form = CommentForm(data={"email": "alice@example.com", "contents": "Hello!"})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_missing_email(self):
        form = CommentForm(data={"name": "Alice", "contents": "Hello!"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_email(self):
        form = CommentForm(data={"name": "Alice", "email": "not-an-email", "contents": "Hello!"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_contents(self):
        form = CommentForm(data={"name": "Alice", "email": "alice@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("contents", form.errors)


class NewsletterFormTests(TestCase):

    def test_valid_form(self):
        form = NewsletterForm(data={"email": "news@example.com"})
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = NewsletterForm(data={"email": "not-an-email"})
        self.assertFalse(form.is_valid())

    def test_empty_email(self):
        form = NewsletterForm(data={"email": ""})
        self.assertFalse(form.is_valid())


# ===========================================================================
# Utility Tests
# ===========================================================================

class GetSentimentTests(TestCase):

    def test_positive_text(self):
        score = get_sentiment("This is absolutely wonderful and amazing!")
        self.assertGreater(score, 0)

    def test_negative_text(self):
        score = get_sentiment("This is terrible and awful and I hate it.")
        self.assertLess(score, 0)

    def test_empty_text(self):
        self.assertEqual(get_sentiment(""), 0.0)

    def test_none_text(self):
        self.assertEqual(get_sentiment(None), 0.0)

    def test_html_stripped(self):
        score = get_sentiment("<p>Great post!</p>")
        self.assertIsInstance(score, float)

    def test_returns_float(self):
        score = get_sentiment("Hello world")
        self.assertIsInstance(score, float)


class RecommendPostsTests(TestCase):

    def setUp(self):
        self.cat1 = make_category("Cat1", slug="cat1")
        self.cat2 = make_category("Cat2", slug="cat2")

        self.post = make_post(self.cat1, title="Base Post", slug="base-post")
        self.same_cat = make_post(self.cat1, title="Same Cat", slug="same-cat")
        self.other_cat = make_post(self.cat2, title="Other Cat", slug="other-cat")

    def test_recommends_from_same_category(self):
        results = recommend_posts(self.post)
        self.assertIn(self.same_cat, results)

    def test_excludes_current_post(self):
        results = recommend_posts(self.post)
        self.assertNotIn(self.post, results)

    def test_limit_respected(self):
        for i in range(5):
            make_post(self.cat1, title=f"Extra {i}", slug=f"extra-{i}")
        results = recommend_posts(self.post, limit=3)
        self.assertLessEqual(len(results), 3)

    def test_tag_based_recommendation(self):
        tagged_post = make_post(self.cat2, title="Tagged Post", slug="tagged-post")
        self.post.tags.add("python")
        tagged_post.tags.add("python")
        results = recommend_posts(self.post)
        self.assertIn(tagged_post, results)

    def test_returns_latest_if_no_tag_or_category_match(self):
        isolated_cat = make_category("Isolated", slug="isolated")
        isolated_post = make_post(isolated_cat, title="Isolated Post", slug="isolated-post")
        results = recommend_posts(isolated_post)
        self.assertIsNotNone(results)


class GetClientIpTests(TestCase):

    def test_returns_remote_addr(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/", REMOTE_ADDR="5.5.5.5")
        ip = get_client_ip(request)
        self.assertEqual(ip, "5.5.5.5")

    def test_returns_x_forwarded_for_first(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/", HTTP_X_FORWARDED_FOR="9.9.9.9, 8.8.8.8", REMOTE_ADDR="1.2.3.4")
        ip = get_client_ip(request)
        self.assertEqual(ip, "9.9.9.9")


# ===========================================================================
# View Tests
# ===========================================================================

@override_settings(CACHES=NO_CACHE)
class FrontpageViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category()

    def test_returns_200(self):
        response = self.client.get(reverse("blog:frontpage"))
        self.assertEqual(response.status_code, 200)

    def test_uses_frontpage_template(self):
        response = self.client.get(reverse("blog:frontpage"))
        self.assertTemplateUsed(response, "frontpage.html")

    def test_shows_active_posts(self):
        post = make_post(self.cat, title="Active Post", slug="active-post")
        response = self.client.get(reverse("blog:frontpage"))
        self.assertContains(response, "Active Post")

    def test_does_not_show_draft_posts(self):
        make_post(self.cat, title="Draft Post", slug="draft-post", status=Post.DRAFT)
        response = self.client.get(reverse("blog:frontpage"))
        self.assertNotContains(response, "Draft Post")

    def test_featured_posts_in_context(self):
        make_post(self.cat, title="Featured", slug="featured", featured=True)
        response = self.client.get(reverse("blog:frontpage"))
        self.assertIn("featured_posts", response.context)
        featured = response.context["featured_posts"]
        self.assertEqual(len(featured), 1)

    def test_pagination(self):
        for i in range(15):
            make_post(self.cat, title=f"Post {i}", slug=f"post-{i}")
        response = self.client.get(reverse("blog:frontpage"))
        self.assertTrue(response.context["posts"].has_next())

    def test_categories_in_context(self):
        response = self.client.get(reverse("blog:frontpage"))
        self.assertIn("categories", response.context)


@override_settings(CACHES=NO_CACHE)
class AboutViewTests(TestCase):

    def test_returns_200(self):
        response = self.client.get(reverse("blog:about"))
        self.assertEqual(response.status_code, 200)

    def test_uses_about_template(self):
        response = self.client.get(reverse("blog:about"))
        self.assertTemplateUsed(response, "about.html")


@override_settings(CACHES=NO_CACHE)
class ContactViewTests(TestCase):

    def test_returns_200(self):
        response = self.client.get(reverse("blog:contact"))
        self.assertEqual(response.status_code, 200)

    def test_uses_contact_template(self):
        response = self.client.get(reverse("blog:contact"))
        self.assertTemplateUsed(response, "contact.html")


@override_settings(CACHES=NO_CACHE)
class PrivacyPolicyViewTests(TestCase):

    def test_returns_200(self):
        response = self.client.get(reverse("blog:privacy_policy"))
        self.assertEqual(response.status_code, 200)

    def test_uses_privacy_policy_template(self):
        response = self.client.get(reverse("blog:privacy_policy"))
        self.assertTemplateUsed(response, "privacy_policy.html")


@override_settings(CACHES=NO_CACHE)
class TermsConditionsViewTests(TestCase):

    def test_returns_200(self):
        response = self.client.get(reverse("blog:terms_conditions"))
        self.assertEqual(response.status_code, 200)

    def test_uses_terms_template(self):
        response = self.client.get(reverse("blog:terms_conditions"))
        self.assertTemplateUsed(response, "terms_conditions.html")


@override_settings(CACHES=NO_CACHE)
class PostDetailViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category("Tech", slug="tech")
        self.post = make_post(self.cat, title="My Post", slug="my-post")

    def test_returns_200_for_active_post(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_uses_post_detail_template(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "post_detail.html")

    def test_returns_404_for_draft_post(self):
        draft = make_post(self.cat, title="Draft", slug="draft", status=Post.DRAFT)
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "draft"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_wrong_category(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "wrong", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_view_tracked(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        self.client.get(url)
        self.assertEqual(PostView.objects.filter(post=self.post).count(), 1)

    def test_second_visit_same_session_not_double_counted(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        self.client.get(url)
        self.client.get(url)
        self.assertEqual(PostView.objects.filter(post=self.post).count(), 1)

    def test_post_in_context(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertEqual(response.context["post"], self.post)

    def test_recommended_posts_in_context(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertIn("recommended_posts", response.context)

    def test_is_saved_false_by_default(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertFalse(response.context["is_saved"])

    def test_comment_submission_creates_comment(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.post(url, {
            "name": "Alice",
            "email": "alice@example.com",
            "contents": "Great post!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)

    def test_comment_sentiment_score_saved(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        self.client.post(url, {
            "name": "Alice",
            "email": "alice@example.com",
            "contents": "This is absolutely wonderful and great!",
        })
        comment = Comment.objects.filter(post=self.post).first()
        self.assertIsNotNone(comment)
        self.assertIsNotNone(comment.sentiment_score)
        self.assertIsInstance(comment.sentiment_score, float)

    def test_invalid_comment_does_not_save(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        self.client.post(url, {"name": "", "email": "bad", "contents": ""})
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)

    def test_save_post(self):
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.post(url, {"save_post": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SavedPost.objects.filter(post=self.post).count(), 1)

    def test_unsave_post(self):
        SavedPost.objects.create(post=self.post, ip_address="127.0.0.1")
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        self.client.post(url, {"save_post": "1"})
        self.assertEqual(SavedPost.objects.filter(post=self.post).count(), 0)

    def test_only_approved_comments_shown(self):
        Comment.objects.create(post=self.post, name="A", email="a@a.com", contents="Approved", is_approved=True)
        Comment.objects.create(post=self.post, name="B", email="b@b.com", contents="Hidden", is_approved=False)
        url = reverse("blog:post_detail", kwargs={"category_slug": "tech", "post_slug": "my-post"})
        response = self.client.get(url)
        self.assertContains(response, "Approved")
        self.assertNotContains(response, "Hidden")


@override_settings(CACHES=NO_CACHE)
class CategoryDetailViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category("Tech", slug="tech")

    def test_returns_200(self):
        url = reverse("blog:category_detail", kwargs={"slug": "tech"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_uses_category_detail_template(self):
        url = reverse("blog:category_detail", kwargs={"slug": "tech"})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "category_detail.html")

    def test_returns_404_for_unknown_category(self):
        url = reverse("blog:category_detail", kwargs={"slug": "unknown"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_shows_only_active_posts_in_category(self):
        make_post(self.cat, title="Live Post", slug="live-post")
        make_post(self.cat, title="Draft Post", slug="draft-post", status=Post.DRAFT)
        url = reverse("blog:category_detail", kwargs={"slug": "tech"})
        response = self.client.get(url)
        self.assertContains(response, "Live Post")
        self.assertNotContains(response, "Draft Post")

    def test_category_in_context(self):
        url = reverse("blog:category_detail", kwargs={"slug": "tech"})
        response = self.client.get(url)
        self.assertEqual(response.context["category"], self.cat)

    def test_pagination(self):
        for i in range(15):
            make_post(self.cat, title=f"Post {i}", slug=f"cat-post-{i}")
        url = reverse("blog:category_detail", kwargs={"slug": "tech"})
        response = self.client.get(url)
        self.assertTrue(response.context["posts"].has_next())


@override_settings(CACHES=NO_CACHE)
class SearchViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category()

    def test_returns_200(self):
        response = self.client.get(reverse("blog:search"))
        self.assertEqual(response.status_code, 200)

    def test_uses_search_template(self):
        response = self.client.get(reverse("blog:search"))
        self.assertTemplateUsed(response, "search.html")

    def test_finds_post_by_title(self):
        make_post(self.cat, title="Unique Panda Story", slug="unique-panda-story")
        response = self.client.get(reverse("blog:search") + "?query=Panda")
        self.assertContains(response, "Unique Panda Story")

    def test_does_not_find_draft_posts(self):
        make_post(self.cat, title="Hidden Draft", slug="hidden-draft", status=Post.DRAFT)
        response = self.client.get(reverse("blog:search") + "?query=Hidden+Draft")
        self.assertNotContains(response, "/hidden-draft/")

    def test_query_in_context(self):
        response = self.client.get(reverse("blog:search") + "?query=hello")
        self.assertEqual(response.context["query"], "hello")

    def test_empty_query_returns_all_active(self):
        make_post(self.cat, title="Post A", slug="post-a")
        make_post(self.cat, title="Post B", slug="post-b")
        response = self.client.get(reverse("blog:search"))
        self.assertEqual(response.context["posts"].count(), 2)

    def test_finds_post_by_content(self):
        make_post(self.cat, title="Some Title", slug="some-title", content="content-keyword-xyz")
        response = self.client.get(reverse("blog:search") + "?query=content-keyword-xyz")
        self.assertContains(response, "Some Title")

    def test_finds_post_by_intro(self):
        make_post(self.cat, title="Intro Post", slug="intro-post", intro="intro-keyword-abc")
        response = self.client.get(reverse("blog:search") + "?query=intro-keyword-abc")
        self.assertContains(response, "Intro Post")


@override_settings(CACHES=NO_CACHE)
class NewsletterSignupViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category()

    def test_new_subscription_created(self):
        self.client.post(
            reverse("blog:newsletter_signup"),
            {"email": "subscriber@example.com"},
            HTTP_REFERER="http://testserver/",
        )
        self.assertTrue(Newsletter.objects.filter(email="subscriber@example.com").exists())

    def test_duplicate_subscription_not_created(self):
        Newsletter.objects.create(email="existing@example.com")
        self.client.post(
            reverse("blog:newsletter_signup"),
            {"email": "existing@example.com"},
            HTTP_REFERER="http://testserver/",
        )
        self.assertEqual(Newsletter.objects.filter(email="existing@example.com").count(), 1)

    def test_redirects_after_signup(self):
        response = self.client.post(
            reverse("blog:newsletter_signup"),
            {"email": "new@example.com"},
            HTTP_REFERER="http://testserver/",
        )
        self.assertEqual(response.status_code, 302)

    def test_invalid_email_not_saved(self):
        self.client.post(
            reverse("blog:newsletter_signup"),
            {"email": "not-an-email"},
            HTTP_REFERER="http://testserver/",
        )
        self.assertFalse(Newsletter.objects.filter(email="not-an-email").exists())

    def test_redirects_to_referer(self):
        response = self.client.post(
            reverse("blog:newsletter_signup"),
            {"email": "ref@example.com"},
            HTTP_REFERER="http://testserver/about/",
        )
        self.assertRedirects(response, "http://testserver/about/", fetch_redirect_response=False)


@override_settings(CACHES=NO_CACHE)
class RobotsTxtViewTests(TestCase):

    def test_returns_200(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)

    def test_content_type_text_plain(self):
        response = self.client.get("/robots.txt")
        self.assertIn("text/plain", response["Content-Type"])

    def test_contains_user_agent(self):
        response = self.client.get("/robots.txt")
        self.assertIn("User-agent", response.content.decode())

    def test_disallows_admin(self):
        response = self.client.get("/robots.txt")
        self.assertIn("/admin/", response.content.decode())
