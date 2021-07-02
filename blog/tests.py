from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.contrib.auth.models import User

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_john1 = User.objects.create_user(username='john1', password='abdsdfsc@1')
        self.user_john2 = User.objects.create_user(username='john2', password='abdsdfsc@1')
    
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
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        
        self.navbar_test(soup)
        
        self.assertEqual(Post.objects.count(), 0)
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)
        
        post_001 = Post.objects.create(
            title='첫 번째',
            content='Hello, world.',
            author=self.user_john1,
        )
        post_002 = Post.objects.create(
            title='두 번째',
            content='하나둘셋 파이팅!',
            author=self.user_john2,
        )
        self.assertEqual(Post.objects.count(), 2)
        
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        
        self.assertIn(self.user_john1.username.upper(), main_area.text)
        self.assertIn(self.user_john2.username.upper(), main_area.text)
        
    def test_post_detail(self):
        post_001 = Post.objects.create(
            title='첫 번째',
            content='Hello, world.',
            author=self.user_john1
        )
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        
        self.assertIn(post_001.title, soup.title.text)
        
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.user_john1.username.upper(), post_area.text),
        self.assertIn(post_001.title, post_area.text)
        self.assertIn(post_001.content, post_area.text)
        