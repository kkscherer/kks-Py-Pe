# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: urllib_utf8.py 3309bc451be4 2009/12/04 11:02:00 Oliver Lau <oliver@von-und-fuer-lau.de> $

import logging

_safe = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~'

_htmlsafe = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~ #+*_.,:;?=)(/&%$"!^@'

_entities = {
     # A
     u'Â': '&Acirc;',
     u'â': '&acirc;',
     u'´': '&acute;',
     u'Æ': '&AElig;',
     u'æ': '&aelig;',
     u'À': '&Agrave;',
     u'à': '&agrave;',
     u'ℵ': '&alefsym;',
     u'Α': '&Alpha;',
     u'α': '&alpha;',
     u'&': '&amp;',
     u'∧': '&and;',
     u'∠': '&ang;',
     u"'": '&apos;',
     u'Å': '&Aring',
     u'å': '&aring;',
     u'≈': '&asymp;',
     u'Ã': '&Atilde;',
     u'ã': '&atilde;',
     u'Ä': '&Auml;',
     u'ä': '&auml;',
     # B
     u'\u201E': '&bdquo;',
     u'Β': '&Beta;',
     u'β': '&beta;',
     u'¦': '&brvbar;',
     u'\u2022': '&bull;',
     # C
     # D
     u'\u2021': '&Dagger;',
     u'\u2020': '&dagger;',
     u'\u21D3': '&dArr;',
     u'\u2193': '&darr;',
     u'\u00B0': '&deg;',
     u'\u0394': '&Delta;',
     u'\u03B4': '&delta;',
     u'\u2666': '&diams;',
     u'\u00F7': '&divide;',
     # E
     u'É': '&Eacute;',
     u'é': '&eacute;',
     u'Ê': '&Ecirc;',
     u'ê': '&ecirc;',
     u'È': '&Egrave;',
     u'è': '&egrave;',
     u'∅': '&empty;',
     u'Ε': '&Epsilon;',
     u'ε': '&epsilon;',
     u'≡': '&equiv;',
     u'Η': '&Eta;',
     u'η': '&eta;',
     u'Ð': '&ETH;',
     u'ð': '&eth',
     u'Ë': '&Euml;',
     u'ë': '&euml;',
     u'€': '&euro;',
     u'∃': '&exist;',
     # F
     u'\u0192': '&fnof;',
     u'\u2200': '&forall;',
     u'\u00BD': '&frac12;',
     u'\u00BC': '&frac14;',
     u'\u00BE': '&frac34;',
     u'\u2044': '&frasl;',
     # G
     u'\u0393': '&Gamma;',
     u'\u03B3': '&gamma;',
     u'\u2265': '&ge;',
     u'>': '&gt;',
     # u'\u08D9': '&ge;',
     # H
     u'\u21D4': '&hArr;',
     u'\u2194': '&harr;',
     u'\u2665': '&hearts;',
     u'\u2026': '&hellip;',
     # I
     u'Í': '&Iacute;',
     u'í': '&iacute;',
     u'\u00CE': '&Icirc;',
     u'\u00EE': '&icirc;',
     u'\u00A1': '&iexcl;',
     u'\u00CC': '&Igrave;',
     u'\u00EC': '&igrave;',
     u'\u2111': '&image;',
     u'\u221E': '&infin;',
     u'\u222B': '&int;',
     u'\u0399': '&Iota;',
     u'\u03B9': '&iota;',
     u'\u00BF': '&iquest;',
     u'\u2208': '&isin;',
     u'\u00CF': '&Iuml;',
     u'\u00EF': '&iuml;',
     # J
     # K
     u'\u039A': '&Kappa;',
     u'\u03BA': '&kappa;',
     # L
     u'\u039B': '&Lambda;',
     u'\u03BB': '&lambda;',
     u'\u2329': '&lang;',
     u'\u00AB': '&laquo;',
     u'\u21D0': '&lArr;',
     u'\u2190': '&larr;',
     u'\u2308': '&lceil;',
     u'\u201C': '&ldquo;',
     u'\u2264': '&le;',
     u'\u230A': '&lfloor;',
     u'\u2217': '&lowast;',
     u'\u25CA': '&loz;',
     u'\u200E': '&lrm;',
     u'\u2039': '&lsaquo;',
     u'\u2018': '&lsquo;',
     u'<': '&lt;',
     # M
     u'\u00AF': '&macr;',
     u'\u2014': '&mdash;',
     u'\u00B5': '&micro;',
     u'\u00B7': '&middot;',
     u'\u2212': '&minus;',
     u'\u039C': '&Mu;',
     u'\u03BC': '&mu;',
     # N
     u'\u2207': '&nabla;',
     u'\u00A0': '&nbsp;',
     u'\u2013': '&ndash;',
     u'\u2260': '&ne;',
     u'\u220B': '&ni;',
     u'\u00AC': '&not;',
     u'\u2209': '&notin;',
     u'\u2284': '&nsub;',
     u'\u00D1': '&Ntilde;',
     u'\u00F1': '&ntilde;',
     u'\u039D': '&Nu;',
     u'\u03BD': '&nu;',
     # O
     u'\u00D3': '&Oacute;',
     u'\u00F3': '&oacute;',
     u'\u00D4': '&Ocirc;',
     u'\u00F4': '&ocirc;',
     u'\u0152': '&OElig;',
     u'\u0153': '&oelig;',
     u'\u00D2': '&Ograve;',
     u'\u00F2': '&ograve;',
     u'\u203E': '&oline;',
     u'\u03A9': '&Omega;',
     u'\u03C9': '&omega;',
     u'\u039F': '&Omicron;',
     u'\u03BF': '&omicron;',
     u'\u2295': '&oplus;',
     u'\u2228': '&or;',
     u'\u00AA': '&ordf;',
     u'\u00BA': '&ordm;',
     u'\u00D8': '&Oslash;',
     u'\u00F8': '&oslash;',
     u'\u00D5': '&Otilde;',
     u'\u00F5': '&otilde;',
     u'\u2297': '&otimes;',
     u'Ö': '&Ouml;',
     u'ö': '&ouml;',
     # P
     u'\u00B6': '&para;',
     u'\u2202': '&part;',
     u'\u2030': '&permil;',
     u'\u22A5': '&perp;',
     u'\u03A6': '&Phi;',
     u'\u03C6': '&Pi;',
     u'\u03C0': '&pi;',
     u'\u03D6': '&piv;',
     u'\u00B1': '&plusmn;',
     u'\u00A3': '&pound;',
     u'\u2033': '&Prime;',
     u'\u2032': '&prime;',
     u'\u220F': '&prod;',
     u'\u221D': '&prop;',
     u'\u03A8': '&Psi;',
     u'\u03C8': '&psi;',
     # Q
     u'"': '&quot;',
     # R
     u'\u221A': '&radic;',
     u'\u232A': '&rang;',
     u'\u00BB': '&raquo;',
     u'\u21D2': '&rArr;',
     u'\u2192': '&rarr;',
     u'\u2309': '&rceil;',
     u'\u201D': '&rdquo;',
     u'\u211C': '&real;',
     u'\u00AE': '&reg;',
     u'\u230B': '&rfloor;',
     u'\u03A1': '&Rho;',
     u'\u03C1': '&rho;',
     u'\u200F': '&rlm;',
     u'\u203A': '&rsaquo;',
     u'\u2019': '&rsquo;',
     # S
     u'\u201A': '&sbquo;',
     u'\u0160': '&Scaron;',
     u'\u0161': '&scaron;',
     u'\u22C5': '&sdot;',
     u'\u00A7': '&sect;',
     u'\u00AD': '&shy;',
     u'\u03A3': '&Sigma;',
     u'\u03C3': '&sigma;',
     u'\u03C2': '&sigmaf;',
     u'\u223C': '&sim;',
     u'\u2660': '&spades;',
     u'\u2282': '&sub;',
     u'\u2286': '&sube;',
     u'\u2211': '&sum;',
     u'\u2283': '&sup;',
     u'\u00B9': '&sup1;',
     u'\u00B2': '&sup2;',
     u'\u00B3': '&sup3;',
     u'\u2287': '&supe;',
     u'\u00DF': '&szlig;',
     # T
     u'\u03A4': '&Tau;',
     u'\u03C4': '&tau;',
     u'\u2234': '&there4;',
     u'\u0398': '&Theta;',
     u'\u03B8': '&theta;',
     u'\u03D1': '&thetasym;',
     u'\u2009': '&thinsp;',
     u'\u00DE': '&THORN;',
     u'\u00FE': '&thorn;',
     u'\u02DC': '&tilde;',
     u'\u00D7': '&times;',
     u'\u2122': '&trade;',
     # U
     u'\u00DA': '&Uacute;',
     u'\u00FA': '&uacute;',
     u'\u21D1': '&uArr;',
     u'\u2191': '&uarr;',
     u'\u00DB': '&Ucirc;',
     u'\u00FB': '&ucirc;',
     u'\u00D9': '&Ugrave;',
     u'\u00F9': '&ugrave;',
     u'\u00A8': '&uml;',
     u'\u03D2': '&upsih;',
     u'\u03A5': '&Upsilon;',
     u'\u03C5': '&upsilon;',
     u'\u00DC': '&Uuml;',
     u'\u00FC': '&uuml;',
     # V
     # W
     u'\u2118': '&weierp;',
     # X
     u'\u039E': '&Xi;',
     u'\u03BE': '&xi;',
     # Y
     u'\u00DD': '&Yacute;',
     u'\u00FD': '&yacute;',
     u'\u00A5': '&yen;',
     u'\u0178': '&Yuml;',
     u'\u00FF': '&yuml;',
     # Z
     u'\u0396': '&Zeta;',
     u'\u03B6': '&zeta;',
     u'\u200D': '&zwj;',
     u'\u200C': '&zwnj;',
}

_nice = {
     u'ä': 'ae',
     u'ö': 'oe',
     u'ü': 'ue',
     u'Ä': 'Ae',
     u'Ö': 'Oe',
     u'Ü': 'Üe',
     u'ß': 'ss',
     u"\u00C5": 'A',
     u"\u00E5": 'a',
     u'à': 'a',
     u'á': 'a',
     u'â': 'a',
     u'è': 'e',
     u'é': 'e',
     u'ê': 'e',
     u"\u00EB": 'e',
     u'ì': 'i',
     u'í': 'i',
     u'î': 'i',
     u'ò': 'o',
     u'ó': 'o',
     u'ô': 'o',
     u'ù': 'u',
     u'ú': 'u',
     u'û': 'u',
     u'À': 'A',
     u'Á': 'A',
     u'Â': 'A',
     u'È': 'E',
     u'É': 'E',
     u'Ê': 'E',
     u"\u00CB": 'E',
     u'Ì': 'I',
     u'Í': 'I',
     u'Î': 'I',
     u'Ò': 'O',
     u'Ó': 'O',
     u'Ô': 'O',
     u'Ù': 'U',
     u'Ú': 'U',
     u'Û': 'U',
     u"¼": '1/4',
     u"\u00BD": '1/2',
     u'¾': '3/4',
     u'²': '2',
     u'³': '3',
     u'°': 'o',
     u'@': 'a',
     u" ": '-',
     u"\u2013": '-',
     u"\u2014": '-',
     u"\u00AF": '-',
     u"\u2212": '-',
     u"\u0152": 'OE',
     u"\u0153": 'oe',
     u"\u00C6": 'AE',
     u"\u00E6": 'ae',
     u"\u00AE": '_R_',
     u"\u00B1": '_R_',
     u"\u00C7": 'C',
     u"\u00D0": 'D',
     u"\u00D1": 'N',
     u"\u00D7": 'x',
     u"\u00DD": 'Y',
     u"\u00A2": 'c',
     u"\u00A5": 'Y',
     u"\u00E7": 'c',
     u"\u00F0": 'd',
     u"\u00F1": 'n',
     u"\u00FD": 'y',
     u"\u00FF": 'y',
     u"\u0100": 'A',
     u"\u0101": 'a',
     u"\u0102": 'A',
     u"\u0103": 'a',
     u"\u0104": 'A',
     u"\u0105": 'a',
     u"\u0106": 'C',
     u"\u0107": 'c',
     u"\u0108": 'C',
     u"\u0109": 'c',
     u"\u010a": 'C',
     u"\u010b": 'c',
     u"\u010c": 'C',
     u"\u010d": 'c',
     # TODO: Liste erweitern ...
}


def _nicen(c):
    if c in _safe: return c
    elif c in _nice: return _nice[c]
    return ''


def nicen(text):
    return u''.join(_nicen(k) for k in unicode(text))


def enc(c):
    if c in _safe: return c
    elif len(c) > 1: return ''.join(u'%%%2X' % (ord(x)) for x in c)
    return u'%%%2X' % ord(c)


# urllib.quote() fuehrt zu einer UnicodeDecode-Exception,
# wenn der uebergebene String Nicht-ASCII-Zeichen enthaelt. Die Funktion
# encode() bietet einen Unicode-tauglichen Ersatz fuer urllib.quote()
def encode(text):
    return u''.join(enc(k) for k in text.encode('utf8'))


# urllib.urlencode() fuehrt zu einer UnicodeDecode-Exception,
# wenn der uebergebene String Nicht-ASCII-Zeichen enthaelt. Die Funktion
# urlencode() bietet einen Unicode-tauglichen Ersatz fuer urllib.urlencode()
def urlencode(params):
    return u'&'.join(u'%s=%s' % (encode(k), encode(params[k])) for k in params)


def html_entity(c):
    if c in _htmlsafe: return c
    elif c in _entities: return _entities[c]
    return u'&#x%04x;' % ord(c)


def htmlentities(text):
    return u''.join(html_entity(k) for k in text)

