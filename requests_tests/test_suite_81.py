# -*- coding: utf-8 -*-

"""Tests for Requests."""

from __future__ import division
import json
import os
import pickle
import collections
import contextlib
import warnings

import io
import requests
import pytest
from requests.adapters import HTTPAdapter
from requests.auth import HTTPDigestAuth, _basic_auth_str
from requests.compat import (
    Morsel, cookielib, getproxies, str, urlparse,
    builtin_str, OrderedDict)
from requests.cookies import (
    cookiejar_from_dict, morsel_to_cookie)
from requests.exceptions import (
    ConnectionError, ConnectTimeout, InvalidSchema, InvalidURL,
    MissingSchema, ReadTimeout, Timeout, RetryError, TooManyRedirects,
    ProxyError, InvalidHeader, UnrewindableBodyError, SSLError)
from requests.models import PreparedRequest
from requests.structures import CaseInsensitiveDict
from requests.sessions import SessionRedirectMixin
from requests.models import urlencode
from requests.hooks import default_hooks

# from .compat import StringIO, u
# from .utils import override_environ
from urllib3.util import Timeout as Urllib3Timeout

# Requests to this URL should always fail with a connection timeout (nothing
# listening on that port)
TARPIT = 'http://10.255.255.1'

try:
    from ssl import SSLContext
    del SSLContext
    HAS_MODERN_SSL = True
except ImportError:
    HAS_MODERN_SSL = False

try:
    requests.pyopenssl
    HAS_PYOPENSSL = True
except AttributeError:
    HAS_PYOPENSSL = False

# -*- coding: utf-8 -*-

import threading
import socket
import time

import pytest
import requests
from testserver.server import Server

# -*- coding: utf-8 -*-

import pytest

from requests.structures import CaseInsensitiveDict, LookupDict

# -*- coding: utf-8 -*-

import os
import copy
from io import BytesIO

import pytest
from requests import compat
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict
from requests.utils import (
    address_in_network, dotted_netmask,
    get_auth_from_url, get_encoding_from_headers,
    get_encodings_from_content, get_environ_proxies,
    guess_filename, guess_json_utf, is_ipv4_address,
    is_valid_cidr, iter_slices, parse_dict_header,
    parse_header_links, prepend_scheme_if_needed,
    requote_uri, select_proxy, should_bypass_proxies, super_len,
    to_key_val_list, to_native_string,
    unquote_header_value, unquote_unreserved,
    urldefragauth, add_dict_to_cookiejar, set_environ)
from requests._internal_utils import unicode_is_ascii


# -*- encoding: utf-8

import sys

import pytest

from requests.help import info


class TestSuperLen:



    @pytest.mark.parametrize('error', [IOError, OSError])
    def test_super_len_handles_files_raising_weird_errors_in_tell(self, error):
        """If tell() raises errors, assume the cursor is at position zero."""
        class BoomFile(object):
            def __len__(self):
                return 5

            def tell(self):
                raise error()

        assert super_len(BoomFile()) == 0

    @pytest.mark.parametrize('error', [IOError, OSError])
    def test_super_len_tell_ioerror(self, error):
        """Ensure that if tell gives an IOError super_len doesn't fail"""
        class NoLenBoomFile(object):
            def tell(self):
                raise error()

            def seek(self, offset, whence):
                pass

        assert super_len(NoLenBoomFile()) == 0

    def test_string(self):
        assert super_len('Test') == 4

    @pytest.mark.parametrize(
        'mode, warnings_num', (
            ('r', 1),
            ('rb', 0),
        ))
    def test_file(self, tmpdir, mode, warnings_num, recwarn):
        file_obj = tmpdir.join('test.txt')
        file_obj.write('Test')
        with file_obj.open(mode) as fd:
            assert super_len(fd) == 4
        assert len(recwarn) == warnings_num

    def test_super_len_with__len__(self):
        foo = [1,2,3,4]
        len_foo = super_len(foo)
        assert len_foo == 4

    def test_super_len_with_no__len__(self):
        class LenFile(object):
            def __init__(self):
                self.len = 5

        assert super_len(LenFile()) == 5



    def test_super_len_with_fileno(self):
        with open(__file__, 'rb') as f:
            length = super_len(f)
            file_data = f.read()
        assert length == len(file_data)

    def test_super_len_with_no_matches(self):
        """Ensure that objects without any length methods default to 0"""
        assert super_len(object()) == 0


class TestSuperLen:



    @pytest.mark.parametrize('error', [IOError, OSError])
    def test_super_len_handles_files_raising_weird_errors_in_tell(self, error):
        """If tell() raises errors, assume the cursor is at position zero."""
        class BoomFile(object):
            def __len__(self):
                return 5

            def tell(self):
                raise error()

        assert super_len(BoomFile()) == 0

    @pytest.mark.parametrize('error', [IOError, OSError])
    def test_super_len_tell_ioerror(self, error):
        """Ensure that if tell gives an IOError super_len doesn't fail"""
        class NoLenBoomFile(object):
            def tell(self):
                raise error()

            def seek(self, offset, whence):
                pass

        assert super_len(NoLenBoomFile()) == 0

    def test_string(self):
        assert super_len('Test') == 4

    @pytest.mark.parametrize(
        'mode, warnings_num', (
            ('r', 1),
            ('rb', 0),
        ))
    def test_file(self, tmpdir, mode, warnings_num, recwarn):
        file_obj = tmpdir.join('test.txt')
        file_obj.write('Test')
        with file_obj.open(mode) as fd:
            assert super_len(fd) == 4
        assert len(recwarn) == warnings_num

    def test_super_len_with__len__(self):
        foo = [1,2,3,4]
        len_foo = super_len(foo)
        assert len_foo == 4

    def test_super_len_with_no__len__(self):
        class LenFile(object):
            def __init__(self):
                self.len = 5

        assert super_len(LenFile()) == 5



    def test_super_len_with_fileno(self):
        with open(__file__, 'rb') as f:
            length = super_len(f)
            file_data = f.read()
        assert length == len(file_data)

    def test_super_len_with_no_matches(self):
        """Ensure that objects without any length methods default to 0"""
        assert super_len(object()) == 0


class TestTimeout:

    def test_stream_timeout(self, httpbin):
        try:
            requests.get(httpbin('delay/10'), timeout=2.0)
        except requests.exceptions.Timeout as e:
            assert 'Read timed out' in e.args[0].args[0]

    @pytest.mark.parametrize(
        'timeout, error_text', (
            ((3, 4, 5), '(connect, read)'),
            ('foo', 'must be an int, float or None'),
        ))
    def test_invalid_timeout(self, httpbin, timeout, error_text):
        with pytest.raises(ValueError) as e:
            requests.get(httpbin('get'), timeout=timeout)
        assert error_text in str(e)

    @pytest.mark.parametrize(
        'timeout', (
            None,
            Urllib3Timeout(connect=None, read=None)
        ))
    def test_none_timeout(self, httpbin, timeout):
        """Check that you can set None as a valid timeout value.

        To actually test this behavior, we'd want to check that setting the
        timeout to None actually lets the request block past the system default
        timeout. However, this would make the test suite unbearably slow.
        Instead we verify that setting the timeout to None does not prevent the
        request from succeeding.
        """
        r = requests.get(httpbin('get'), timeout=timeout)
        assert r.status_code == 200

    @pytest.mark.parametrize(
        'timeout', (
            (None, 0.1),
            Urllib3Timeout(connect=None, read=0.1)
        ))
    def test_read_timeout(self, httpbin, timeout):
        try:
            requests.get(httpbin('delay/10'), timeout=timeout)
            pytest.fail('The recv() request should time out.')
        except ReadTimeout:
            pass

    @pytest.mark.parametrize(
        'timeout', (
            (0.1, None),
            Urllib3Timeout(connect=0.1, read=None)
        ))
    def test_connect_timeout(self, timeout):
        try:
            requests.get(TARPIT, timeout=timeout)
            pytest.fail('The connect() request should time out.')
        except ConnectTimeout as e:
            assert isinstance(e, ConnectionError)
            assert isinstance(e, Timeout)

    @pytest.mark.parametrize(
        'timeout', (
            (0.1, 0.1),
            Urllib3Timeout(connect=0.1, read=0.1)
        ))
    def test_total_timeout_connect(self, timeout):
        try:
            requests.get(TARPIT, timeout=timeout)
            pytest.fail('The connect() request should time out.')
        except ConnectTimeout:
            pass

    def test_encoded_methods(self, httpbin):
        """See: https://github.com/requests/requests/issues/2316"""
        r = requests.request(b'GET', httpbin('get'))
        assert r.ok


SendCall = collections.namedtuple('SendCall', ('args', 'kwargs'))



def test_json_encodes_as_bytes():
    # urllib3 expects bodies as bytes-like objects
    body = {"key": "value"}
    p = PreparedRequest()
    p.prepare(
        method='GET',
        url='https://www.example.com/',
        json=body
    )
    assert isinstance(p.body, bytes)


def test_requests_are_updated_each_time(httpbin):
    session = RedirectSession([303, 307])
    prep = requests.Request('POST', httpbin('post')).prepare()
    r0 = session.send(prep)
    assert r0.request.method == 'POST'
    assert session.calls[-1] == SendCall((r0.request,), {})
    redirect_generator = session.resolve_redirects(r0, prep)
    default_keyword_args = {
        'stream': False,
        'verify': True,
        'cert': None,
        'timeout': None,
        'allow_redirects': False,
        'proxies': {},
    }
    for response in redirect_generator:
        assert response.request.method == 'GET'
        send_call = SendCall((response.request,), default_keyword_args)
        assert session.calls[-1] == send_call


# @pytest.mark.parametrize("var,url,proxy", [
#     ('http_proxy', 'http://example.com', 'socks5://proxy.com:9876'),
#     ('https_proxy', 'https://example.com', 'socks5://proxy.com:9876'),
#     ('all_proxy', 'http://example.com', 'socks5://proxy.com:9876'),
#     ('all_proxy', 'https://example.com', 'socks5://proxy.com:9876'),
# ])
# def test_proxy_env_vars_override_default(var, url, proxy):
#     session = requests.Session()
#     prep = PreparedRequest()
#     prep.prepare(method='GET', url=url)
#
#     kwargs = {
#         var: proxy
#     }
#     scheme = urlparse(url).scheme
#     with override_environ(**kwargs):
#         proxies = session.rebuild_proxies(prep, {})
#         assert scheme in proxies
#         assert proxies[scheme] == proxy


@pytest.mark.parametrize(
    'data', (
        (('a', 'b'), ('c', 'd')),
        (('c', 'd'), ('a', 'b')),
        (('a', 'b'), ('c', 'd'), ('e', 'f')),
    ))
def test_data_argument_accepts_tuples(data):
    """Ensure that the data argument will accept tuples of strings
    and properly encode them.
    """
    p = PreparedRequest()
    p.prepare(
        method='GET',
        url='http://www.example.com',
        data=data,
        hooks=default_hooks()
    )
    assert p.body == urlencode(data)


# @pytest.mark.parametrize(
#     'kwargs', (
#         None,
#         {
#             'method': 'GET',
#             'url': 'http://www.example.com',
#             'data': 'foo=bar',
#             'hooks': default_hooks()
#         },
#         {
#             'method': 'GET',
#             'url': 'http://www.example.com',
#             'data': 'foo=bar',
#             'hooks': default_hooks(),
#             'cookies': {'foo': 'bar'}
#         },
#         {
#             'method': 'GET',
#             'url': u('http://www.example.com/üniçø∂é')
#         },
#     ))
# def test_prepared_copy(kwargs):
#     p = PreparedRequest()
#     if kwargs:
#         p.prepare(**kwargs)
#     copy = p.copy()
#     for attr in ('method', 'url', 'headers', '_cookies', 'body', 'hooks'):
#         assert getattr(p, attr) == getattr(copy, attr)


def test_urllib3_retries(httpbin):
    from urllib3.util import Retry
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=Retry(
        total=2, status_forcelist=[500]
    )))

    with pytest.raises(RetryError):
        s.get(httpbin('status/500'))


# def test_urllib3_pool_connection_closed(httpbin):
#     s = requests.Session()
#     s.mount('http://', HTTPAdapter(pool_connections=0, pool_maxsize=0))
#
#     try:
#         s.get(httpbin('status/200'))
#     except ConnectionError as e:
#         assert u"Pool is closed." in str(e)


# class TestPreparingURLs(object):
#     @pytest.mark.parametrize(
#         'url,expected',
#         (
#             ('http://google.com', 'http://google.com/'),
#             (u'http://ジェーピーニック.jp', u'http://xn--hckqz9bzb1cyrb.jp/'),
#             (u'http://xn--n3h.net/', u'http://xn--n3h.net/'),
#             (
#                 u'http://ジェーピーニック.jp'.encode('utf-8'),
#                 u'http://xn--hckqz9bzb1cyrb.jp/'
#             ),
#             (
#                 u'http://straße.de/straße',
#                 u'http://xn--strae-oqa.de/stra%C3%9Fe'
#             ),
#             (
#                 u'http://straße.de/straße'.encode('utf-8'),
#                 u'http://xn--strae-oqa.de/stra%C3%9Fe'
#             ),
#             (
#                 u'http://Königsgäßchen.de/straße',
#                 u'http://xn--knigsgchen-b4a3dun.de/stra%C3%9Fe'
#             ),
#             (
#                 u'http://Königsgäßchen.de/straße'.encode('utf-8'),
#                 u'http://xn--knigsgchen-b4a3dun.de/stra%C3%9Fe'
#             ),
#             (
#                 b'http://xn--n3h.net/',
#                 u'http://xn--n3h.net/'
#             ),
#             (
#                 b'http://[1200:0000:ab00:1234:0000:2552:7777:1313]:12345/',
#                 u'http://[1200:0000:ab00:1234:0000:2552:7777:1313]:12345/'
#             ),
#             (
#                 u'http://[1200:0000:ab00:1234:0000:2552:7777:1313]:12345/',
#                 u'http://[1200:0000:ab00:1234:0000:2552:7777:1313]:12345/'
#             )
#         )
#     )
#     def test_preparing_url(self, url, expected):
#         r = requests.Request('GET', url=url)
#         p = r.prepare()
#         assert p.url == expected

    # @pytest.mark.parametrize(
    #     'url',
    #     (
    #         b"http://*.google.com",
    #         b"http://*",
    #         u"http://*.google.com",
    #         u"http://*",
    #         u"http://☃.net/"
    #     )
    # )
    # def test_preparing_bad_url(self, url):
    #     r = requests.Request('GET', url=url)
    #     with pytest.raises(requests.exceptions.InvalidURL):
    #         r.prepare()

    # @pytest.mark.parametrize(
    #     'input, expected',
    #     (
    #         (
    #             b"http+unix://%2Fvar%2Frun%2Fsocket/path%7E",
    #             u"http+unix://%2Fvar%2Frun%2Fsocket/path~",
    #         ),
    #         (
    #             u"http+unix://%2Fvar%2Frun%2Fsocket/path%7E",
    #             u"http+unix://%2Fvar%2Frun%2Fsocket/path~",
    #         ),
    #         (
    #             b"mailto:user@example.org",
    #             u"mailto:user@example.org",
    #         ),
    #         (
    #             u"mailto:user@example.org",
    #             u"mailto:user@example.org",
    #         ),
    #         (
    #             b"data:SSDimaUgUHl0aG9uIQ==",
    #             u"data:SSDimaUgUHl0aG9uIQ==",
    #         )
    #     )
    # )
    # def test_url_mutation(self, input, expected):
    #     """
    #     This test validates that we correctly exclude some URLs from
    #     preparation, and that we handle others. Specifically, it tests that
    #     any URL whose scheme doesn't begin with "http" is left alone, and
    #     those whose scheme *does* begin with "http" are mutated.
    #     """
    #     r = requests.Request('GET', url=input)
    #     p = r.prepare()
    #     assert p.url == expected

    # @pytest.mark.parametrize(
    #     'input, params, expected',
    #     (
    #         (
    #             b"http+unix://%2Fvar%2Frun%2Fsocket/path",
    #             {"key": "value"},
    #             u"http+unix://%2Fvar%2Frun%2Fsocket/path?key=value",
    #         ),
    #         (
    #             u"http+unix://%2Fvar%2Frun%2Fsocket/path",
    #             {"key": "value"},
    #             u"http+unix://%2Fvar%2Frun%2Fsocket/path?key=value",
    #         ),
    #         (
    #             b"mailto:user@example.org",
    #             {"key": "value"},
    #             u"mailto:user@example.org",
    #         ),
    #         (
    #             u"mailto:user@example.org",
    #             {"key": "value"},
    #             u"mailto:user@example.org",
    #         ),
    #     )
    # )
    # def test_parameters_for_nonstandard_schemes(self, input, params, expected):
    #     """
    #     Setting parameters for nonstandard schemes is allowed if those schemes
    #     begin with "http", and is forbidden otherwise.
    #     """
    #     r = requests.Request('GET', url=input, params=params)
    #     p = r.prepare()
    #     assert p.url == expected

def test_can_access_idna_attribute():
    requests.packages.idna


def test_default_hooks():
    assert hooks.default_hooks() == {'response': []}

def test_default_hooks():
    assert hooks.default_hooks() == {'response': []}

class VersionedPackage(object):
    def __init__(self, version):
        self.__version__ = version

def test_redirect_rfc1808_to_non_ascii_location():
    path = u'š'
    expected_path = b'%C5%A1'
    redirect_request = []  # stores the second request to the server

    def redirect_resp_handler(sock):
        consume_socket_content(sock, timeout=0.5)
        location = u'//{0}:{1}/{2}'.format(host, port, path)
        sock.send(
            b'HTTP/1.1 301 Moved Permanently\r\n'
            b'Content-Length: 0\r\n'
            b'Location: ' + location.encode('utf8') + b'\r\n'
            b'\r\n'
        )
        redirect_request.append(consume_socket_content(sock, timeout=0.5))
        sock.send(b'HTTP/1.1 200 OK\r\n\r\n')

    close_server = threading.Event()
    server = Server(redirect_resp_handler, wait_to_close_event=close_server)

    with server as (host, port):
        url = u'http://{0}:{1}'.format(host, port)
        r = requests.get(url=url, allow_redirects=True)
        assert r.status_code == 200
        assert len(r.history) == 1
        assert r.history[0].status_code == 301
        assert redirect_request[0].startswith(b'GET /' + expected_path + b' HTTP/1.1')
        assert r.url == u'{0}/{1}'.format(url, expected_path.decode('ascii'))

        close_server.set()

class TestMorselToCookieMaxAge:

    """Tests for morsel_to_cookie when morsel contains max-age."""

    def test_max_age_valid_int(self):
        """Test case where a valid max age in seconds is passed."""

        morsel = Morsel()
        morsel['max-age'] = 60
        cookie = morsel_to_cookie(morsel)
        assert isinstance(cookie.expires, int)

    def test_max_age_invalid_str(self):
        """Test case where a invalid max age is passed."""

        morsel = Morsel()
        morsel['max-age'] = 'woops'
        with pytest.raises(TypeError):
            morsel_to_cookie(morsel)


def test_redirect_rfc1808_to_non_ascii_location():
    path = u'š'
    expected_path = b'%C5%A1'
    redirect_request = []  # stores the second request to the server

    def redirect_resp_handler(sock):
        consume_socket_content(sock, timeout=0.5)
        location = u'//{0}:{1}/{2}'.format(host, port, path)
        sock.send(
            b'HTTP/1.1 301 Moved Permanently\r\n'
            b'Content-Length: 0\r\n'
            b'Location: ' + location.encode('utf8') + b'\r\n'
            b'\r\n'
        )
        redirect_request.append(consume_socket_content(sock, timeout=0.5))
        sock.send(b'HTTP/1.1 200 OK\r\n\r\n')

    close_server = threading.Event()
    server = Server(redirect_resp_handler, wait_to_close_event=close_server)

    with server as (host, port):
        url = u'http://{0}:{1}'.format(host, port)
        r = requests.get(url=url, allow_redirects=True)
        assert r.status_code == 200
        assert len(r.history) == 1
        assert r.history[0].status_code == 301
        assert redirect_request[0].startswith(b'GET /' + expected_path + b' HTTP/1.1')
        assert r.url == u'{0}/{1}'.format(url, expected_path.decode('ascii'))

        close_server.set()

class TestMorselToCookieMaxAge:

    """Tests for morsel_to_cookie when morsel contains max-age."""

    def test_max_age_valid_int(self):
        """Test case where a valid max age in seconds is passed."""

        morsel = Morsel()
        morsel['max-age'] = 60
        cookie = morsel_to_cookie(morsel)
        assert isinstance(cookie.expires, int)

    def test_max_age_invalid_str(self):
        """Test case where a invalid max age is passed."""

        morsel = Morsel()
        morsel['max-age'] = 'woops'
        with pytest.raises(TypeError):
            morsel_to_cookie(morsel)


class TestMorselToCookieExpires:
    """Tests for morsel_to_cookie when morsel contains expires."""

    def test_expires_valid_str(self):
        """Test case where we convert expires from string time."""

        morsel = Morsel()
        morsel['expires'] = 'Thu, 01-Jan-1970 00:00:01 GMT'
        cookie = morsel_to_cookie(morsel)
        assert cookie.expires == 1

    @pytest.mark.parametrize(
        'value, exception', (
            (100, TypeError),
            ('woops', ValueError),
        ))
    def test_expires_invalid_int(self, value, exception):
        """Test case where an invalid type is passed for expires."""
        morsel = Morsel()
        morsel['expires'] = value
        with pytest.raises(exception):
            morsel_to_cookie(morsel)

    def test_expires_none(self):
        """Test case where expires is None."""

        morsel = Morsel()
        morsel['expires'] = None
        cookie = morsel_to_cookie(morsel)
        assert cookie.expires is None


class TestGuessJSONUTF:

    @pytest.mark.parametrize(
        'encoding', (
            'utf-32', 'utf-8-sig', 'utf-16', 'utf-8', 'utf-16-be', 'utf-16-le',
            'utf-32-be', 'utf-32-le'
        ))
    def test_encoded(self, encoding):
        data = '{}'.encode(encoding)
        assert guess_json_utf(data) == encoding

    def test_bad_utf_like_encoding(self):
        assert guess_json_utf(b'\x00\x00\x00\x00') is None

    @pytest.mark.parametrize(
        ('encoding', 'expected'), (
            ('utf-16-be', 'utf-16'),
            ('utf-16-le', 'utf-16'),
            ('utf-32-be', 'utf-32'),
            ('utf-32-le', 'utf-32')
        ))
    def test_guess_by_bom(self, encoding, expected):
        data = u'\ufeff{}'.encode(encoding)
        assert guess_json_utf(data) == expected


USER = PASSWORD = "%!*'();:@&=+$,/?#[] "
ENCODED_USER = compat.quote(USER, '')
ENCODED_PASSWORD = compat.quote(PASSWORD, '')


@pytest.mark.parametrize(
    'url, auth', (
        (
            'http://' + ENCODED_USER + ':' + ENCODED_PASSWORD + '@' +
            'request.com/url.html#test',
            (USER, PASSWORD)
        ),
        (
            'http://user:pass@complex.url.com/path?query=yes',
            ('user', 'pass')
        ),
        (
            'http://user:pass%20pass@complex.url.com/path?query=yes',
            ('user', 'pass pass')
        ),
        (
            'http://user:pass pass@complex.url.com/path?query=yes',
            ('user', 'pass pass')
        ),
        (
            'http://user%25user:pass@complex.url.com/path?query=yes',
            ('user%user', 'pass')
        ),
        (
            'http://user:pass%23pass@complex.url.com/path?query=yes',
            ('user', 'pass#pass')
        ),
        (
            'http://complex.url.com/path?query=yes',
            ('', '')
        ),
    ))
def test_get_auth_from_url(url, auth):
    assert get_auth_from_url(url) == auth


@pytest.mark.parametrize(
    'uri, expected', (
        (
            # Ensure requoting doesn't break expectations
            'http://example.com/fiz?buz=%25ppicture',
            'http://example.com/fiz?buz=%25ppicture',
        ),
        (
            # Ensure we handle unquoted percent signs in redirects
            'http://example.com/fiz?buz=%ppicture',
            'http://example.com/fiz?buz=%25ppicture',
        ),
    ))
def test_requote_uri_with_unquoted_percents(uri, expected):
    """See: https://github.com/requests/requests/issues/2356"""
    assert requote_uri(uri) == expected


@pytest.mark.parametrize(
    'uri, expected', (
        (
            # Illegal bytes
            'http://example.com/?a=%--',
            'http://example.com/?a=%--',
        ),
        (
            # Reserved characters
            'http://example.com/?a=%300',
            'http://example.com/?a=00',
        )
    ))
def test_unquote_unreserved(uri, expected):
    assert unquote_unreserved(uri) == expected


@pytest.mark.parametrize(
    'mask, expected', (
        (8, '255.0.0.0'),
        (24, '255.255.255.0'),
        (25, '255.255.255.128'),
    ))
def test_dotted_netmask(mask, expected):
    assert dotted_netmask(mask) == expected


http_proxies = {'http': 'http://http.proxy',
                'http://some.host': 'http://some.host.proxy'}
all_proxies = {'all': 'socks5://http.proxy',
               'all://some.host': 'socks5://some.host.proxy'}
mixed_proxies = {'http': 'http://http.proxy',
                 'http://some.host': 'http://some.host.proxy',
                 'all': 'socks5://http.proxy'}
@pytest.mark.parametrize(
    'url, expected, proxies', (
        ('hTTp://u:p@Some.Host/path', 'http://some.host.proxy', http_proxies),
        ('hTTp://u:p@Other.Host/path', 'http://http.proxy', http_proxies),
        ('hTTp:///path', 'http://http.proxy', http_proxies),
        ('hTTps://Other.Host', None, http_proxies),
        ('file:///etc/motd', None, http_proxies),

        ('hTTp://u:p@Some.Host/path', 'socks5://some.host.proxy', all_proxies),
        ('hTTp://u:p@Other.Host/path', 'socks5://http.proxy', all_proxies),
        ('hTTp:///path', 'socks5://http.proxy', all_proxies),
        ('hTTps://Other.Host', 'socks5://http.proxy', all_proxies),

        ('http://u:p@other.host/path', 'http://http.proxy', mixed_proxies),
        ('http://u:p@some.host/path', 'http://some.host.proxy', mixed_proxies),
        ('https://u:p@other.host/path', 'socks5://http.proxy', mixed_proxies),
        ('https://u:p@some.host/path', 'socks5://http.proxy', mixed_proxies),
        ('https://', 'socks5://http.proxy', mixed_proxies),
        # XXX: unsure whether this is reasonable behavior
        ('file:///etc/motd', 'socks5://http.proxy', all_proxies),
    ))
def test_select_proxies(url, expected, proxies):
    """Make sure we can select per-host proxies correctly."""
    assert select_proxy(url, proxies) == expected


@pytest.mark.parametrize(
    'value, expected', (
        ('foo="is a fish", bar="as well"', {'foo': 'is a fish', 'bar': 'as well'}),
        ('key_without_value', {'key_without_value': None})
    ))
def test_parse_dict_header(value, expected):
    assert parse_dict_header(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        (
            CaseInsensitiveDict(),
            None
        ),
        (
            CaseInsensitiveDict({'content-type': 'application/json; charset=utf-8'}),
            'utf-8'
        ),
        (
            CaseInsensitiveDict({'content-type': 'text/plain'}),
            'ISO-8859-1'
        ),
    ))
def test_get_encoding_from_headers(value, expected):
    assert get_encoding_from_headers(value) == expected


@pytest.mark.parametrize(
    'value, length', (
        ('', 0),
        ('T', 1),
        ('Test', 4),
        ('Cont', 0),
        ('Other', -5),
        ('Content', None),
    ))
def test_iter_slices(value, length):
    if length is None or (length <= 0 and len(value) > 0):
        # Reads all content at once
        assert len(list(iter_slices(value, length))) == 1
    else:
        assert len(list(iter_slices(value, 1))) == length


@pytest.mark.parametrize(
    'value, expected', (
        (
            '<http:/.../front.jpeg>; rel=front; type="image/jpeg"',
            [{'url': 'http:/.../front.jpeg', 'rel': 'front', 'type': 'image/jpeg'}]
        ),
        (
            '<http:/.../front.jpeg>',
            [{'url': 'http:/.../front.jpeg'}]
        ),
        (
            '<http:/.../front.jpeg>;',
            [{'url': 'http:/.../front.jpeg'}]
        ),
        (
            '<http:/.../front.jpeg>; type="image/jpeg",<http://.../back.jpeg>;',
            [
                {'url': 'http:/.../front.jpeg', 'type': 'image/jpeg'},
                {'url': 'http://.../back.jpeg'}
            ]
        ),
        (
            '',
            []
        ),
    ))
def test_parse_header_links(value, expected):
    assert parse_header_links(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        ('example.com/path', 'http://example.com/path'),
        ('//example.com/path', 'http://example.com/path'),
    ))
def test_prepend_scheme_if_needed(value, expected):
    assert prepend_scheme_if_needed(value, 'http') == expected


@pytest.mark.parametrize(
    'value, expected', (
        ('T', 'T'),
        (b'T', 'T'),
        (u'T', 'T'),
    ))
def test_to_native_string(value, expected):
    assert to_native_string(value) == expected


@pytest.mark.parametrize(
    'url, expected', (
        ('http://u:p@example.com/path?a=1#test', 'http://example.com/path?a=1'),
        ('http://example.com/path', 'http://example.com/path'),
        ('//u:p@example.com/path', '//example.com/path'),
        ('//example.com/path', '//example.com/path'),
        ('example.com/path', '//example.com/path'),
        ('scheme:u:p@example.com/path', 'scheme://example.com/path'),
    ))
def test_urldefragauth(url, expected):
    assert urldefragauth(url) == expected


@pytest.mark.parametrize(
    'url, expected', (
            ('http://192.168.0.1:5000/', True),
            ('http://192.168.0.1/', True),
            ('http://172.16.1.1/', True),
            ('http://172.16.1.1:5000/', True),
            ('http://localhost.localdomain:5000/v1.0/', True),
            ('http://172.16.1.12/', False),
            ('http://172.16.1.12:5000/', False),
            ('http://google.com:5000/v1.0/', False),
    ))
def test_should_bypass_proxies(url, expected, monkeypatch):
    """Tests for function should_bypass_proxies to check if proxy
    can be bypassed or not
    """
    monkeypatch.setenv('no_proxy', '192.168.0.0/24,127.0.0.1,localhost.localdomain,172.16.1.1')
    monkeypatch.setenv('NO_PROXY', '192.168.0.0/24,127.0.0.1,localhost.localdomain,172.16.1.1')
    assert should_bypass_proxies(url, no_proxy=None) == expected


@pytest.mark.parametrize(
    'cookiejar', (
        compat.cookielib.CookieJar(),
        RequestsCookieJar()
    ))
def test_add_dict_to_cookiejar(cookiejar):
    """Ensure add_dict_to_cookiejar works for
    non-RequestsCookieJar CookieJars
    """
    cookiedict = {'test': 'cookies',
                  'good': 'cookies'}
    cj = add_dict_to_cookiejar(cookiejar, cookiedict)
    cookies = dict((cookie.name, cookie.value) for cookie in cj)
    assert cookiedict == cookies


@pytest.mark.parametrize(
    'value, expected', (
                (u'test', True),
                (u'æíöû', False),
                (u'ジェーピーニック', False),
    )
)
def test_unicode_is_ascii(value, expected):
    assert unicode_is_ascii(value) is expected


@pytest.mark.parametrize(
    'url, expected', (
            ('http://192.168.0.1:5000/', True),
            ('http://192.168.0.1/', True),
            ('http://172.16.1.1/', True),
            ('http://172.16.1.1:5000/', True),
            ('http://localhost.localdomain:5000/v1.0/', True),
            ('http://172.16.1.12/', False),
            ('http://172.16.1.12:5000/', False),
            ('http://google.com:5000/v1.0/', False),
    ))
def test_should_bypass_proxies_no_proxy(
        url, expected, monkeypatch):
    """Tests for function should_bypass_proxies to check if proxy
    can be bypassed or not using the 'no_proxy' argument
    """
    no_proxy = '192.168.0.0/24,127.0.0.1,localhost.localdomain,172.16.1.1'
    # Test 'no_proxy' argument
    assert should_bypass_proxies(url, no_proxy=no_proxy) == expected


@pytest.mark.skipif(os.name != 'nt', reason='Test only on Windows')
@pytest.mark.parametrize(
    'url, expected, override', (
            ('http://192.168.0.1:5000/', True, None),
            ('http://192.168.0.1/', True, None),
            ('http://172.16.1.1/', True, None),
            ('http://172.16.1.1:5000/', True, None),
            ('http://localhost.localdomain:5000/v1.0/', True, None),
            ('http://172.16.1.22/', False, None),
            ('http://172.16.1.22:5000/', False, None),
            ('http://google.com:5000/v1.0/', False, None),
            ('http://mylocalhostname:5000/v1.0/', True, '<local>'),
            ('http://192.168.0.1/', False, ''),
    ))
def test_should_bypass_proxies_win_registry(url, expected, override,
                                            monkeypatch):
    """Tests for function should_bypass_proxies to check if proxy
    can be bypassed or not with Windows registry settings
    """
    if override is None:
        override = '192.168.*;127.0.0.1;localhost.localdomain;172.16.1.1'
    if compat.is_py3:
        import winreg
    else:
        import _winreg as winreg

    class RegHandle:
        def Close(self):
            pass

    ie_settings = RegHandle()

    def OpenKey(key, subkey):
        return ie_settings

    def QueryValueEx(key, value_name):
        if key is ie_settings:
            if value_name == 'ProxyEnable':
                return [1]
            elif value_name == 'ProxyOverride':
                return [override]

    monkeypatch.setenv('http_proxy', '')
    monkeypatch.setenv('https_proxy', '')
    monkeypatch.setenv('ftp_proxy', '')
    monkeypatch.setenv('no_proxy', '')
    monkeypatch.setenv('NO_PROXY', '')
    monkeypatch.setattr(winreg, 'OpenKey', OpenKey)
    monkeypatch.setattr(winreg, 'QueryValueEx', QueryValueEx)


@pytest.mark.parametrize(
    'env_name, value', (
            ('no_proxy', '192.168.0.0/24,127.0.0.1,localhost.localdomain'),
            ('no_proxy', None),
            ('a_new_key', '192.168.0.0/24,127.0.0.1,localhost.localdomain'),
            ('a_new_key', None),
    ))
def test_set_environ(env_name, value):
    """Tests set_environ will set environ values and will restore the environ."""
    environ_copy = copy.deepcopy(os.environ)
    with set_environ(env_name, value):
        assert os.environ.get(env_name) == value

    assert os.environ == environ_copy


def test_set_environ_raises_exception():
    """Tests set_environ will raise exceptions in context when the
    value parameter is None."""
    with pytest.raises(Exception) as exception:
        with set_environ('test1', None):
            raise Exception('Expected exception')

    assert 'Expected exception' in str(exception.value)
import requests


def test_can_access_urllib3_attribute():
    requests.packages.urllib3


def hook(value):
    return value[1:]


def test_chunked_upload():
    """can safely send generators"""
    close_server = threading.Event()
    server = Server.basic_response_server(wait_to_close_event=close_server)
    data = iter([b'a', b'b', b'c'])

    with server as (host, port):
        url = 'http://{0}:{1}/'.format(host, port)
        r = requests.post(url, data=data, stream=True)
        close_server.set()  # release server block

    assert r.status_code == 200
    assert r.request.headers['Transfer-Encoding'] == 'chunked'


def test_can_access_idna_attribute():
    requests.packages.idna


class TestMorselToCookieExpires:
    """Tests for morsel_to_cookie when morsel contains expires."""

    def test_expires_valid_str(self):
        """Test case where we convert expires from string time."""

        morsel = Morsel()
        morsel['expires'] = 'Thu, 01-Jan-1970 00:00:01 GMT'
        cookie = morsel_to_cookie(morsel)
        assert cookie.expires == 1

    @pytest.mark.parametrize(
        'value, exception', (
            (100, TypeError),
            ('woops', ValueError),
        ))
    def test_expires_invalid_int(self, value, exception):
        """Test case where an invalid type is passed for expires."""
        morsel = Morsel()
        morsel['expires'] = value
        with pytest.raises(exception):
            morsel_to_cookie(morsel)

    def test_expires_none(self):
        """Test case where expires is None."""

        morsel = Morsel()
        morsel['expires'] = None
        cookie = morsel_to_cookie(morsel)
        assert cookie.expires is None


class TestCaseInsensitiveDict:

    @pytest.mark.parametrize(
        'cid', (
            CaseInsensitiveDict({'Foo': 'foo', 'BAr': 'bar'}),
            CaseInsensitiveDict([('Foo', 'foo'), ('BAr', 'bar')]),
            CaseInsensitiveDict(FOO='foo', BAr='bar'),
        ))
    def test_init(self, cid):
        assert len(cid) == 2
        assert 'foo' in cid
        assert 'bar' in cid

    def test_docstring_example(self):
        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        assert cid['aCCEPT'] == 'application/json'
        assert list(cid) == ['Accept']

    def test_len(self):
        cid = CaseInsensitiveDict({'a': 'a', 'b': 'b'})
        cid['A'] = 'a'
        assert len(cid) == 2

    def test_getitem(self):
        cid = CaseInsensitiveDict({'Spam': 'blueval'})
        assert cid['spam'] == 'blueval'
        assert cid['SPAM'] == 'blueval'

    def test_fixes_649(self):
        """__setitem__ should behave case-insensitively."""
        cid = CaseInsensitiveDict()
        cid['spam'] = 'oneval'
        cid['Spam'] = 'twoval'
        cid['sPAM'] = 'redval'
        cid['SPAM'] = 'blueval'
        assert cid['spam'] == 'blueval'
        assert cid['SPAM'] == 'blueval'
        assert list(cid.keys()) == ['SPAM']

    def test_delitem(self):
        cid = CaseInsensitiveDict()
        cid['Spam'] = 'someval'
        del cid['sPam']
        assert 'spam' not in cid
        assert len(cid) == 0

    def test_contains(self):
        cid = CaseInsensitiveDict()
        cid['Spam'] = 'someval'
        assert 'Spam' in cid
        assert 'spam' in cid
        assert 'SPAM' in cid
        assert 'sPam' in cid
        assert 'notspam' not in cid

    def test_get(self):
        cid = CaseInsensitiveDict()
        cid['spam'] = 'oneval'
        cid['SPAM'] = 'blueval'
        assert cid.get('spam') == 'blueval'
        assert cid.get('SPAM') == 'blueval'
        assert cid.get('sPam') == 'blueval'
        assert cid.get('notspam', 'default') == 'default'

    def test_update(self):
        cid = CaseInsensitiveDict()
        cid['spam'] = 'blueval'
        cid.update({'sPam': 'notblueval'})
        assert cid['spam'] == 'notblueval'
        cid = CaseInsensitiveDict({'Foo': 'foo', 'BAr': 'bar'})
        cid.update({'fOO': 'anotherfoo', 'bAR': 'anotherbar'})
        assert len(cid) == 2
        assert cid['foo'] == 'anotherfoo'
        assert cid['bar'] == 'anotherbar'

    def test_update_retains_unchanged(self):
        cid = CaseInsensitiveDict({'foo': 'foo', 'bar': 'bar'})
        cid.update({'foo': 'newfoo'})
        assert cid['bar'] == 'bar'

    def test_iter(self):
        cid = CaseInsensitiveDict({'Spam': 'spam', 'Eggs': 'eggs'})
        keys = frozenset(['Spam', 'Eggs'])
        assert frozenset(iter(cid)) == keys

    def test_equality(self):
        cid = CaseInsensitiveDict({'SPAM': 'blueval', 'Eggs': 'redval'})
        othercid = CaseInsensitiveDict({'spam': 'blueval', 'eggs': 'redval'})
        assert cid == othercid
        del othercid['spam']
        assert cid != othercid
        assert cid == {'spam': 'blueval', 'eggs': 'redval'}
        assert cid != object()

    def test_setdefault(self):
        cid = CaseInsensitiveDict({'Spam': 'blueval'})
        assert cid.setdefault('spam', 'notblueval') == 'blueval'
        assert cid.setdefault('notspam', 'notblueval') == 'notblueval'

    def test_lower_items(self):
        cid = CaseInsensitiveDict({
            'Accept': 'application/json',
            'user-Agent': 'requests',
        })
        keyset = frozenset(lowerkey for lowerkey, v in cid.lower_items())
        lowerkeyset = frozenset(['accept', 'user-agent'])
        assert keyset == lowerkeyset

    def test_preserve_key_case(self):
        cid = CaseInsensitiveDict({
            'Accept': 'application/json',
            'user-Agent': 'requests',
        })
        keyset = frozenset(['Accept', 'user-Agent'])
        assert frozenset(i[0] for i in cid.items()) == keyset
        assert frozenset(cid.keys()) == keyset
        assert frozenset(cid) == keyset

    def test_preserve_last_key_case(self):
        cid = CaseInsensitiveDict({
            'Accept': 'application/json',
            'user-Agent': 'requests',
        })
        cid.update({'ACCEPT': 'application/json'})
        cid['USER-AGENT'] = 'requests'
        keyset = frozenset(['ACCEPT', 'USER-AGENT'])
        assert frozenset(i[0] for i in cid.items()) == keyset
        assert frozenset(cid.keys()) == keyset
        assert frozenset(cid) == keyset

    def test_copy(self):
        cid = CaseInsensitiveDict({
            'Accept': 'application/json',
            'user-Agent': 'requests',
        })
        cid_copy = cid.copy()
        assert cid == cid_copy
        cid['changed'] = True
        assert cid != cid_copy

