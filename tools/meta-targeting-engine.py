#!/usr/bin/env python3
"""Tyrion v5.0 Detailed Targeting Accuracy Engine (`tools/meta-targeting-engine.py`).

Vazifasi:
  Meta Ads Detailed Targeting (Детальный таргетинг — Interests, Behaviors, Demographics) variantlarini
  uydirmasdan, rasmiy Meta Marketing API v26.0 endpointlari orqali qidirish, tekshirish (validation)
  va har bir variantni 6 ta qat'iy aniqlik holatiga (`validation_status`) ajratib hisobot chiqarish.

Rasmiy Meta Marketing API Endpointlari:
  1. Global Targeting Search     : `GET /{api_version}/search?type=adinterest&q={q}&limit={limit}&locale={locale}`
  2. Account Targeting Search    : `GET /{api_version}/act_{ad_account_id}/targetingsearch?q={q}&limit={limit}&locale={locale}`
  3. Account Targeting Suggestions: `GET /{api_version}/act_{ad_account_id}/targetingsuggestions?targeting_list={json}`
  4. Account Targeting Validation : `GET /{api_version}/act_{ad_account_id}/targetingvalidation?targeting_list={json}`

6 ta Qat'iy Holat (Validation Status):
  - `VERIFIED_AVAILABLE`          : Rasmiy API dan topilgan VA `targetingvalidation` da `valid: true` bilan tasdiqlangan.
  - `FOUND_NOT_VALIDATED`         : Rasmiy API qidiruvidan (`/search` yoki `targetingsearch`) topilgan, ammo `targetingvalidation` bajarilmagan.
  - `UNAVAILABLE_OR_CONSOLIDATED` : Rasmiy API variantning eskirgani, yaroqsizligi (`valid: false`) yoki boshqa variantga birlashtirilganini bildirgan.
  - `RELATED_UNVERIFIED`          : AI/ekspert tomonidan mazmunan mos deb taklif qilingan g'oya yoki statik lug'at elementi — Meta API da tasdiqlanmagan!
  - `NOT_FOUND`                   : Bajarilgan live qidiruv urinishida rasmiy API dan natija qaytmadi (mutlaq yo'qlik isboti emas, faqat shu so'rov bo'yicha topilmadi).
  - `API_UNAVAILABLE`             : Live qidiruvni bajarib bo'lmadi (token yo'q, 401/403 ruxsat xatosi, 429 limit, 5xx yoki tarmoq uzilishi).

Qat'iy Qoida:
  Live API ishlamagan (`API_UNAVAILABLE`) yoki tekshirilmagan holatda HECH QACHON statik ro'yxat (`NICHE_TAXONOMY` / `SOLVENTNOST_FILTERS`)
  yoki AI taxmini `VERIFIED_AVAILABLE` yoxud `FOUND_NOT_VALIDATED` sifatida ko'rsatilmaydi!
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

DEFAULT_GRAPH_API_VERSION = "v26.0"

# 6 Canonical Statuses
STATUS_VERIFIED_AVAILABLE = "VERIFIED_AVAILABLE"
STATUS_FOUND_NOT_VALIDATED = "FOUND_NOT_VALIDATED"
STATUS_UNAVAILABLE_OR_CONSOLIDATED = "UNAVAILABLE_OR_CONSOLIDATED"
STATUS_RELATED_UNVERIFIED = "RELATED_UNVERIFIED"
STATUS_NOT_FOUND = "NOT_FOUND"
STATUS_API_UNAVAILABLE = "API_UNAVAILABLE"

ALL_VALID_STATUSES = (
    STATUS_VERIFIED_AVAILABLE,
    STATUS_FOUND_NOT_VALIDATED,
    STATUS_UNAVAILABLE_OR_CONSOLIDATED,
    STATUS_RELATED_UNVERIFIED,
    STATUS_NOT_FOUND,
    STATUS_API_UNAVAILABLE,
)

SPECIAL_AD_CATEGORIES = ("NONE", "HOUSING", "EMPLOYMENT", "CREDIT", "ISSUES_ELECTIONS_POLITICS")

# O'zbek lotin, O'zbek kirill va Rus tilidagi tushunchalarni Meta Graph API qidiruv so'rovlariga (faqat query sifatida!) kengaytirish lug'ati.
# MUHIM: Bular tasdiqlangan Meta interest nomlari EMAS, faqat API ga yuboriladigan qidiruv kalit so'zlaridir.
MULTILINGUAL_QUERY_SYNONYMS: dict[str, list[str]] = {
    # Real estate / Ko'chmas mulk
    "ko'chmas mulk": ["Real estate", "Property", "Apartment", "Mortgage loan", "Real estate investing"],
    "kochmas mulk": ["Real estate", "Property", "Apartment", "Mortgage loan"],
    "xonadon": ["Apartment", "Condominium", "Housing", "Interior design"],
    "novostroyka": ["Apartment", "Real estate", "New construction", "Property investment"],
    "ipoteka": ["Mortgage loan", "Home equity", "Real estate"],
    "кўчмас мулк": ["Real estate", "Property", "Apartment", "Mortgage loan"],
    "хонадон": ["Apartment", "Housing", "Interior design"],
    "ипотека": ["Mortgage loan", "Real estate"],
    "недвижимость": ["Real estate", "Property", "Apartment", "Real estate investing"],
    "квартира": ["Apartment", "Condominium", "Interior design"],
    # Education / Ta'lim
    "ta'lim": ["Higher education", "Online learning", "Education", "Career development"],
    "talim": ["Higher education", "Online learning", "Education"],
    "kurs": ["Online learning", "Professional certification", "Vocational education"],
    "ingliz tili": ["English language", "IELTS", "Language school", "TOEFL"],
    "таълим": ["Higher education", "Online learning", "Education"],
    "инглиз тили": ["English language", "IELTS", "Language school"],
    "образование": ["Higher education", "Online learning", "Education"],
    "курсы": ["Online learning", "Professional certification", "Career development"],
    "английский язык": ["English language", "IELTS", "Language school"],
    # Medical / Tibbiyot
    "stomatologiya": ["Dentistry", "Cosmetic dentistry", "Oral hygiene", "Dental implant"],
    "klinika": ["Healthcare", "Medicalger", "Medicine", "Physical therapy", "Wellness"],
    "tibbiyot": ["Healthcare", "Medicine", "Wellness", "Medical specialty"],
    "стоматология": ["Dentistry", "Cosmetic dentistry", "Oral hygiene"],
    "клиника": ["Healthcare", "Medicine", "Wellness"],
    "медицина": ["Healthcare", "Medicine", "Wellness"],
    # E-commerce & Fashion
    "kiyim": ["Clothing", "Shopping and fashion", "Boutique", "Online shopping"],
    "erkaklar kostyumi": ["Men's clothing", "Suit (clothing)", "Formal wear", "Shopping and fashion"],
    "kostyum": ["Suit (clothing)", "Formal wear", "Men's clothing", "Fashion"],
    "ayollar kiyimi": ["Women's clothing", "Dresses", "Boutique", "Shopping and fashion"],
    "onlayn do'kon": ["Online shopping", "E-commerce", "Discount store", "Shopping"],
    "кийим": ["Clothing", "Shopping and fashion", "Online shopping"],
    "одежда": ["Clothing", "Shopping and fashion", "Boutique", "Online shopping"],
    # Beauty & Cosmetics
    "kosmetika": ["Cosmetics", "Skin care", "Beauty salon", "Fragrances"],
    "atir": ["Fragrances", "Perfume", "Luxury goods", "Cosmetics"],
    "parfyumeriya": ["Fragrances", "Perfume", "Cosmetics"],
    "косметика": ["Cosmetics", "Skin care", "Beauty salon"],
    "парфюмерия": ["Fragrances", "Perfume", "Luxury goods"],
    # Auto
    "avtomobil": ["Automobile", "Car dealership", "Auto detailing", "Automotive repair shop"],
    "avtoservis": ["Automotive repair shop", "Auto detailing", "Vehicle maintenance"],
    "автомобиль": ["Automobile", "Car dealership", "Auto detailing"],
    "автосервис": ["Automotive repair shop", "Auto detailing"],
    # B2B / SaaS
    "biznes": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management"],
    "crm": ["Customer relationship management", "Enterprise software", "Sales"],
    "бизнес": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management"],
    # Local / Fitness / HoReCa
    "fitnes": ["Physical fitness", "Gym", "Weight training", "Yoga"],
    "restoran": ["Restaurants", "Fast food", "Dining out", "Coffeehouses"],
    "фитнес": ["Physical fitness", "Gym", "Weight training"],
    "ресторан": ["Restaurants", "Dining out"],
}

NICHE_SEED_CANDIDATES: dict[str, list[str]] = {
    "ecom": ["Online shopping", "Shopping and fashion", "Boutique", "Consumer electronics", "Engaged Shoppers"],
    "edu": ["Higher education", "Online learning", "Language school", "IELTS", "Career development"],
    "real-estate": ["Real estate", "Property investment", "Apartment", "Mortgage loan", "Interior design"],
    "medical": ["Healthcare", "Dentistry", "Cosmetic dentistry", "Physical therapy", "Wellness"],
    "b2b": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management", "Digital marketing"],
    "beauty": ["Cosmetics", "Fragrances", "Beauty salon", "Skin care", "Luxury goods"],
    "auto": ["Automobile", "Car dealership", "Auto detailing", "SUV", "Automotive repair shop"],
    "local": ["Physical fitness", "Gym", "Restaurants", "Tourism", "Hotel"],
}

SOLVENTNOST_HYPOTHESES: list[dict[str, str]] = [
    {
        "candidate_name": "Engaged Shoppers",
        "category_hint": "behaviors",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "So'nggi 7 kunda reklamadagi 'Shop Now' CTA tugmasini bosgan foydalanuvchilar. Yuqori daromad kafolati emas, balki onlayn xarid faolligi gipotezasi.",
    },
    {
        "candidate_name": "Frequent International Travelers",
        "category_hint": "behaviors",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "Chet elga safar qiluvchilar. Yuqori to'lov qobiliyati uchun bilvosita marketing gipotezasi — xizmat sohasiga qarab A/B sinov talab etiladi.",
    },
    {
        "candidate_name": "Facebook Page Admins",
        "category_hint": "behaviors",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "Biznes sahifa administratorlari. B2B qaror qabul qiluvchilar uchun gipoteza (SMM mutaxassislari ham kirib qolishi mumkin).",
    },
    {
        "candidate_name": "Mobile Device User: Flagship / iPhone Pro Series",
        "category_hint": "user_device",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "Qurilma modeli daromadning mutlaq isboti emas (nasiyaga olingan bo'lishi mumkin) — faqat tekshiriladigan gipoteza sifatida qo'llang.",
    },
]


def get_graph_api_version() -> str:
    ver = os.environ.get("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION).strip()
    return ver if ver else DEFAULT_GRAPH_API_VERSION


def normalize_account_id_optional(account_id: str) -> str:
    clean = str(account_id or "").strip()
    if not clean:
        clean = os.environ.get("META_AD_ACCOUNT_ID", "").strip()
    if not clean or clean == "act_1234567890":
        return ""
    if not clean.startswith("act_"):
        clean = f"act_{clean}"
    if not clean[4:].isdigit():
        raise ValueError(f"Noto'g'ri Meta Ad Account ID formati: {clean!r} (namuna: act_1234567890)")
    return clean


def detect_query_language(text: str, explicit_lang: str = "auto") -> str:
    if explicit_lang and explicit_lang != "auto":
        return explicit_lang
    s = str(text or "")
    if re.search(r"[ўқғҳЎҚҒҲ]", s):
        return "uz_cyrillic"
    if re.search(r"[а-яА-ЯёЁ]", s):
        return "ru"
    if re.search(r"\b(ko'chmas|ta'lim|bo'yicha|uchun|do'kon|kiyim|xonadon|shifokor)\b", s.lower()):
        return "uz_latin"
    return "en"


def expand_search_queries(
    product: str = "",
    niche: str = "ecom",
    customer_profile: str = "",
    extra_queries: list[str] | None = None,
    max_queries: int = 8,
) -> list[dict[str, str]]:
    """Mahsulot, nisha va mijoz profilidan qidiruv so'rovlarini (search queries) shakllantiradi.
    Bular faqat qidiruv uchun nomzod so'rovlardir — Meta tasdiqlagan interestlar EMAS!
    """
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()

    def _add(term: str, origin: str) -> None:
        clean = re.sub(r"\s+", " ", str(term or "").strip())
        if not clean or len(clean) < 2:
            return
        key = clean.lower()
        if key not in seen and len(candidates) < max_queries:
            seen.add(key)
            candidates.append({
                "query": clean[:100],
                "origin": origin,
                "role": "SEARCH_QUERY_ONLY_NOT_VERIFIED_INTEREST",
            })

    if extra_queries:
        for q in extra_queries:
            if q and str(q).strip():
                _add(str(q).strip(), "explicit_user_query")
                low_q = str(q).strip().lower()
                for syn in MULTILINGUAL_QUERY_SYNONYMS.get(low_q, []):
                    _add(syn, f"multilingual_synonym:{low_q}")

    combined_input = f"{product} {customer_profile}".strip().lower()
    if combined_input:
        for phrase, syns in MULTILINGUAL_QUERY_SYNONYMS.items():
            if phrase in combined_input:
                for syn in syns:
                    _add(syn, f"multilingual_synonym:{phrase}")

    if product.strip():
        _add(product.strip(), "product_description")

    for seed in NICHE_SEED_CANDIDATES.get(niche, NICHE_SEED_CANDIDATES["ecom"]):
        _add(seed, f"niche_seed:{niche}")

    return candidates[:max_queries]


def _validate_same_origin(next_url: str, base_url: str) -> str:
    clean_next = tcore.sanitize_url(next_url)
    p_next = urllib.parse.urlparse(clean_next)
    p_base = urllib.parse.urlparse(base_url)
    if p_next.scheme.lower() != p_base.scheme.lower() or p_next.netloc.lower() != p_base.netloc.lower():
        raise PermissionError(
            f"Xavfsizlik xatosi: paging.next URL manzili ({p_next.netloc}) asosiy Graph API domeniga ({p_base.netloc}) mos emas!"
        )
    return clean_next


def _compute_relevance_reason(
    item_name: str,
    item_type: str,
    item_path: list[str] | None,
    search_query: str,
    product: str,
    niche: str,
    customer_profile: str,
) -> str:
    """AI/evristik moslik izohi. Bu Meta tasdig'i EMAS, balki tahliliy izoh."""
    parts = [f"'{search_query}' so'rovi orqali rasmiy API dan topildi"]
    if item_path:
        parts.append(f"kategoriya yo'li: {' > '.join(str(x) for x in item_path)}")
    if product:
        parts.append(f"mahsulot ('{product}') va '{niche}' nishasi uchun mazmunan mos nomzod")
    else:
        parts.append(f"'{niche}' nishasi auditoriya segmentiga aloqador")
    if customer_profile:
        parts.append(f"mijoz profili ('{customer_profile}') bilan kesishish ehtimoli bor")
    return " (AI tahlili, Meta kafolati emas: " + "; ".join(parts) + ")."


def _parse_optional_bound(val: Any) -> int | None:
    """Faqat API javobida aniq son qaytganda int qaytaradi; aks holda None (hech qachon uydirmaydi)."""
    if val is None or isinstance(val, bool) or val == "":
        return None
    try:
        num = int(float(val))
        return num if num >= 0 else None
    except (ValueError, TypeError):
        return None


def _load_valid_cache(
    cache_path: Path | None,
    cache_key: str,
    api_version: str,
    ttl_seconds: int,
) -> tuple[dict[str, Any] | None, str | None]:
    if cache_path is None or not cache_path.is_file():
        return None, None
    try:
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
        entries = raw.get("entries", {}) if isinstance(raw, dict) else {}
        entry = entries.get(cache_key)
        if not isinstance(entry, dict):
            return None, None
        cached_ver = str(entry.get("api_version", ""))
        fetched_epoch = float(entry.get("fetched_epoch", 0.0))
        entry_ttl = int(entry.get("ttl_seconds", ttl_seconds))
        age = time.time() - fetched_epoch
        if cached_ver != api_version:
            return None, f"Kesh versiyasi eskirgan ({cached_ver} != {api_version}) — yangi live so'rov talab etiladi."
        if age > entry_ttl:
            return None, f"Kesh muddati tugagan (yoshi {int(age)}s > TTL {entry_ttl}s) — eskirgan kesh tasdiqlangan natija sifatida ishlatilmaydi."
        payload = entry.get("payload")
        if isinstance(payload, dict):
            return payload, None
    except Exception:
        return None, "Kesh fayli o'qilmadi — live API ga murojaat qilinadi."
    return None, None


def _save_cache(
    cache_path: Path | None,
    cache_key: str,
    api_version: str,
    ttl_seconds: int,
    query_params: dict[str, Any],
    payload: dict[str, Any],
) -> None:
    if cache_path is None:
        return
    existing: dict[str, Any] = {"schema": "tyrion.targeting_cache/v5", "entries": {}}
    if cache_path.is_file():
        try:
            loaded = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("entries"), dict):
                existing = loaded
        except Exception:
            pass
    existing["entries"][cache_key] = {
        "api_version": api_version,
        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fetched_epoch": time.time(),
        "ttl_seconds": ttl_seconds,
        "query_params": query_params,
        "payload": payload,
    }
    tcore.atomic_write_json(cache_path, existing)


def _fetch_paginated_endpoint(
    initial_url: str,
    base_url: str,
    headers: dict[str, str],
    max_pages: int = 3,
    timeout: float = 8.0,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Graph API endpointidan (`targetingsearch` yoki `/search`) sahifalangan (`paging.next`) natijalarni yig'adi."""
    all_items: list[dict[str, Any]] = []
    current_url: str | None = initial_url
    pages_fetched = 0

    while current_url and pages_fetched < max_pages:
        resp = tcore.http_get_json_with_backoff(
            current_url, headers=headers, timeout=timeout, max_retries=max_retries
        )
        if "error" in resp:
            return {
                "ok": False,
                "error": tcore.redact_secrets(str(resp.get("error", "API xatosi"))),
                "http_status": resp.get("http_status"),
                "error_category": resp.get("error_category", "API_ERROR"),
                "retries_attempted": resp.get("retries_attempted", 0),
                "items": all_items,
                "pages_fetched": pages_fetched,
            }
        data = resp.get("data")
        if not isinstance(data, list):
            return {
                "ok": False,
                "error": "Meta Graph API javobida `data` ro'yxati topilmadi.",
                "http_status": 200,
                "error_category": "UNEXPECTED_PAYLOAD_SHAPE",
                "retries_attempted": 0,
                "items": all_items,
                "pages_fetched": pages_fetched,
            }
        for row in data:
            if isinstance(row, dict):
                all_items.append(row)
        pages_fetched += 1

        paging = resp.get("paging")
        next_raw = paging.get("next") if isinstance(paging, dict) else None
        if next_raw and isinstance(next_raw, str) and next_raw.strip():
            current_url = _validate_same_origin(next_raw.strip(), base_url)
        else:
            current_url = None

    return {
        "ok": True,
        "items": all_items,
        "pages_fetched": pages_fetched,
        "is_truncated": current_url is not None,
    }


def _run_targeting_validation(
    base_url: str,
    api_version: str,
    account_id: str,
    headers: dict[str, str],
    items_by_key: dict[tuple[str, str], dict[str, Any]],
    checked_at: str,
) -> tuple[bool, str | None]:
    """`GET /{api_version}/{act_id}/targetingvalidation` orqali topilgan variantlarning yaroqliligini tekshiradi."""
    if not account_id or not items_by_key:
        return False, None

    targeting_list = [
        {"id": item["id"], "type": item["type"], "name": item["name"]}
        for item in items_by_key.values()
    ]
    params = urllib.parse.urlencode({
        "targeting_list": json.dumps(targeting_list, ensure_ascii=False),
    })
    val_endpoint = f"GET /{api_version}/{account_id}/targetingvalidation"
    url = f"{base_url}/{api_version}/{account_id}/targetingvalidation?{params}"
    resp = tcore.http_get_json_with_backoff(url, headers=headers, timeout=8.0, max_retries=2)
    if "error" in resp:
        return False, f"targetingvalidation bajarilmadi ({resp.get('error_category', 'ERROR')}): {tcore.redact_secrets(str(resp['error']))}"

    data = resp.get("data")
    if not isinstance(data, list):
        return False, "targetingvalidation kutilmagan javob qaytardi (`data` ro'yxat emas)."

    val_by_id: dict[str, dict[str, Any]] = {}
    for row in data:
        if isinstance(row, dict) and row.get("id") is not None:
            val_by_id[str(row["id"]).strip()] = row

    for (_id, _type), item in items_by_key.items():
        vrow = val_by_id.get(_id)
        if vrow is None:
            continue
        is_valid = vrow.get("valid")
        status_text = str(vrow.get("status") or vrow.get("deprecation_status") or "").upper()
        replacements_raw = vrow.get("replacements") or vrow.get("suggested_replacements") or vrow.get("consolidated_into")
        replacement_info = None
        if isinstance(replacements_raw, list) and replacements_raw:
            first_rep = replacements_raw[0]
            if isinstance(first_rep, dict) and first_rep.get("id") and first_rep.get("name"):
                replacement_info = {
                    "id": str(first_rep["id"]),
                    "name": str(first_rep["name"]),
                    "type": str(first_rep.get("type") or item["type"]),
                }
        elif isinstance(replacements_raw, dict) and replacements_raw.get("id") and replacements_raw.get("name"):
            replacement_info = {
                "id": str(replacements_raw["id"]),
                "name": str(replacements_raw["name"]),
                "type": str(replacements_raw.get("type") or item["type"]),
            }

        if is_valid is False or "DEPRECATED" in status_text or "CONSOLIDATED" in status_text or "INVALID" in status_text:
            item["validation_status"] = STATUS_UNAVAILABLE_OR_CONSOLIDATED
            item["validation_details"] = {
                "validated_via": val_endpoint,
                "valid": False,
                "reason": str(vrow.get("message") or vrow.get("reason") or status_text or "Meta targetingvalidation ushbu variantni yaroqsiz yoki birlashtirilgan deb topdi."),
                "consolidated_into": replacement_info,
                "checked_at": checked_at,
            }
        elif is_valid is True:
            item["validation_status"] = STATUS_VERIFIED_AVAILABLE
            item["validation_details"] = {
                "validated_via": val_endpoint,
                "valid": True,
                "reason": "Meta targetingvalidation orqali joriy akkauntda ishlashi tasdiqlandi.",
                "consolidated_into": None,
                "checked_at": checked_at,
            }

    return True, None


def search_and_validate_targeting(
    product: str = "",
    niche: str = "ecom",
    customer_profile: str = "",
    objective: str = "SALES",
    country: str = "UZ",
    language: str = "auto",
    queries: list[str] | None = None,
    ad_account_id: str = "",
    special_ad_category: str = "NONE",
    include_suggestions: bool = False,
    validate_results: bool = True,
    limit_per_query: int = 15,
    max_pages_per_query: int = 2,
    locale: str = "en_US",
    cache_path: Path | None = None,
    cache_ttl_seconds: int = 3600,
) -> dict[str, Any]:
    """Meta Ads Detailed Targeting variantlarini qidiradi, tekshiradi va 6 ta qat'iy holatga ajratgan hisobot qaytaradi."""
    api_version = get_graph_api_version()
    base_url = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    acct = normalize_account_id_optional(ad_account_id)
    spec_cat = str(special_ad_category or "NONE").strip().upper()
    if spec_cat not in SPECIAL_AD_CATEGORIES:
        raise ValueError(f"Noto'g'ri special_ad_category: {special_ad_category!r}. Ruxsat etilgan: {SPECIAL_AD_CATEGORIES}")

    detected_lang = detect_query_language(f"{product} {customer_profile} {' '.join(queries or [])}", explicit_lang=language)
    expanded_queries = expand_search_queries(
        product=product,
        niche=niche,
        customer_profile=customer_profile,
        extra_queries=queries,
    )

    cache_sig_raw = json.dumps({
        "product": product,
        "niche": niche,
        "customer_profile": customer_profile,
        "queries": [q["query"] for q in expanded_queries],
        "acct": acct,
        "validate": validate_results,
        "suggestions": include_suggestions,
        "locale": locale,
    }, sort_keys=True)
    cache_key = hashlib.sha256(cache_sig_raw.encode("utf-8")).hexdigest()[:24]

    cached_payload, cache_warning = _load_valid_cache(cache_path, cache_key, api_version, cache_ttl_seconds)
    if cached_payload is not None:
        cached_copy = json.loads(json.dumps(cached_payload))
        cached_copy["live_check_status"]["served_from_valid_cache"] = True
        return cached_copy

    # Build unverified related ideas (static niche seeds + solventnost hypotheses)
    # CRITICAL RULE: These ALWAYS have validation_status = RELATED_UNVERIFIED and can NEVER be promoted without live API proof!
    related_unverified_ideas: list[dict[str, Any]] = []
    for q_obj in expanded_queries:
        related_unverified_ideas.append({
            "candidate_term": q_obj["query"],
            "origin": q_obj["origin"],
            "validation_status": STATUS_RELATED_UNVERIFIED,
            "is_verified_meta_option": False,
            "explanation": "Qidiruv uchun shakllantirilgan nomzod ibora yoki statik klaster. Live API tasdig'isiz Ads Manager'da mavjud deb hisoblanmasin.",
        })
    for sh in SOLVENTNOST_HYPOTHESES:
        related_unverified_ideas.append({
            "candidate_term": sh["candidate_name"],
            "category_hint": sh["category_hint"],
            "validation_status": STATUS_RELATED_UNVERIFIED,
            "is_verified_meta_option": False,
            "hypothesis_type": sh["hypothesis_type"],
            "explanation": sh["note"],
        })

    limitations: list[str] = []
    if cache_warning:
        limitations.append(cache_warning)
    if spec_cat != "NONE":
        limitations.append(
            f"DIQQAT (Special Ad Category = {spec_cat}): Meta reklama siyosatiga ko'ra yosh, jins, pochta indeksi va ko'plab "
            "demografik/behavior targeting opsiyalari cheklangan. Ushbu cheklovlarni chetlab o'tishga urinmang!"
        )
    limitations.append(
        "To'lov qobiliyati (Solventnost — iPhone, xalqaro sayohat, Page Admin) signallari tasdiqlangan daromad filtri EMAS, "
        "balki kampaniyada A/B sinov orqali tekshiriladigan marketing gipotezasidir."
    )

    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not token or token == "your_meta_access_token_here":
        limitations.insert(
            0,
            "META_ACCESS_TOKEN o'rnatilmagan: Live Meta Graph API qidiruvi va targetingvalidation bajarilmadi (`API_UNAVAILABLE`). "
            "Statik va AI nomzod so'zlari faqat `RELATED_UNVERIFIED` sifatida berildi — ularni tasdiqlangan interest deb ishlatmang!",
        )
        return {
            "schema": "tyrion.detailed_targeting_accuracy/v5",
            "query_context": {
                "product": product,
                "niche": niche,
                "customer_profile": customer_profile,
                "objective": objective,
                "country": country.upper(),
                "detected_query_language": detected_lang,
                "ad_account_id": acct or None,
                "special_ad_category": spec_cat,
                "generated_search_queries": expanded_queries,
            },
            "live_check_status": {
                "executed": False,
                "status": STATUS_API_UNAVAILABLE,
                "error_category": "MISSING_TOKEN",
                "http_status": None,
                "error_message": "META_ACCESS_TOKEN muhit o'zgaruvchisi topilmadi.",
                "api_version": api_version,
                "checked_at": checked_at,
                "served_from_valid_cache": False,
            },
            "verified_targeting_options": [],
            "unavailable_or_consolidated_options": [],
            "related_unverified_ideas": related_unverified_ideas,
            "not_found_queries": [],
            "recommended_audience_combinations": {
                "status": "NO_VERIFIED_OPTIONS_AVAILABLE",
                "note": "Live API tekshiruvi bajarilmagani (`API_UNAVAILABLE`) sababli tasdiqlangan targeting kombinatsiyasi tuzilmadi. Avval `META_ACCESS_TOKEN` orqali live qidiruvni bajaring.",
                "combinations": [],
            },
            "limitations_and_disclosures": limitations,
        }

    headers = {"Authorization": f"Bearer {token}"}
    items_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    not_found_queries: list[dict[str, str]] = []
    api_failures: list[dict[str, Any]] = []

    safe_limit = tcore.safe_int(limit_per_query, default=15, min_val=1, max_val=100, field_name="limit_per_query")
    safe_max_pages = tcore.safe_int(max_pages_per_query, default=2, min_val=1, max_val=20, field_name="max_pages_per_query")

    for q_obj in expanded_queries:
        q_str = q_obj["query"]
        if acct:
            endpoint_label = f"GET /{api_version}/{acct}/targetingsearch"
            params = urllib.parse.urlencode({
                "q": q_str,
                "limit": str(safe_limit),
                "locale": locale,
            })
            url = f"{base_url}/{api_version}/{acct}/targetingsearch?{params}"
        else:
            endpoint_label = f"GET /{api_version}/search?type=adinterest"
            params = urllib.parse.urlencode({
                "type": "adinterest",
                "q": q_str,
                "limit": str(safe_limit),
                "locale": locale,
            })
            url = f"{base_url}/{api_version}/search?{params}"

        fetched = _fetch_paginated_endpoint(
            initial_url=url,
            base_url=base_url,
            headers=headers,
            max_pages=safe_max_pages,
        )
        if not fetched["ok"]:
            api_failures.append({
                "query": q_str,
                "endpoint": endpoint_label,
                "error": fetched["error"],
                "http_status": fetched.get("http_status"),
                "error_category": fetched.get("error_category", "API_ERROR"),
                "retries_attempted": fetched.get("retries_attempted", 0),
            })
            # Stop immediately on 401/403 auth/permission failure instead of hammering the API
            if fetched.get("error_category") in ("AUTH_401", "PERMISSION_403"):
                break
            continue

        raw_rows = fetched["items"]
        valid_rows_for_query = 0
        for row in raw_rows:
            raw_id = row.get("id")
            raw_name = row.get("name")
            if raw_id is None or raw_name is None or str(raw_id).strip() == "" or str(raw_name).strip() == "":
                continue
            item_id = str(raw_id).strip()
            item_name = str(raw_name)  # Preserve exact Meta name without translating or modifying!
            item_type = str(row.get("type") or "adinterest").strip()
            raw_path = row.get("path")
            item_path = [str(p) for p in raw_path] if isinstance(raw_path, list) else None

            lower_bound = _parse_optional_bound(row.get("audience_size_lower_bound"))
            upper_bound = _parse_optional_bound(row.get("audience_size_upper_bound"))

            dedup_key = (item_id, item_type.lower())
            valid_rows_for_query += 1

            # Check if the search payload itself marks the item as deprecated/invalid
            row_valid = row.get("valid")
            row_deprecated = bool(row.get("deprecated") or str(row.get("status", "")).upper() in ("DEPRECATED", "CONSOLIDATED", "INVALID"))
            initial_status = STATUS_UNAVAILABLE_OR_CONSOLIDATED if (row_valid is False or row_deprecated) else STATUS_FOUND_NOT_VALIDATED

            replacement_obj = None
            rep_raw = row.get("consolidated_into") or row.get("replacement")
            if isinstance(rep_raw, dict) and rep_raw.get("id") and rep_raw.get("name"):
                replacement_obj = {
                    "id": str(rep_raw["id"]),
                    "name": str(rep_raw["name"]),
                    "type": str(rep_raw.get("type") or item_type),
                }

            if dedup_key not in items_by_key:
                items_by_key[dedup_key] = {
                    "id": item_id,
                    "name": item_name,
                    "type": item_type,
                    "path": item_path,
                    "topic": row.get("topic"),
                    "description": row.get("description"),
                    "audience_size_lower_bound": lower_bound,
                    "audience_size_upper_bound": upper_bound,
                    "search_query": q_str,
                    "matched_queries": [q_str],
                    "source_endpoint": endpoint_label,
                    "api_version": api_version,
                    "checked_at": checked_at,
                    "validation_status": initial_status,
                    "validation_details": {
                        "validated_via": endpoint_label if initial_status == STATUS_UNAVAILABLE_OR_CONSOLIDATED else None,
                        "valid": False if initial_status == STATUS_UNAVAILABLE_OR_CONSOLIDATED else None,
                        "reason": (
                            str(row.get("deprecation_reason") or "Meta API ushbu opsiyani eskirgan yoki birlashtirilgan deb belgilagan.")
                            if initial_status == STATUS_UNAVAILABLE_OR_CONSOLIDATED
                            else "Rasmiy qidiruvdan topildi, ammo targetingvalidation hali bajarilmagan."
                        ),
                        "consolidated_into": replacement_obj,
                        "checked_at": checked_at,
                    },
                    "relevance_reason": _compute_relevance_reason(
                        item_name, item_type, item_path, q_str, product, niche, customer_profile
                    ),
                    "relevance_is_ai_opinion_not_meta_proof": True,
                }
            else:
                if q_str not in items_by_key[dedup_key]["matched_queries"]:
                    items_by_key[dedup_key]["matched_queries"].append(q_str)

        if valid_rows_for_query == 0:
            not_found_queries.append({
                "query": q_str,
                "source_endpoint": endpoint_label,
                "api_version": api_version,
                "checked_at": checked_at,
                "validation_status": STATUS_NOT_FOUND,
                "explanation": (
                    f"'{q_str}' so'rovi bo'yicha {endpoint_label} javobida 0 ta rasmiy natija qaytdi. "
                    "Eslatma: NOT_FOUND bu tushuncha Meta'da umuman yo'qligining mutlaq isboti emas, balki ayni so'rov bo'yicha topilmaganini bildiradi."
                ),
            })

    # If every query failed with an API error and 0 items were retrieved, report API_UNAVAILABLE honestly
    if api_failures and not items_by_key and not not_found_queries:
        first_fail = api_failures[0]
        limitations.insert(
            0,
            f"Live Meta Graph API so'rovi xato bilan tugadi ({first_fail['error_category']}): {first_fail['error']}. "
            "Hech qanday statik yoki AI variant tasdiqlangan (`VERIFIED_AVAILABLE`) deb belgilangani yo'q!",
        )
        return {
            "schema": "tyrion.detailed_targeting_accuracy/v5",
            "query_context": {
                "product": product,
                "niche": niche,
                "customer_profile": customer_profile,
                "objective": objective,
                "country": country.upper(),
                "detected_query_language": detected_lang,
                "ad_account_id": acct or None,
                "special_ad_category": spec_cat,
                "generated_search_queries": expanded_queries,
            },
            "live_check_status": {
                "executed": False,
                "status": STATUS_API_UNAVAILABLE,
                "error_category": first_fail["error_category"],
                "http_status": first_fail.get("http_status"),
                "error_message": first_fail["error"],
                "api_version": api_version,
                "checked_at": checked_at,
                "served_from_valid_cache": False,
                "api_failures": api_failures,
            },
            "verified_targeting_options": [],
            "unavailable_or_consolidated_options": [],
            "related_unverified_ideas": related_unverified_ideas,
            "not_found_queries": [],
            "recommended_audience_combinations": {
                "status": "NO_VERIFIED_OPTIONS_AVAILABLE",
                "note": "API xatosi (`API_UNAVAILABLE`) sababli tasdiqlangan variantlar olinmadi.",
                "combinations": [],
            },
            "limitations_and_disclosures": limitations,
        }

    # Optional Step B: Account-scoped targetingsuggestions
    if include_suggestions and acct and items_by_key:
        seed_list = [
            {"id": it["id"], "type": it["type"]}
            for it in list(items_by_key.values())[:5]
            if it["validation_status"] != STATUS_UNAVAILABLE_OR_CONSOLIDATED
        ]
        if seed_list:
            sug_endpoint = f"GET /{api_version}/{acct}/targetingsuggestions"
            sug_params = urllib.parse.urlencode({
                "targeting_list": json.dumps(seed_list, ensure_ascii=False),
                "limit": str(safe_limit),
            })
            sug_url = f"{base_url}/{api_version}/{acct}/targetingsuggestions?{sug_params}"
            sug_fetched = _fetch_paginated_endpoint(sug_url, base_url, headers, max_pages=1)
            if sug_fetched["ok"]:
                for row in sug_fetched["items"]:
                    raw_id = row.get("id")
                    raw_name = row.get("name")
                    if not raw_id or not raw_name:
                        continue
                    s_id = str(raw_id).strip()
                    s_name = str(raw_name)
                    s_type = str(row.get("type") or "interests").strip()
                    s_key = (s_id, s_type.lower())
                    if s_key not in items_by_key:
                        s_path = [str(p) for p in row["path"]] if isinstance(row.get("path"), list) else None
                        items_by_key[s_key] = {
                            "id": s_id,
                            "name": s_name,
                            "type": s_type,
                            "path": s_path,
                            "topic": row.get("topic"),
                            "description": row.get("description"),
                            "audience_size_lower_bound": _parse_optional_bound(row.get("audience_size_lower_bound")),
                            "audience_size_upper_bound": _parse_optional_bound(row.get("audience_size_upper_bound")),
                            "search_query": "targetingsuggestions_seed",
                            "matched_queries": ["targetingsuggestions_seed"],
                            "source_endpoint": sug_endpoint,
                            "api_version": api_version,
                            "checked_at": checked_at,
                            "validation_status": STATUS_FOUND_NOT_VALIDATED,
                            "validation_details": {
                                "validated_via": None,
                                "valid": None,
                                "reason": "Meta targetingsuggestions endpointidan olindi; targetingvalidation hali bajarilmagan.",
                                "consolidated_into": None,
                                "checked_at": checked_at,
                            },
                            "relevance_reason": _compute_relevance_reason(
                                s_name, s_type, s_path, "targetingsuggestions", product, niche, customer_profile
                            ),
                            "relevance_is_ai_opinion_not_meta_proof": True,
                        }
            else:
                limitations.append(f"targetingsuggestions qo'shimcha so'rovi bajarilmadi: {sug_fetched['error']}")

    # Step C: Account-scoped targetingvalidation
    validation_executed = False
    if validate_results and acct and items_by_key:
        validation_executed, val_err = _run_targeting_validation(
            base_url=base_url,
            api_version=api_version,
            account_id=acct,
            headers=headers,
            items_by_key=items_by_key,
            checked_at=checked_at,
        )
        if val_err:
            limitations.append(val_err)
    elif not acct:
        limitations.insert(
            0,
            "Reklama akkaunt ID si (`--account-id act_...`) berilmagani sababli global `/search?type=adinterest` ishlatildi va "
            "`/{ad-account-id}/targetingvalidation` bajarilmadi. Topilgan rasmiy natijalar `FOUND_NOT_VALIDATED` holatida qoldirildi.",
        )

    verified_options: list[dict[str, Any]] = []
    unavailable_options: list[dict[str, Any]] = []

    for item in items_by_key.values():
        if item["validation_status"] == STATUS_UNAVAILABLE_OR_CONSOLIDATED:
            unavailable_options.append(item)
        else:
            verified_options.append(item)

    # Filter out any related_unverified_ideas whose exact name was already found in official API results
    found_names_lower = {it["name"].lower() for it in verified_options}
    filtered_unverified = [
        idea for idea in related_unverified_ideas
        if idea["candidate_term"].lower() not in found_names_lower
    ]

    # Build Recommended Audience Combinations strictly from verified/found official options
    strictly_verified = [it for it in verified_options if it["validation_status"] == STATUS_VERIFIED_AVAILABLE]
    usable_pool = strictly_verified if strictly_verified else verified_options
    combinations: list[dict[str, Any]] = []
    if usable_pool:
        pool_status = STATUS_VERIFIED_AVAILABLE if strictly_verified else STATUS_FOUND_NOT_VALIDATED
        core_slice = usable_pool[:5]
        combinations.append({
            "layer_name": "L2_Official_Meta_Detailed_Targeting_Stack",
            "options_status": pool_status,
            "requires_validation_before_launch": (pool_status != STATUS_VERIFIED_AVAILABLE),
            "included_options": [
                {
                    "id": it["id"],
                    "name": it["name"],
                    "type": it["type"],
                    "validation_status": it["validation_status"],
                    "source_endpoint": it["source_endpoint"],
                }
                for it in core_slice
            ],
            "recommended_exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
        })
        combo_block = {
            "status": "BUILT_FROM_OFFICIAL_API_RESULTS",
            "source_validation_status": pool_status,
            "note": (
                "Kombinatsiya faqat Meta Graph API va targetingvalidation tasdiqlagan (`VERIFIED_AVAILABLE`) variantlardan tuzildi."
                if pool_status == STATUS_VERIFIED_AVAILABLE
                else "DIQQAT: Kombinatsiya rasmiy Meta Graph API qidiruvidan topilgan (`FOUND_NOT_VALIDATED`) variantlardan tuzildi — "
                     "kampaniyani yoqishdan oldin `--account-id act_...` bilan `targetingvalidation` tekshiruvidan o'tkazing."
            ),
            "combinations": combinations,
        }
    else:
        combo_block = {
            "status": "NO_VERIFIED_OPTIONS_AVAILABLE",
            "source_validation_status": STATUS_NOT_FOUND,
            "note": "Rasmiy API qidiruvida tasdiqlangan variant topilmagani sababli kombinatsiya tuzilmadi (tasdiqlanmagan AI g'oyalaridan kombinatsiya qurish taqiqlangan).",
            "combinations": [],
        }

    result_payload = {
        "schema": "tyrion.detailed_targeting_accuracy/v5",
        "query_context": {
            "product": product,
            "niche": niche,
            "customer_profile": customer_profile,
            "objective": objective,
            "country": country.upper(),
            "detected_query_language": detected_lang,
            "ad_account_id": acct or None,
            "special_ad_category": spec_cat,
            "generated_search_queries": expanded_queries,
        },
        "live_check_status": {
            "executed": True,
            "status": "LIVE_SEARCH_AND_VALIDATION_COMPLETED" if validation_executed else "LIVE_SEARCH_ONLY_NO_VALIDATION",
            "validation_executed": validation_executed,
            "error_category": "PARTIAL_QUERY_ERRORS" if api_failures else "NONE",
            "api_version": api_version,
            "checked_at": checked_at,
            "served_from_valid_cache": False,
            "counts": {
                "verified_available": sum(1 for x in verified_options if x["validation_status"] == STATUS_VERIFIED_AVAILABLE),
                "found_not_validated": sum(1 for x in verified_options if x["validation_status"] == STATUS_FOUND_NOT_VALIDATED),
                "unavailable_or_consolidated": len(unavailable_options),
                "related_unverified": len(filtered_unverified),
                "not_found_queries": len(not_found_queries),
            },
            "partial_api_failures": api_failures,
        },
        "verified_targeting_options": verified_options,
        "unavailable_or_consolidated_options": unavailable_options,
        "related_unverified_ideas": filtered_unverified,
        "not_found_queries": not_found_queries,
        "recommended_audience_combinations": combo_block,
        "limitations_and_disclosures": limitations,
    }

    if not api_failures:
        _save_cache(
            cache_path=cache_path,
            cache_key=cache_key,
            api_version=api_version,
            ttl_seconds=cache_ttl_seconds,
            query_params={"product": product, "niche": niche, "acct": acct},
            payload=result_payload,
        )

    return result_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="meta-targeting-engine.py",
        description="Tyrion v5.0 Meta Ads Detailed Targeting Accuracy Engine (Zero Hallucinated Interests)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Mahsulot/nisha bo'yicha Detailed Targeting variantlarini rasmiy Meta API orqali qidirish va tekshirish")
    p_search.add_argument("--product", default="", help="Mahsulot yoki xizmat tavsifi (masalan: 'Klassik erkaklar kostyumi' yoki 'Стоматология Ташкент')")
    p_search.add_argument("--niche", default="ecom", choices=list(NICHE_SEED_CANDIDATES.keys()))
    p_search.add_argument("--customer-profile", default="", help="Maqsadli mijoz profili")
    p_search.add_argument("--objective", default="SALES", choices=["SALES", "LEADS", "ENGAGEMENT", "TRAFFIC", "AWARENESS"])
    p_search.add_argument("--country", default="UZ")
    p_search.add_argument("--language", default="auto", choices=["auto", "uz_latin", "uz_cyrillic", "ru", "en"])
    p_search.add_argument("--query", action="append", default=[], help="Aniq qidiruv so'rovi (bir nechta berish mumkin)")
    p_search.add_argument("--account-id", default="", help="Meta Ad Account ID (`act_...`) — targetingsearch va targetingvalidation uchun")
    p_search.add_argument("--special-ad-category", default="NONE", choices=list(SPECIAL_AD_CATEGORIES))
    p_search.add_argument("--suggestions", action="store_true", help="`/{act_id}/targetingsuggestions` endpointini ham chaqirish")
    p_search.add_argument("--no-validate", action="store_true", help="`targetingvalidation` qadamini o'tkazib yuborish")
    p_search.add_argument("--limit", type=int, default=15)
    p_search.add_argument("--max-pages", type=int, default=2)
    p_search.add_argument("--locale", default="en_US")
    p_search.add_argument("--cache-file", default="", help="Ixtiyoriy TTL kesh fayli yo'li")
    p_search.add_argument("--cache-ttl", type=int, default=3600, help="Kesh yaroqlilik muddati (soniya)")
    p_search.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        cpath = Path(args.cache_file) if args.cache_file else None
        res = search_and_validate_targeting(
            product=args.product,
            niche=args.niche,
            customer_profile=args.customer_profile,
            objective=args.objective,
            country=args.country,
            language=args.language,
            queries=args.query,
            ad_account_id=args.account_id,
            special_ad_category=args.special_ad_category,
            include_suggestions=args.suggestions,
            validate_results=not args.no_validate,
            limit_per_query=args.limit,
            max_pages_per_query=args.max_pages,
            locale=args.locale,
            cache_path=cpath,
            cache_ttl_seconds=args.cache_ttl,
        )
    except Exception as exc:
        print(f"Xato: {tcore.redact_secrets(str(exc))}", file=sys.stderr)
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    lcs = res["live_check_status"]
    print("=" * 76)
    print("  🎯 TYRION DETAILED TARGETING ACCURACY REPORT")
    print("=" * 76)
    print(f"  1. LIVE TEKSHIRUV HOLATI : {lcs['status']} (executed={lcs['executed']}, API={lcs['api_version']}, vaqt={lcs['checked_at']})")
    if lcs.get("error_message"):
        print(f"     Sabab / Xato          : [{lcs.get('error_category')}] {lcs['error_message']}")
    print(f"\n  2. TASDIQLANGAN / RASMIY TOPILGAN VARIANTLAR ({len(res['verified_targeting_options'])} ta):")
    if not res["verified_targeting_options"]:
        print("     • (Rasmiy API dan tasdiqlangan variant yo'q)")
    for it in res["verified_targeting_options"]:
        bounds = (
            f"hajm: {it['audience_size_lower_bound']:,}..{it['audience_size_upper_bound']:,}"
            if it["audience_size_lower_bound"] is not None and it["audience_size_upper_bound"] is not None
            else "hajm: API qaytarmagan"
        )
        print(f"     • [{it['validation_status']}] {it['name']} (id={it['id']}, type={it['type']}, {bounds})")
        print(f"       Manba: {it['source_endpoint']} | So'rov: '{it['search_query']}'")

    if res["unavailable_or_consolidated_options"]:
        print(f"\n  3. ESKIRGAN YOKI BIRLASHTIRILGAN VARIANTLAR ({len(res['unavailable_or_consolidated_options'])} ta):")
        for it in res["unavailable_or_consolidated_options"]:
            rep = (it.get("validation_details") or {}).get("consolidated_into")
            rep_str = f" -> Yangi variant: {rep['name']} (id={rep['id']})" if isinstance(rep, dict) else ""
            print(f"     • [{it['validation_status']}] {it['name']} (id={it['id']}){rep_str}")

    print(f"\n  4. TASDIQLANMAGAN, LEKIN MAZMUNAN MOS G'OYALAR ({len(res['related_unverified_ideas'])} ta):")
    for idea in res["related_unverified_ideas"][:8]:
        print(f"     • [{idea['validation_status']}] {idea['candidate_term']} — {idea['explanation']}")

    if res["not_found_queries"]:
        print(f"\n  5. RASMIY NATIJA TOPILMAGAN SO'ROVLAR ({len(res['not_found_queries'])} ta):")
        for nf in res["not_found_queries"]:
            print(f"     • [{nf['validation_status']}] '{nf['query']}' ({nf['source_endpoint']})")

    combo = res["recommended_audience_combinations"]
    print(f"\n  6. TAVSIYA ETILGAN AUDITORIYA KOMBINATSIYASI: {combo['status']}")
    print(f"     {combo['note']}")
    print("\n  7. CHEKLOVLAR VA IZOHLAR:")
    for lim in res["limitations_and_disclosures"]:
        print(f"     • {lim}")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
