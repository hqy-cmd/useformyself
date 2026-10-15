/* WLoc Surge adaptation, MIT. Copyright (c) 2026 WLoc8.com contributors.
 * Based on OpenHRTT/wloc 07b3ba0ce63d50c2fc771809e560946e070bda89.
 * See LICENSE and README.md. No network, storage, or device identifiers logged.
 */
(function () {
  'use strict';
  const MAX = 1024 * 1024;
  const cat = parts => {
    const size = parts.reduce((n, p) => n + p.length, 0);
    if (size > MAX) throw Error('message too large');
    const out = new Uint8Array(size); let p = 0;
    for (const a of parts) { out.set(a, p); p += a.length; }
    return out;
  };
  function varint(value) {
    let n = BigInt.asUintN(64, BigInt(value)); const out = [];
    do { const b = Number(n & 127n); n >>= 7n; out.push(b | (n ? 128 : 0)); } while (n);
    return new Uint8Array(out);
  }
  function fields(a) {
    let p = 0; const out = [];
    function read() {
      let n = 0n;
      for (let i = 0; i < 10; i++) {
        if (p >= a.length) throw Error('truncated varint');
        const b = a[p++];
        if (i === 9 && b > 1) throw Error('varint overflow');
        n |= BigInt(b & 127) << BigInt(i * 7);
        if (!(b & 128)) return n;
      }
      throw Error('invalid varint');
    }
    while (p < a.length) {
      const start = p, key = read();
      const id = Number(key >> 3n), wire = Number(key & 7n);
      if (id < 1 || id > 536870911) throw Error('invalid field');
      let data;
      if (wire === 0) read();
      else if (wire === 1) p += 8;
      else if (wire === 5) p += 4;
      else if (wire === 2) {
        const n = read();
        if (n > BigInt(a.length - p)) throw Error('invalid field length');
        data = a.slice(p, p + Number(n)); p += Number(n);
      } else throw Error('unsupported protobuf wire type');
      if (p > a.length) throw Error('truncated field');
      out.push({id, wire, data, raw: a.slice(start, p)});
    }
    return out;
  }
  const msg = (id, bytes) => cat([varint(id * 8 + 2), varint(bytes.length), bytes]);
  const int = (id, n) => cat([varint(id * 8), varint(n)]);
  // Swift rounded(): nearest, ties away from zero.
  const round = n => n < 0 ? -Math.round(-n) : Math.round(n);
  function payload(a) {
    let p = 0;
    function uint(n) {
      if (p + n > a.length) throw Error('truncated ARPC');
      let v = 0; for (let i = 0; i < n; i++) v = v * 256 + a[p++];
      return v;
    }
    uint(2); // version: upstream accepts any UInt16
    for (let i = 0; i < 3; i++) {
      const n = uint(2); p += n;
      if (p > a.length) throw Error('truncated ARPC string');
    }
    uint(4); const n = uint(4);
    if (p + n !== a.length) throw Error('ARPC length mismatch');
    return a.slice(p);
  }
  function config(argument) {
    const c = Object.create(null);
    for (const pair of String(argument || '').split('&')) {
      const at = pair.indexOf('=');
      if (at > 0) c[pair.slice(0, at)] = decodeURIComponent(pair.slice(at + 1));
    }
    if (c.enabled !== 'true') return null;
    if (c.radiusKm === undefined) c.radiusKm = '0';
    function num(key, min, max, integer) {
      const s = c[key];
      if (!s || !/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(s)) throw Error('invalid ' + key);
      const n = Number(s);
      if (!Number.isFinite(n) || n < min || n > max || (integer && !Number.isInteger(n))) throw Error('invalid ' + key);
      return n;
    }
    return {lat: num('lat', -90, 90), lon: num('lon', -180, 180),
      radiusKm: num('radiusKm', 0, 1000),
      altitude: num('altitude', -12000, 100000),
      hacc: num('hacc', 0, 1000000, true), vacc: num('vacc', 0, 1000000, true)};
  }
  // Uniform area on a spherical cap, not uniform distance from the center.
  // Cartesian tangent basis stays well-defined at poles and the date line.
  function jitter(c) {
    if (!c.radiusKm) return c;
    const rad = Math.PI / 180, lat = c.lat * rad, lon = c.lon * rad;
    const angle = 2 * Math.asin(Math.sqrt(Math.random()) * Math.sin(c.radiusKm / 6371.0088 / 2));
    const bearing = 2 * Math.PI * Math.random();
    const cl = Math.cos(lat), sl = Math.sin(lat), co = Math.cos(lon), so = Math.sin(lon);
    const a = Math.cos(angle), n = Math.sin(angle) * Math.cos(bearing), e = Math.sin(angle) * Math.sin(bearing);
    const x = a * cl * co - n * sl * co - e * so;
    const y = a * cl * so - n * sl * so + e * co;
    const z = a * sl + n * cl;
    return Object.assign({}, c, {lat: Math.atan2(z, Math.hypot(x, y)) / rad, lon: Math.atan2(y, x) / rad});
  }
  function build(a, c) {
    c = jitter(c);
    const location = cat([int(1, round(c.lat * 1e8)), int(2, round(c.lon * 1e8)),
      int(3, c.hacc), int(4, 3), int(5, round(c.altitude)), int(6, c.vacc), int(11, 63), int(12, 467)]);
    let count = 0;
    const parts = [];
    for (const f of fields(payload(a))) {
      if (f.id === 2) {
        if (f.wire !== 2) throw Error('invalid WiFi field');
        const wifi = fields(f.data);
        if (!wifi.some(x => x.id === 1 && x.wire === 2 && x.data.length)) throw Error('missing BSSID');
        parts.push(msg(2, cat(wifi.filter(x => x.id !== 2).map(x => x.raw).concat([msg(2, location)]))));
        count++;
      } else if (![3, 4, 33].includes(f.id)) parts.push(f.raw);
    }
    if (!count) throw Error('no WiFi devices');
    const pb = cat(parts);
    if (pb.length > 65535) throw Error('response exceeds UInt16 envelope');
    return cat([new Uint8Array([0, 1, 0, 0, 0, 1, 0, 0, pb.length >> 8, pb.length & 255]), pb]);
  }
  let result = {};
  try {
    const c = config(typeof $argument === 'undefined' ? '' : $argument);
    if (c && typeof $request !== 'undefined' && $request.method === 'POST' &&
        /^https:\/\/(?:gs-loc|gs-loc-cn)\.apple\.com(?::443)?\/clls\/wloc(?:\?[^#]*)?$/.test($request.url)) {
      const headers = $request.headers || {};
      const encoding = Object.keys(headers).find(k => k.toLowerCase() === 'content-encoding');
      if (encoding && String(headers[encoding]).toLowerCase() !== 'identity') throw Error('encoded request unsupported');
      if (!($request.body instanceof Uint8Array) || !$request.body.length || $request.body.length > MAX) throw Error('invalid binary body');
      result = {response: {status: 200, headers: {'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control': 'no-store'}, body: build($request.body, c)}};
      console.log('[WLoc] synthetic response generated (' + result.response.body.length + ' bytes)');
    }
  } catch (e) { console.log('[WLoc] passthrough: ' + e.message); }
  $done(result);
})();
