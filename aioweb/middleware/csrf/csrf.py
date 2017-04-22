"""
Adapted Django CSRF middleware 
"""
import random
import re
import string
import hmac

REASON_NO_REFERER = "Referer checking failed - no Referer."
REASON_BAD_REFERER = "Referer checking failed - %s does not match any trusted origins."
REASON_NO_CSRF_COOKIE = "CSRF cookie not set."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."
REASON_MALFORMED_REFERER = "Referer checking failed - Referer is malformed."
REASON_INSECURE_REFERER = "Referer checking failed - Referer is insecure while host is secure."

CSRF_SECRET_LENGTH = 32
CSRF_TOKEN_LENGTH = 2 * CSRF_SECRET_LENGTH
CSRF_ALLOWED_CHARS = string.ascii_letters + string.digits


def _get_new_csrf_string():
    return ''.join([random.choice(CSRF_ALLOWED_CHARS) for c in range(CSRF_SECRET_LENGTH)])


def _salt_cipher_secret(secret):
    """
    Given a secret (assumed to be a string of CSRF_ALLOWED_CHARS), generate a
    token by adding a salt and using it to encrypt the secret.
    """
    salt = _get_new_csrf_string()
    chars = CSRF_ALLOWED_CHARS
    pairs = zip((chars.index(x) for x in secret), (chars.index(x) for x in salt))
    cipher = ''.join(chars[(x + y) % len(chars)] for x, y in pairs)
    return salt + cipher


def unsalt_cipher_token(token):
    """
    Given a token (assumed to be a string of CSRF_ALLOWED_CHARS, of length
    CSRF_TOKEN_LENGTH, and that its first half is a salt), use it to decrypt
    the second half to produce the original secret.
    """
    salt = token[:CSRF_SECRET_LENGTH]
    token = token[CSRF_SECRET_LENGTH:]
    chars = CSRF_ALLOWED_CHARS
    pairs = zip((chars.index(x) for x in token), (chars.index(x) for x in salt))
    secret = ''.join(chars[x - y] for x, y in pairs)  # Note negative values are ok
    return secret


def make_csrf_token(secret=None):
    return _salt_cipher_secret(secret if secret else _get_new_csrf_string())


def sanitize_token(token):
    # Allow only ASCII alphanumerics
    if not re.match('[a-zA-Z0-9]{%s}' % CSRF_TOKEN_LENGTH, token):
        return None
    elif len(token) == CSRF_TOKEN_LENGTH:
        return token
    elif len(token) == CSRF_SECRET_LENGTH:
        # Older Django versions set cookies to values of CSRF_SECRET_LENGTH
        # alphanumeric characters. For backwards compatibility, accept
        # such values as unsalted secrets.
        # It's easier to salt here and be consistent later, rather than add
        # different code paths in the checks, although that might be a tad more
        # efficient.
        return _salt_cipher_secret(token)
    return None


def compare_salted_tokens(request_csrf_token, csrf_token):
    # Assume both arguments are sanitized -- that is, strings of
    # length CSRF_TOKEN_LENGTH, all CSRF_ALLOWED_CHARS.
    return hmac.compare_digest(
        unsalt_cipher_token(request_csrf_token),
        unsalt_cipher_token(csrf_token),
    )

#
# class CsrfViewMiddleware(MiddlewareMixin):
#     """
#     Middleware that requires a present and correct csrfmiddlewaretoken
#     for POST requests that have a CSRF cookie, and sets an outgoing
#     CSRF cookie.
#
#     This middleware should be used in conjunction with the csrf_token template
#     tag.
#     """
#     # The _accept and _reject methods currently only exist for the sake of the
#     # requires_csrf_token decorator.
#     def _accept(self, request):
#         # Avoid checking the request twice by adding a custom attribute to
#         # request.  This will be relevant when both decorator and middleware
#         # are used.
#         request.csrf_processing_done = True
#         return None
#
#     def _reject(self, request, reason):
#         logger.warning(
#             'Forbidden (%s): %s', reason, request.path,
#             extra={
#                 'status_code': 403,
#                 'request': request,
#             }
#         )
#         return _get_failure_view()(request, reason=reason)
#
#     def process_view(self, request, callback, callback_args, callback_kwargs):
#         if getattr(request, 'csrf_processing_done', False):
#             return None
#
#         try:
#             cookie_token = request.COOKIES[settings.CSRF_COOKIE_NAME]
#         except KeyError:
#             csrf_token = None
#         else:
#             csrf_token = _sanitize_token(cookie_token)
#             if csrf_token != cookie_token:
#                 # Cookie token needed to be replaced;
#                 # the cookie needs to be reset.
#                 request.csrf_cookie_needs_reset = True
#             # Use same token next time.
#             request.META['CSRF_COOKIE'] = csrf_token
#
#         # Wait until request.META["CSRF_COOKIE"] has been manipulated before
#         # bailing out, so that get_token still works
#         if getattr(callback, 'csrf_exempt', False):
#             return None
#
#         # Assume that anything not defined as 'safe' by RFC7231 needs protection
#         if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
#             if getattr(request, '_dont_enforce_csrf_checks', False):
#                 # Mechanism to turn off CSRF checks for test suite.
#                 # It comes after the creation of CSRF cookies, so that
#                 # everything else continues to work exactly the same
#                 # (e.g. cookies are sent, etc.), but before any
#                 # branches that call reject().
#                 return self._accept(request)
#
#             if request.is_secure():
#                 # Suppose user visits http://example.com/
#                 # An active network attacker (man-in-the-middle, MITM) sends a
#                 # POST form that targets https://example.com/detonate-bomb/ and
#                 # submits it via JavaScript.
#                 #
#                 # The attacker will need to provide a CSRF cookie and token, but
#                 # that's no problem for a MITM and the session-independent
#                 # secret we're using. So the MITM can circumvent the CSRF
#                 # protection. This is true for any HTTP connection, but anyone
#                 # using HTTPS expects better! For this reason, for
#                 # https://example.com/ we need additional protection that treats
#                 # http://example.com/ as completely untrusted. Under HTTPS,
#                 # Barth et al. found that the Referer header is missing for
#                 # same-domain requests in only about 0.2% of cases or less, so
#                 # we can use strict Referer checking.
#                 referer = force_text(
#                     request.META.get('HTTP_REFERER'),
#                     strings_only=True,
#                     errors='replace'
#                 )
#                 if referer is None:
#                     return self._reject(request, REASON_NO_REFERER)
#
#                 referer = urlparse(referer)
#
#                 # Make sure we have a valid URL for Referer.
#                 if '' in (referer.scheme, referer.netloc):
#                     return self._reject(request, REASON_MALFORMED_REFERER)
#
#                 # Ensure that our Referer is also secure.
#                 if referer.scheme != 'https':
#                     return self._reject(request, REASON_INSECURE_REFERER)
#
#                 # If there isn't a CSRF_COOKIE_DOMAIN, assume we need an exact
#                 # match on host:port. If not, obey the cookie rules.
#                 if settings.CSRF_COOKIE_DOMAIN is None:
#                     # request.get_host() includes the port.
#                     good_referer = request.get_host()
#                 else:
#                     good_referer = settings.CSRF_COOKIE_DOMAIN
#                     server_port = request.get_port()
#                     if server_port not in ('443', '80'):
#                         good_referer = '%s:%s' % (good_referer, server_port)
#
#                 # Here we generate a list of all acceptable HTTP referers,
#                 # including the current host since that has been validated
#                 # upstream.
#                 good_hosts = list(settings.CSRF_TRUSTED_ORIGINS)
#                 good_hosts.append(good_referer)
#
#                 if not any(is_same_domain(referer.netloc, host) for host in good_hosts):
#                     reason = REASON_BAD_REFERER % referer.geturl()
#                     return self._reject(request, reason)
#
#             if csrf_token is None:
#                 # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
#                 # and in this way we can avoid all CSRF attacks, including login
#                 # CSRF.
#                 return self._reject(request, REASON_NO_CSRF_COOKIE)
#
#             # Check non-cookie token for match.
#             request_csrf_token = ""
#             if request.method == "POST":
#                 try:
#                     request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
#                 except IOError:
#                     # Handle a broken connection before we've completed reading
#                     # the POST data. process_view shouldn't raise any
#                     # exceptions, so we'll ignore and serve the user a 403
#                     # (assuming they're still listening, which they probably
#                     # aren't because of the error).
#                     pass
#
#             if request_csrf_token == "":
#                 # Fall back to X-CSRFToken, to make things easier for AJAX,
#                 # and possible for PUT/DELETE.
#                 request_csrf_token = request.META.get(settings.CSRF_HEADER_NAME, '')
#
#             request_csrf_token = _sanitize_token(request_csrf_token)
#             if not _compare_salted_tokens(request_csrf_token, csrf_token):
#                 return self._reject(request, REASON_BAD_TOKEN)
#
#         return self._accept(request)
#
#     def process_response(self, request, response):
#         if not getattr(request, 'csrf_cookie_needs_reset', False):
#             if getattr(response, 'csrf_cookie_set', False):
#                 return response
#
#         if not request.META.get("CSRF_COOKIE_USED", False):
#             return response
#
#         # Set the CSRF cookie even if it's already set, so we renew
#         # the expiry timer.
#         response.set_cookie(settings.CSRF_COOKIE_NAME,
#                             request.META["CSRF_COOKIE"],
#                             max_age=settings.CSRF_COOKIE_AGE,
#                             domain=settings.CSRF_COOKIE_DOMAIN,
#                             path=settings.CSRF_COOKIE_PATH,
#                             secure=settings.CSRF_COOKIE_SECURE,
#                             httponly=settings.CSRF_COOKIE_HTTPONLY
#                             )
#         # Content varies with the CSRF cookie, so set the Vary header.
#         patch_vary_headers(response, ('Cookie',))
#         response.csrf_cookie_set = True
#         return response
