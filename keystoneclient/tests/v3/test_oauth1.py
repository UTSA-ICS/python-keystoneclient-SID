# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import httpretty
import six
from testtools import matchers

from keystoneclient.openstack.common import jsonutils
from keystoneclient.openstack.common import timeutils
from keystoneclient.tests.v3 import utils
from keystoneclient.v3.contrib.oauth1 import access_tokens
from keystoneclient.v3.contrib.oauth1 import consumers
from keystoneclient.v3.contrib.oauth1 import request_tokens

try:
    from oauthlib import oauth1
except ImportError:
    oauth1 = None


class BaseTest(utils.TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        if oauth1 is None:
            self.skipTest('oauthlib package not available')


class ConsumerTests(BaseTest, utils.CrudTests):
    def setUp(self):
        super(ConsumerTests, self).setUp()
        self.key = 'consumer'
        self.collection_key = 'consumers'
        self.model = consumers.Consumer
        self.manager = self.client.oauth1.consumers
        self.path_prefix = 'OS-OAUTH1'

    def new_ref(self, **kwargs):
        kwargs = super(ConsumerTests, self).new_ref(**kwargs)
        kwargs.setdefault('description', uuid.uuid4().hex)
        return kwargs

    @httpretty.activate
    def test_description_is_optional(self):
        consumer_id = uuid.uuid4().hex
        resp_ref = {'consumer': {'description': None,
                                 'id': consumer_id}}

        self.stub_url(httpretty.POST,
                      [self.path_prefix, self.collection_key],
                      status=201, json=resp_ref)

        consumer = self.manager.create()
        self.assertEqual(consumer_id, consumer.id)
        self.assertIsNone(consumer.description)

    @httpretty.activate
    def test_description_not_included(self):
        consumer_id = uuid.uuid4().hex
        resp_ref = {'consumer': {'id': consumer_id}}

        self.stub_url(httpretty.POST,
                      [self.path_prefix, self.collection_key],
                      status=201, json=resp_ref)

        consumer = self.manager.create()
        self.assertEqual(consumer_id, consumer.id)


class TokenTests(BaseTest):
    def _new_oauth_token(self):
        key = uuid.uuid4().hex
        secret = uuid.uuid4().hex
        token = 'oauth_token=%s&oauth_token_secret=%s' % (key, secret)
        return (key, secret, token)

    def _new_oauth_token_with_expires_at(self):
        key, secret, token = self._new_oauth_token()
        expires_at = timeutils.strtime()
        token += '&oauth_expires_at=%s' % expires_at
        return (key, secret, expires_at, token)

    def _validate_oauth_headers(self, auth_header, oauth_client):
        """Assert that the data in the headers matches the data
        that is produced from oauthlib.
        """

        self.assertThat(auth_header, matchers.StartsWith('OAuth '))
        auth_header = auth_header[len('OAuth '):]
        header_params = oauth_client.get_oauth_params()
        parameters = dict(header_params)

        self.assertEqual('HMAC-SHA1', parameters['oauth_signature_method'])
        self.assertEqual('1.0', parameters['oauth_version'])
        self.assertIsInstance(parameters['oauth_nonce'], six.string_types)
        self.assertEqual(oauth_client.client_key,
                         parameters['oauth_consumer_key'])
        if oauth_client.resource_owner_key:
            self.assertEqual(oauth_client.resource_owner_key,
                             parameters['oauth_token'],)
        if oauth_client.verifier:
            self.assertEqual(oauth_client.verifier,
                             parameters['oauth_verifier'])
        if oauth_client.callback_uri:
            self.assertEqual(oauth_client.callback_uri,
                             parameters['oauth_callback'])
        if oauth_client.timestamp:
            self.assertEqual(oauth_client.timestamp,
                             parameters['oauth_timestamp'])
        return parameters


class RequestTokenTests(TokenTests):
    def setUp(self):
        super(RequestTokenTests, self).setUp()
        self.model = request_tokens.RequestToken
        self.manager = self.client.oauth1.request_tokens
        self.path_prefix = 'OS-OAUTH1'

    @httpretty.activate
    def test_authorize_request_token(self):
        request_key = uuid.uuid4().hex
        info = {'id': request_key,
                'key': request_key,
                'secret': uuid.uuid4().hex}
        request_token = request_tokens.RequestToken(self.manager, info)

        verifier = uuid.uuid4().hex
        resp_ref = {'token': {'oauth_verifier': verifier}}
        self.stub_url(httpretty.PUT,
                      [self.path_prefix, 'authorize', request_key],
                      status=200, json=resp_ref)

        # Assert the manager is returning the expected data
        role_id = uuid.uuid4().hex
        token = request_token.authorize([role_id])
        self.assertEqual(verifier, token.oauth_verifier)

        # Assert that the request was sent in the expected structure
        exp_body = {'roles': [{'id': role_id}]}
        self.assertRequestBodyIs(json=exp_body)

    @httpretty.activate
    def test_create_request_token(self):
        project_id = uuid.uuid4().hex
        consumer_key = uuid.uuid4().hex
        consumer_secret = uuid.uuid4().hex

        request_key, request_secret, resp_ref = self._new_oauth_token()

        # NOTE(stevemar) The server expects the body to be JSON. Even though
        # the resp_ref is a string it is not a JSON string.
        self.stub_url(httpretty.POST, [self.path_prefix, 'request_token'],
                      status=201, body=jsonutils.dumps(resp_ref),
                      content_type='application/x-www-form-urlencoded')

        # Assert the manager is returning request token object
        request_token = self.manager.create(consumer_key, consumer_secret,
                                            project_id)
        self.assertIsInstance(request_token, self.model)
        self.assertEqual(request_key, request_token.key)
        self.assertEqual(request_secret, request_token.secret)

        # Assert that the project id is in the header
        self.assertRequestHeaderEqual('requested_project_id', project_id)
        req_headers = httpretty.last_request().headers

        oauth_client = oauth1.Client(consumer_key,
                                     client_secret=consumer_secret,
                                     signature_method=oauth1.SIGNATURE_HMAC,
                                     callback_uri="oob")
        self._validate_oauth_headers(req_headers['Authorization'],
                                     oauth_client)


class AccessTokenTests(TokenTests):
    def setUp(self):
        super(AccessTokenTests, self).setUp()
        self.manager = self.client.oauth1.access_tokens
        self.model = access_tokens.AccessToken
        self.path_prefix = 'OS-OAUTH1'

    @httpretty.activate
    def test_create_access_token_expires_at(self):
        verifier = uuid.uuid4().hex
        consumer_key = uuid.uuid4().hex
        consumer_secret = uuid.uuid4().hex
        request_key = uuid.uuid4().hex
        request_secret = uuid.uuid4().hex

        t = self._new_oauth_token_with_expires_at()
        access_key, access_secret, expires_at, resp_ref = t

        # NOTE(stevemar) The server expects the body to be JSON. Even though
        # the resp_ref is a string it is not a JSON string.
        self.stub_url(httpretty.POST, [self.path_prefix, 'access_token'],
                      status=201, body=jsonutils.dumps(resp_ref),
                      content_type='application/x-www-form-urlencoded')

        # Assert that the manager creates an access token object
        access_token = self.manager.create(consumer_key, consumer_secret,
                                           request_key, request_secret,
                                           verifier)
        self.assertIsInstance(access_token, self.model)
        self.assertEqual(access_key, access_token.key)
        self.assertEqual(access_secret, access_token.secret)
        self.assertEqual(expires_at, access_token.expires)

        req_headers = httpretty.last_request().headers
        oauth_client = oauth1.Client(consumer_key,
                                     client_secret=consumer_secret,
                                     resource_owner_key=request_key,
                                     resource_owner_secret=request_secret,
                                     signature_method=oauth1.SIGNATURE_HMAC,
                                     verifier=verifier,
                                     timestamp=expires_at)
        self._validate_oauth_headers(req_headers['Authorization'],
                                     oauth_client)
