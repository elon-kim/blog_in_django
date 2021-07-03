from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag
from django.contrib.auth.models import User

# Create your tests here.


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_john1 = User.objects.create_user(username='john1', password='abdsdfsc@1')
        self.user_john2 = User.objects.create_user(username='john2', password='abdsdfsc@1')
        self.user_john1.is_staff = True
        self.user_john1.save()
        
        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')
        
        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')
        
        self.post_001 = Post.objects.create(
            title='첫 번째',
            content='Hello, world.',
            category=self.category_programming,
            author=self.user_john1,
        )
        self.post_001.tags.add(self.tag_hello)
        
        self.post_002 = Post.objects.create(
            title='두 번째',
            content='하나둘셋 파이팅!',
            category=self.category_music,
            author=self.user_john2,
        )
        
        self.post_003 = Post.objects.create(
            title='세 번째',
            content='카테고리 없음',
            author=self.user_john2,
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)
        
    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Navbar')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        
        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        
        self.assertIn(self.user_john1.username.upper(), main_area.text)
        self.assertIn(self.user_john2.username.upper(), main_area.text)

        # 포스트 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')
        
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.user_john1.username.upper(), post_area.text)
        self.assertIn(self.post_001.title, post_area.text)
        
        self.assertIn(self.category_programming.name, post_area.text)
        self.assertIn(self.post_001.content, post_area.text)
        
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        
    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        self.assertIn(self.category_programming.name, soup.h1.text)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
        
    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        self.assertIn(self.tag_hello.name, soup.h1.text)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
    
    def test_create_post(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        
        self.client.login(username='john2', password='abdsdfsc@1')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        
        self.client.login(username='john1', password='abdsdfsc@1')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        
        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)
        
        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'what a wonderful world',
                'content' : 'you too',
                'tags_str' : 'new tag; 한글 태그, python'
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, 'what a wonderful world')
        self.assertEqual(last_post.author.username, 'john1')
        
        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'
        
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)
        
        self.assertNotEqual(self.post_003.author, self.user_john1)
        self.client.login(
            username = 'john1',
            password = 'abdsdfsc@1',
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        self.client.login(
            username = 'john2',
            password = 'abdsdfsc@1',
        )
        response = self.client.get(update_post_url)
        self.assertEqual(self.post_003.author, self.user_john2)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)
        
        response = self.client.post(
            update_post_url,
            {
                'title' : '세 번째 포스트 수정',
                'content' : '안녕 자기 렛미쉑댓 부리',
                'category' : self.category_music.pk,
            },
            follow = True
        )
        
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트 수정', main_area.text)
        self.assertIn('안녕 자기 렛미쉑댓 부리', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        
        
    