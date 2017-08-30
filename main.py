# Author: Akshay Subramanian (ONID: subramaa)
# Assignment: OAuth 2.0 Implementation for Google+ Access
# CS 496 - 07/20/17

import webapp2
import logging
import json
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import urllib
import functools
import random, string
import os
from google.appengine.ext.webapp import template

#pages to create:

    # page with a link that a user creates to go to the Google OAuth 2.0 Endpoint
        # This is the client directing the user to the server that holds the access

#Following two pages will be the same - callback used to access the token and query the google plus API
    # page that handles the user getting redirected by the Google Endpoint
        # This is where the client must get the authorization code from the end-user that was provided by the server

    # page that uses the token that was generated to go get google+ information
        # This is the client using the token to access the authorized resource

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))


class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        def handle_result(rpc):
            #print "inside callback"
            stateVal = self.request.cookies.get('check')
            result = rpc.get_result()
            response = json.loads(result.content)
            token = response["access_token"]
            setHeaders = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
            resp = urlfetch.fetch(url="https://www.googleapis.com/plus/v1/people/me", payload=None, method="Get", headers=setHeaders, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=True)
            data = json.loads(resp.content)
            display = data["displayName"]
            fName = data["name"]["givenName"]
            lName = data["name"]["familyName"]
            url = data["url"]

            template_values = {
                'first': fName,
                'last': lName,
                'url': url,
                'state': stateVal
            }

            path = os.path.join(os.path.dirname(__file__), 'oauth.html')
            self.response.out.write(template.render("oauth.html", template_values))

        cookie_value = self.request.cookies.get('check')
        #self.response.write(cookie_value)
        responseState = self.request.get('state')
        if responseState != cookie_value:
            template_values = {
                'content': "WRONG STATE!"
            }
            path = os.path.join(os.path.dirname(__file__), 'oauth.html')
            self.response.out.write(template.render("oauth.html", template_values))
        else:
            #self.response.write(cooke_value)
            responseCode = self.request.get('code')
            setHeaders = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload_data = urllib.urlencode({'grant_type':'authorization_code',
                       "code":responseCode,
                       "client_id":"1054569871065-kqfacfjc2gb5jdur7vg26a4697mjflqr.apps.googleusercontent.com",
                       "client_secret":"Fs7VsigNkY6tLoYHZbC0-Lq9",
                       "redirect_uri":"https://oauth-496-project.appspot.com/OAuth"})
            rpc = urlfetch.create_rpc()
            rpc.callback = functools.partial(handle_result, rpc)
            urlfetch.make_fetch_call(rpc, url = "https://www.googleapis.com/oauth2/v4/token", payload = payload_data, method = urlfetch.POST, headers = setHeaders)
            rpc.wait()




class MainPage(webapp2.RequestHandler):
    def get(self):
        state = randomword(20)
        self.response.set_cookie('check', state, max_age=360, path='/OAuth',
                    domain='oauth-496-project.appspot.com', secure=True)
        link = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=1054569871065-kqfacfjc2gb5jdur7vg26a4697mjflqr.apps.googleusercontent.com&redirect_uri=https://oauth-496-project.appspot.com/OAuth&scope=email&state=" + state + "&access_type=offline"
        template_values = {
            'url': link,
            'url_linkText': "Click here for Authentication"
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render("index.html", template_values))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/OAuth', OAuthHandler)
], debug=True)
