from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin

KV = '''
Screen:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        MDTextField:
            id: url_input
            hint_text: "Enter URL"
            size_hint_x: None
            width: 300
            pos_hint: {"center_x": 0.5}
            mode: "rectangle"
            color_mode: 'accent'
            line_color_focus: 1, 0, 0, 1
            on_text_validate: app.scrape_website()

        MDRaisedButton:
            text: "Submit"
            pos_hint: {"center_x": 0.5}
            md_bg_color: app.theme_cls.primary_color
            on_release: app.scrape_website()

        GridLayout:
            id: info_grid
            cols: 1
            row_default_height: 40
            row_force_default: True
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(5)

        MDScrollView:
            id: scroll_view
            size_hint: (1, 1)
            BoxLayout:
                id: image_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                padding: dp(10)

'''

class WebsiteInfoApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)

    def scrape_website(self):
        url = self.root.ids.url_input.text
        if not url.startswith('http'):
            url = 'http://' + url

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else 'No title found'
            language = soup.find('html').get('lang', 'Unknown')
            domain = urlparse(url).netloc
            charset = response.encoding
            doctype = soup.contents[0] if isinstance(soup.contents[0], str) and soup.contents[0].startswith('<!DOCTYPE') else 'Unknown'
            images = soup.find_all('img')
            protocol = 'HTTPS' if url.startswith('https') else 'HTTP'
            internal_links = len([link for link in soup.find_all('a', href=True) if urlparse(link['href']).netloc == domain])
            
            favicon = None
            for link in soup.find_all('link', rel=True):
                if 'icon' in link.get('rel'):
                    favicon = urljoin(url, link.get('href'))
                    break

            info = [
                f"\n"
                f"Title: {title} \n",
                f"Language: {language}",
                f"Domain: {domain}",
                f"Charset: {charset}",
                f"Doctype: {doctype}",
                f"Images: {len(images)}",
                f"Protocol: {protocol}",
                f"Internal Links: {internal_links} \n",
                f"Favicon: {favicon if favicon else 'No favicon found'}"
            ]

            info_grid = self.root.ids.info_grid
            info_grid.clear_widgets()
            for item in info:
                info_grid.add_widget(MDLabel(text=item, halign='center', theme_text_color='Primary'))



            # Clear previous images
            image_box = self.root.ids.image_box
            image_box.clear_widgets()

            # Display favicon
            if favicon:
                image_box.add_widget(
                    AsyncImage(source=favicon, size_hint_y=None, height=100)
                )
            # Display images
            for img in images:
                img_url = img.get('src')
                if not img_url.startswith(('http', 'https')):
                    img_url = urljoin(url, img_url)
                image_box.add_widget(
                    AsyncImage(source=img_url, size_hint_y=None, height=200)
                )

        except Exception as e:
            self.root.ids.result_label.text = str(e)

if __name__ == '__main__':
    WebsiteInfoApp().run()
