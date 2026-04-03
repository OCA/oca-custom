#!/usr/bin/env python
# Usage: click-odoo -d <database> 003_reset_default_avatar.py
# claude.ai generated

import click, click_odoo

import base64
import hashlib
import urllib.request

import logging
_logger = logging.getLogger(__file__)

BATCH_SIZE = 100
DEFAULT_AVATAR_URLS = [
    "https://oca.akretion.com/web/image/res.partner/11567/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/8624/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/5835/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/2889/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/7815/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/8761/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/9951/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/66292/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/11580/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/843/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/9939/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/10297/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/1520/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/14321/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/11671/avatar_1920",
    "https://oca.akretion.com/web/image/res.partner/11518/avatar_1920",
]

@click.command()
@click_odoo.env_options(default_log_level='info')
def main(env):
    _reset_default_avatar(env)

def _reset_default_avatar(env):
    # 1. Récupérer les hash des avatars par défaut
    default_hashes = get_default_avatar_hashes()
    if not default_hashes:
        _logger.error("Aucun hash récupéré, abandon.")
        return

    # 2. Récupérer tous les IDs concernés
    all_ids = iter_partner_ids(env)
    if not all_ids:
        _logger.info("Aucun partenaire avec une image_1920, rien à faire.")
        return
    
    # 3. Traitement par batch avec commit intermédiaire
    total = len(all_ids)
    total_cleaned = 0
    batch_count = (total + BATCH_SIZE - 1) // BATCH_SIZE  # ceil division

    _logger.info(
        "Démarrage du traitement : %d partenaire(s) en %d batch(s) de %d.",
        total,
        batch_count,
        BATCH_SIZE,
    )

    for batch_num, offset in enumerate(range(0, total, BATCH_SIZE), start=1):
        batch_ids = all_ids[offset : offset + BATCH_SIZE]
        _logger.info(
            "Batch %d/%d : partenaires %d à %d...",
            batch_num,
            batch_count,
            offset + 1,
            min(offset + BATCH_SIZE, total),
        )

        cleaned = process_batch(env, batch_ids, default_hashes)
        total_cleaned += cleaned

        # Commit après chaque batch pour libérer les locks et sauvegarder
        # progressivement (sans --rollback, sinon le commit est ignoré)
        env.cr.commit()
        _logger.info(
            "  Batch %d/%d terminé : %d remis à zéro (total : %d/%d).",
            batch_num,
            batch_count,
            cleaned,
            total_cleaned,
            total,
        )

    _logger.info(
        "=== Nettoyage terminé : %d/%d partenaire(s) remis à zéro. ===",
        total_cleaned,
        total,
    )


def get_default_avatar_hashes():
    """
    Retourne un set de hash MD5 des images téléchargées depuis les URLs.
    On hash les bytes bruts (décodés depuis la réponse HTTP).
    """
    hashes = {}  # hash -> url (pour les logs)
    _logger.info("Téléchargement des %d avatars par défaut...", len(DEFAULT_AVATAR_URLS))
    for url in DEFAULT_AVATAR_URLS:
        md5, image_bytes = fetch_image_hash(url)
        if md5:
            hashes[md5] = url
            _logger.info("  ✓ %s -> %s", url.split("/")[7], md5)  # partner id
        else:
            _logger.warning("  ✗ Échec pour %s", url)
    _logger.info("%d hash récupérés.", len(hashes))
    return hashes

def fetch_image_hash(url):
    """Télécharge une image depuis une URL et retourne son hash MD5."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            image_bytes = response.read()
        return hashlib.md5(image_bytes).hexdigest(), image_bytes
    except Exception as e:
        _logger.error("Impossible de télécharger l'image depuis %s : %s", url, e)
        return None, None

def iter_partner_ids(env):
    """Retourne la liste complète des IDs de res.partner ayant une image_1920."""
    _logger.info("Récupération des IDs des partenaires avec une image_1920 définie...")
    # On ne récupère que les IDs pour ne pas tout charger en mémoire
    partners = env["res.partner"].with_context(active_test=False).search(
        [("image_1920", "!=", False)]
    )
    ids = partners.ids
    _logger.info("%d partenaire(s) trouvé(s) avec une image_1920.", len(ids))
    return ids

def process_batch(env, partner_ids, default_hashes):
    """
    Traite un batch de partenaires.
    Retourne le nombre de partenaires remis à zéro dans ce batch.
    """
    cleaned = 0
    partners = env["res.partner"].browse(partner_ids)

    for partner in partners:
        try:
            image_b64 = partner.image_1920
            if not image_b64:
                continue

            if isinstance(image_b64, bytes):
                image_bytes = base64.b64decode(image_b64)
            else:
                image_bytes = base64.b64decode(image_b64.encode())

            image_md5 = hashlib.md5(image_bytes).hexdigest()

            if image_md5 in default_hashes:
                _logger.info(
                    "  → Partenaire %d (%s) : correspond à l'avatar par défaut %s -> remise à zéro.",
                    partner.id,
                    partner.display_name,
                    default_hashes[image_md5],
                )
                partner.image_1920 = False
                cleaned += 1

        except Exception as e:
            _logger.error(
                "  ✗ Erreur partenaire %d (%s) : %s",
                partner.id,
                partner.display_name,
                e,
            )

    return cleaned

if __name__ == "__main__":
    main()
