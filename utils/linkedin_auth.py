import os
import json
from requests_oauthlib import OAuth2Session
import streamlit as st

class LinkedInOAuth:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = 'http://0.0.0.0:5000/callback'
        self.authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.scope = ['r_liteprofile', 'r_emailaddress']

    def get_auth_url(self):
        """Generate authorization URL"""
        linkedin = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
        authorization_url, state = linkedin.authorization_url(self.authorization_base_url)
        return authorization_url, state

    def fetch_token(self, authorization_response):
        """Exchange authorization code for access token"""
        linkedin = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)
        token = linkedin.fetch_token(
            self.token_url,
            client_secret=self.client_secret,
            authorization_response=authorization_response
        )
        return token

    def get_profile_data(self, token):
        """Fetch LinkedIn profile data"""
        linkedin = OAuth2Session(self.client_id, token=token)
        profile_url = 'https://api.linkedin.com/v2/me'
        email_url = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
        
        profile = linkedin.get(profile_url).json()
        email = linkedin.get(email_url).json()
        
        return {
            'firstName': profile.get('localizedFirstName', ''),
            'lastName': profile.get('localizedLastName', ''),
            'email': email.get('elements', [{}])[0].get('handle~', {}).get('emailAddress', '')
        }
