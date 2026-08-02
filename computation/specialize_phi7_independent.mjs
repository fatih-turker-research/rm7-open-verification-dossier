#!/usr/bin/env node
// Independent BigInt reconstruction of the Frey-line Phi_7 specialization.
//
// Unlike specialize_phi7.py, this program keeps every source expression in
// Z[x,y], then substitutes x=(9/5)V^2 by clearing a separate power of 5 for
// each coefficient.  Agreement of the final canonical stream is therefore an
// independent check of the rational-polynomial arithmetic and normalization.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const EXPECTED_HASH = "C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC";
const PHI_U_EXPONENTS = [2, 3, ...Array(43).fill(4), 3, 2, 2, 1, 0];

function require(condition, message) {
  if (!condition) throw new Error(message);
}

function gcd(a, b) {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b !== 0n) [a, b] = [b, a % b];
  return a;
}

function pow(base, exponent) {
  let result = 1n;
  let b = BigInt(base);
  let e = exponent;
  while (e > 0) {
    if (e & 1) result *= b;
    e >>= 1;
    if (e) b *= b;
  }
  return result;
}

// Bivariate Z[x,y], keyed as "xDegree,yDegree".
function key(xDegree, yDegree) {
  return `${xDegree},${yDegree}`;
}

function unpack(monomial) {
  const comma = monomial.indexOf(",");
  return [Number(monomial.slice(0, comma)), Number(monomial.slice(comma + 1))];
}

function add(left, right) {
  if (left.size < right.size) [left, right] = [right, left];
  const result = new Map(left);
  for (const [monomial, coefficient] of right) {
    const value = (result.get(monomial) ?? 0n) + coefficient;
    if (value === 0n) result.delete(monomial);
    else result.set(monomial, value);
  }
  return result;
}

function negate(poly) {
  return new Map([...poly].map(([monomial, coefficient]) => [monomial, -coefficient]));
}

function multiply(left, right) {
  if (left.size === 0 || right.size === 0) return new Map();
  const result = new Map();
  for (const [leftMonomial, leftCoefficient] of left) {
    const [leftX, leftY] = unpack(leftMonomial);
    for (const [rightMonomial, rightCoefficient] of right) {
      const [rightX, rightY] = unpack(rightMonomial);
      const monomial = key(leftX + rightX, leftY + rightY);
      const value = (result.get(monomial) ?? 0n) + leftCoefficient * rightCoefficient;
      if (value === 0n) result.delete(monomial);
      else result.set(monomial, value);
    }
  }
  return result;
}

function polyPower(poly, exponent) {
  require(exponent >= 0, "negative exponent");
  let result = new Map([[key(0, 0), 1n]]);
  let base = poly;
  let e = exponent;
  while (e > 0) {
    if (e & 1) result = multiply(result, base);
    e >>= 1;
    if (e) base = multiply(base, base);
  }
  return result;
}

class Parser {
  constructor(text) {
    this.text = text;
    this.position = 0;
  }

  skipSpace() {
    while (this.position < this.text.length && /\s/.test(this.text[this.position])) {
      this.position += 1;
    }
  }

  peek() {
    this.skipSpace();
    return this.position < this.text.length ? this.text[this.position] : "";
  }

  take(expected = null) {
    this.skipSpace();
    require(this.position < this.text.length, "unexpected end of expression");
    const character = this.text[this.position++];
    if (expected !== null) require(character === expected, `expected ${expected}, got ${character}`);
    return character;
  }

  integer() {
    this.skipSpace();
    const start = this.position;
    while (this.position < this.text.length && /[0-9]/.test(this.text[this.position])) {
      this.position += 1;
    }
    require(this.position > start, `expected integer at ${start}`);
    return BigInt(this.text.slice(start, this.position));
  }

  parse() {
    const result = this.expression();
    require(this.peek() === "", `trailing input at ${this.position}`);
    return result;
  }

  expression() {
    let result = this.term();
    for (;;) {
      const token = this.peek();
      if (token === "+") {
        this.take();
        result = add(result, this.term());
      } else if (token === "-") {
        this.take();
        result = add(result, negate(this.term()));
      } else {
        return result;
      }
    }
  }

  term() {
    let result = this.factor();
    while (this.peek() === "*") {
      this.take();
      result = multiply(result, this.factor());
    }
    return result;
  }

  factor() {
    const token = this.peek();
    let result;
    if (token === "+") {
      this.take();
      result = this.factor();
    } else if (token === "-") {
      this.take();
      result = negate(this.factor());
    } else if (token === "(") {
      this.take();
      result = this.expression();
      this.take(")");
    } else if (token === "x") {
      this.take();
      result = new Map([[key(1, 0), 1n]]);
    } else if (token === "y") {
      this.take();
      result = new Map([[key(0, 1), 1n]]);
    } else if (/[0-9]/.test(token)) {
      result = new Map([[key(0, 0), this.integer()]]);
    } else {
      throw new Error(`unexpected token ${JSON.stringify(token)} at ${this.position}`);
    }
    if (this.peek() === "^") {
      this.take();
      const exponent = Number(this.integer());
      result = polyPower(result, exponent);
    }
    return result;
  }
}

// Return P(V) with P(V)/5^maxX = f((9/5)V^2,V).
function scaledPullback(poly) {
  let maxX = -1;
  for (const monomial of poly.keys()) maxX = Math.max(maxX, unpack(monomial)[0]);
  require(maxX >= 0, "zero source polynomial");
  const fivePowers = Array.from({length: maxX + 1}, (_, i) => pow(5n, i));
  const ninePowers = Array.from({length: maxX + 1}, (_, i) => pow(9n, i));
  const result = new Map();
  for (const [monomial, coefficient] of poly) {
    const [xDegree, yDegree] = unpack(monomial);
    const vDegree = 2 * xDegree + yDegree;
    const value = coefficient * ninePowers[xDegree] * fivePowers[maxX - xDegree];
    const total = (result.get(vDegree) ?? 0n) + value;
    if (total === 0n) result.delete(vDegree);
    else result.set(vDegree, total);
  }
  return {maxX, poly: result};
}

function multiplyVPolys(left, right) {
  const result = new Map();
  for (const [a, ca] of left) {
    for (const [b, cb] of right) {
      const degree = a + b;
      const value = (result.get(degree) ?? 0n) + ca * cb;
      if (value === 0n) result.delete(degree);
      else result.set(degree, value);
    }
  }
  return result;
}

function scaleShift(poly, scalar, shift) {
  return new Map([...poly].map(([degree, coefficient]) => [degree + shift, coefficient * scalar]));
}

function vOrder(poly) {
  require(poly.size > 0, "zero V-polynomial");
  return Math.min(...poly.keys());
}

function vDegree(poly) {
  require(poly.size > 0, "zero V-polynomial");
  return Math.max(...poly.keys());
}

function main() {
  const database = process.argv[2];
  require(database, "usage: node specialize_phi7_independent.mjs DATABASE");
  require(PHI_U_EXPONENTS.length === 50, "bad exponent table");

  const parseFile = relative => {
    const text = fs.readFileSync(path.join(database, relative), "ascii");
    return new Parser(text).parse();
  };

  const denominator = scaledPullback(parseFile("DenQ5Gund7"));
  require(denominator.maxX === 32, "unexpected denominator x-degree");
  require(vOrder(denominator.poly) === 28 && vDegree(denominator.poly) === 64,
    "unexpected denominator pullback");

  const numeratorData = [];
  for (let i = 1; i <= 50; i += 1) {
    numeratorData.push(scaledPullback(parseFile(`NumPhi/numphi${i}`)));
  }

  // Each entry is {xDegree, denominatorExponent, poly}.  The denominator
  // exponent records the exact power of 5 before a global scalar clear.
  const entries = [];
  const leadingPoly = scaleShift(
    multiplyVPolys(denominator.poly, denominator.poly),
    pow(9n, 4),
    8,
  );
  entries.push({xDegree: 50, denominatorExponent: 2 * denominator.maxX + 4, poly: leadingPoly});
  for (let i = 1; i <= 50; i += 1) {
    const k = 4 - PHI_U_EXPONENTS[i - 1];
    entries.push({
      xDegree: i - 1,
      denominatorExponent: numeratorData[i - 1].maxX + k,
      poly: scaleShift(numeratorData[i - 1].poly, pow(9n, k), 2 * k),
    });
  }

  const globalFiveExponent = Math.max(...entries.map(entry => entry.denominatorExponent));
  require(globalFiveExponent === 82, `unexpected scalar denominator 5^${globalFiveExponent}`);
  const coefficients = new Map();
  for (const entry of entries) {
    coefficients.set(
      entry.xDegree,
      scaleShift(entry.poly, pow(5n, globalFiveExponent - entry.denominatorExponent), 0),
    );
  }

  const commonVOrder = Math.min(...[...coefficients.values()].map(vOrder));
  require(commonVOrder === 64, `unexpected common V order ${commonVOrder}`);
  for (const [xDegree, poly] of coefficients) {
    coefficients.set(xDegree, new Map([...poly].map(([degree, value]) => [degree - commonVOrder, value])));
  }

  let content = 0n;
  for (const poly of coefficients.values()) {
    for (const value of poly.values()) content = gcd(content, value);
  }
  require(content === pow(2n, 48) * pow(3n, 64), `unexpected global content ${content}`);
  for (const poly of coefficients.values()) {
    for (const [degree, value] of poly) poly.set(degree, value / content);
  }

  const leading = coefficients.get(50);
  const leadingValue = leading.get(vDegree(leading));
  if (leadingValue < 0n) {
    for (const poly of coefficients.values()) {
      for (const [degree, value] of poly) poly.set(degree, -value);
    }
  }

  const digest = crypto.createHash("sha256");
  digest.update("ZXV-DESC-V1\n", "ascii");
  let totalTerms = 0;
  let maximumDigits = 0;
  for (let xDegree = 50; xDegree >= 0; xDegree -= 1) {
    digest.update(`X:${xDegree}\n`, "ascii");
    const poly = coefficients.get(xDegree) ?? new Map();
    const degrees = [...poly.keys()].sort((a, b) => b - a);
    for (const degree of degrees) {
      const value = poly.get(degree);
      digest.update(`${degree}:${value}\n`, "ascii");
      totalTerms += 1;
      maximumDigits = Math.max(maximumDigits, (value < 0n ? -value : value).toString().length);
    }
    digest.update("ENDX\n", "ascii");
  }
  const hash = digest.digest("hex").toUpperCase();
  const overallVDegree = Math.max(...[...coefficients.values()].map(vDegree));
  require(hash === EXPECTED_HASH, `canonical hash mismatch: ${hash}`);
  require(totalTerms === 4752, `unexpected term count ${totalTerms}`);
  require(overallVDegree === 100, `unexpected V-degree ${overallVDegree}`);
  require(maximumDigits === 755, `unexpected maximum digits ${maximumDigits}`);

  console.log(JSON.stringify({
    status: "PASS",
    method: "independent Node BigInt bivariate parse and power-of-5 denominator clear",
    canonical_stream_sha256: hash,
    bidegree: [50, overallVDegree],
    common_v_factor_removed: commonVOrder,
    scalar_denominator: `5^${globalFiveExponent}`,
    integer_content_removed: "2^48*3^64",
    total_nonzero_terms: totalTerms,
    maximum_decimal_coefficient_digits: maximumDigits,
  }, null, 2));
}

try {
  main();
} catch (error) {
  console.error(`FAIL: ${error.message}`);
  process.exitCode = 1;
}
