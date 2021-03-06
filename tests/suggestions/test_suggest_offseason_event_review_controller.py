import unittest2
import webapp2
import webtest

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from webapp2_extras.routes import RedirectRoute

from consts.account_permissions import AccountPermissions
from controllers.suggestions.suggest_offseason_event_review_controller import \
    SuggestOffseasonEventReviewController
from models.account import Account
from models.event import Event
from models.suggestion import Suggestion


class TestSuggestOffseasonEventReviewController(unittest2.TestCase):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_taskqueue_stub(_all_queues_valid=True)
        ndb.get_context().clear_cache()  # Prevent data from leaking between tests

        app = webapp2.WSGIApplication([
            RedirectRoute(r'/suggest/offseason/review', SuggestOffseasonEventReviewController, 'review-offseason', strict_slash=True),
        ], debug=True)
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    def loginUser(self):
        self.testbed.setup_env(
            user_email="user@example.com",
            user_id="123",
            user_is_admin='0',
            overwrite=True)

        self.account = Account.get_or_insert(
            "123",
            email="user@example.com",
            registered=True)

    def givePermission(self):
        self.account.permissions.append(AccountPermissions.REVIEW_OFFSEASON_EVENTS)
        self.account.put()

    def createSuggestion(self):
        from helpers.suggestions.suggestion_creator import SuggestionCreator
        status = SuggestionCreator.createOffseasonEventSuggestion(self.account.key,
                                                                  'Test Event',
                                                                  '2016-10-12',
                                                                  '2016-10-13',
                                                                  'http://foo.bar.com',
                                                                  'Venue Name',
                                                                  '123 Fake St',
                                                                  'New York',
                                                                  'NY',
                                                                  'USA')
        self.assertEqual(status[0], 'success')
        return Suggestion.query().fetch(keys_only=True)[0].id()

    def getSuggestionForm(self, suggestion_id):
        response = self.testapp.get('/suggest/offseason/review')
        self.assertEqual(response.status_int, 200)

        form = response.forms.get('review_{}'.format(suggestion_id), None)
        self.assertIsNotNone(form)
        return form

    def test_login_redirect(self):
        response = self.testapp.get('/suggest/offseason/review', status='3*')
        response = response.follow(expect_errors=True)
        self.assertTrue(response.request.path.startswith("/account/login_required"))

    def test_no_permissions(self):
        self.loginUser()
        response = self.testapp.get('/suggest/offseason/review', status='3*')
        response = response.follow(expect_errors=True)
        self.assertEqual(response.request.path, '/')

    def test_nothing_to_review(self):
        self.loginUser()
        self.givePermission()
        response = self.testapp.get('/suggest/offseason/review')
        self.assertEqual(response.status_int, 200)

    def test_accept_suggestion(self):
        self.loginUser()
        self.givePermission()
        suggestion_id = self.createSuggestion()
        form = self.getSuggestionForm(suggestion_id)

        form['event_short'] = 'test'
        response = form.submit('verdict', value='accept').follow()
        self.assertEqual(response.status_int, 200)

        suggestion = Suggestion.get_by_id(suggestion_id)
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.review_state, Suggestion.REVIEW_ACCEPTED)

        event = Event.get_by_id('2016test')
        self.assertIsNotNone(event)

    def test_reject_suggestion(self):
        self.loginUser()
        self.givePermission()
        suggestion_id = self.createSuggestion()
        form = self.getSuggestionForm(suggestion_id)

        form['event_short'] = 'test'
        response = form.submit('verdict', value='reject').follow()
        self.assertEqual(response.status_int, 200)

        suggestion = Suggestion.get_by_id(suggestion_id)
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.review_state, Suggestion.REVIEW_REJECTED)

        event = Event.get_by_id('2016test')
        self.assertIsNone(event)
