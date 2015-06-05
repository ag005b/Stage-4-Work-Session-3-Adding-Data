import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


DEFAULT_SUBMISSION_NAME = 'Anonymous Submission'

# We set a parent key on the 'Comment' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.

def submission_key(submission_name=DEFAULT_SUBMISSION_NAME):
    """Constructs a Datastore key for a Comment entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Submission', submission_name)

# [START comment]
class Comment(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

# [END comment]

class Handler(webapp2.RequestHandler): 
    """
    Basic Handler; will be inherited by more specific path Handlers
    """
    def write(self, *a, **kw):
        "Write small strings to the website"
        self.response.out.write(*a, **kw)  

    def render_str(self, template, **params):  
        "Render jija2 templates"
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)   

    def render(self, template, **kw):
        "Write the jinja template to the website"
        self.write(self.render_str(template, **kw))


# [START main_page]
class MainPage(Handler):
    def get(self):
        submission_name = self.request.get('submission_name', DEFAULT_SUBMISSION_NAME)

        comments_query = Comment.query(
            ancestor=submission_key(submission_name)).order(-Comment.date)

        comments = comments_query.fetch(10)
#        self.render('notes.html')
        
        template_values = {
            'comment': comments_query,
            'submission_name': urllib.quote_plus(submission_name),
        }

        template = JINJA_ENVIRONMENT.get_template('notes.html')
        self.response.write(template.render(template_values))

# [END main_page]

# [START Comment Submission]
class Submission(webapp2.RequestHandler):
    def post(self):
        # We set a parent key on the 'Comment' to ensure that they are all
        # in the same entity group. Queries across the single entity group
        # will be consistent.  However, the write rate should be limited to
        # ~1/second. 
        submission_name = self.request.get('submission_name', DEFAULT_SUBMISSION_NAME)
        
        comment = Comment(parent=submission_key(submission_name))

        comment.content = self.request.get("content")
        comment.put()

        query_params = {'submission_name': submission_name}
        self.redirect('/?' + urllib.urlencode(query_params))

#[END Comment Submission]


app = webapp2.WSGIApplication([
    ('/', MainPage), 
    ('/submission', Submission),
], debug=True)


