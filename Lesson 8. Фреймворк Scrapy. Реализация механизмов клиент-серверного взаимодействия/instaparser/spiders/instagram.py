import json
import re
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy


class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1650388687:AUVQAPLsNiCtdG0b660bL/la/fAfzNJ0AaVNGPhAI7fwS9ANR85sT7Kjag60UVTeviSs34AXFch4cAYMc8Pq56W6i7ntwpu2ucSOa3aIY3LRVrPRqB2XvkxeB+KW6C2TQEPNVbnxpAqk8m4yOJg='
    parse_user = ['kuhlmann_offiziell', 'nstwrv']
    api_link_followers = 'https://i.instagram.com/api/v1/friendships/--/followers/?'
    api_link_following = 'https://i.instagram.com/api/v1/friendships/--/following/?'


    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login, 'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for parse in self.parse_user:
                yield response.follow(
                    f'/{parse}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': parse}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        api_link_followers = self.api_link_followers.replace('--', f'{user_id}')
        get_api_link_followers = f'{api_link_followers}count=12&search_surface=follow_list_page'

        api_link_following = self.api_link_following.replace('--', f'{user_id}')
        get_api_link_following = f'{api_link_following}count=12'

        yield response.follow(get_api_link_followers,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )
        yield response.follow(get_api_link_following,
                              callback=self.user_following_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

    def user_followers_parse(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        if j_data.get('next_max_id'):
            max_id = j_data.get('next_max_id')
            api_link_followers = self.api_link_followers.replace('--', f'{user_id}')
            get_api_link_followers = f'{api_link_followers}count=12&max_id={max_id}&search_surface=follow_list_page'
            yield response.follow(get_api_link_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

            followers = j_data.get('users')
            for follower in followers:
                item = InstaparserItem(
                    user_id=user_id,
                    username=username,
                    type_='followers',
                    pk_followers=follower.get('pk'),
                    name_followers=follower.get('username'),
                    full_name_followers=follower.get('full_name'),
                    followers_data=follower.get('users')
                )
                yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        if j_data.get('next_max_id'):
            max_id = j_data.get('next_max_id')
            api_link_following = self.api_link_following.replace('--', f'{user_id}')
            get_api_link_following = f'{api_link_following}count=12&max_id={max_id}'
            yield response.follow(get_api_link_following,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

            followings = j_data.get('users')
            for following in followings:
                item = InstaparserItem(
                    user_id=user_id,
                    username=username,
                    type_='following',
                    pk_following=following.get('pk'),
                    name_following=following.get('username'),
                    full_name_following=following.get('full_name'),
                    following_data=following.get('users')
                )
                yield item

    def fetch_csrf_token(self, text):
        """ Get csrf-token for auth """
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]