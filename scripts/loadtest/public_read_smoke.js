import http from 'k6/http';
import { check, sleep } from 'k6';

// A deliberately small, read-only smoke ramp. This is not a 10M-user benchmark.
const baseUrl = (__ENV.BASE_URL || '').replace(/\/+$/, '');
const readPath = __ENV.READ_PATH || '/';
const authorized = __ENV.LOAD_TEST_AUTHORIZED === 'YES';
const allowLocalHttp = __ENV.ALLOW_LOCAL_HTTP === 'YES';

if (!authorized) {
  throw new Error('Refusing to run: set LOAD_TEST_AUTHORIZED=YES only for a system you own or are explicitly authorized to test.');
}
if (!baseUrl) {
  throw new Error('BASE_URL is required.');
}
const schemeEnd = baseUrl.indexOf('://');
if (schemeEnd < 0 || /[/?#@]/.test(baseUrl.slice(schemeEnd + 3))) {
  throw new Error('BASE_URL must contain only the scheme, hostname, and optional port; put paths in READ_PATH.');
}
if (/[\r\n]/.test(baseUrl) || /[\r\n]/.test(readPath)) {
  throw new Error('BASE_URL and READ_PATH must not contain newline characters.');
}
if (!readPath.startsWith('/') || readPath.startsWith('//')) {
  throw new Error('READ_PATH must be a same-origin path beginning with one slash.');
}
const isHttps = baseUrl.startsWith('https://');
const isLocalHttp = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(baseUrl);
if (!isHttps && !(allowLocalHttp && isLocalHttp)) {
  throw new Error('HTTPS is required; HTTP is allowed only for localhost/127.0.0.1 with ALLOW_LOCAL_HTTP=YES.');
}

export const options = {
  stages: [
    { duration: '30s', target: 1 },
    { duration: '30s', target: 5 },
    { duration: '60s', target: 10 },
    { duration: '60s', target: 20 },
    { duration: '60s', target: 30 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1500'],
  },
  discardResponseBodies: true,
};

export default function () {
  const response = http.get(`${baseUrl}${readPath}`, {
    redirects: 3,
    timeout: '10s',
    tags: { test_type: 'read_only_smoke' },
  });

  check(response, {
    'read-only endpoint returns success or redirect': (r) =>
      r.status === 200 || (r.status >= 300 && r.status < 400),
  });

  sleep(1);
}
