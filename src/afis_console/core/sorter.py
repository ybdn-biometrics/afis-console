import os
import shutil
import fitz  # PyMuPDF

def has_no_homonyme(pdf_path: str) -> bool | None:
    """
    Analyse la page 1 du PDF via extraction par mots (avec positions).
    Le "non" après "Homonymes" est souvent dans un bloc séparé mais sur
    la même ligne (même coordonnée Y). On vérifie donc que "non" apparaît
    sur la même ligne que "Homonymes" dans le PDF.
    Retourne True si "Homonymes ... non" sur la même ligne, False sinon, None si erreur.
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return None
        page = doc[0]
        words = page.get_text('words')  # (x0, y0, x1, y1, mot, bloc, ligne, mot_idx)
        doc.close()

        # Trouver le mot "Homonymes" et sa position Y
        homonyme_y = None
        for w in words:
            if 'homonyme' in w[4].lower():
                homonyme_y = w[1]  # coordonnée Y du haut du mot
                break

        if homonyme_y is None:
            # Pas de mention d'homonymes → traitement manuel
            return False

        # Chercher "non" sur la même ligne (tolérance de 3px sur Y)
        tolerance = 3
        for w in words:
            if w[4].lower() == 'non' and abs(w[1] - homonyme_y) <= tolerance:
                return True

        return False
    except Exception as e:
        print(f"  ⚠ Erreur lecture {os.path.basename(pdf_path)}: {e}")
        return None

def process_folder(source_dir: str, log_callback=None):
    """
    Traite le dossier source.
    log_callback(msg: str) : fonction pour remonter les logs.
    Retourne un dict stats ou None si erreur critique.
    """
    if not log_callback:
        log_callback = print

    if not os.path.isdir(source_dir):
        log_callback(f"Erreur : '{source_dir}' n'est pas un dossier valide.")
        return None

    # Créer les dossiers de destination
    dir_ok = os.path.join(source_dir, "Pas_d_homonyme")
    dir_manual = os.path.join(source_dir, "Homonymes_detectes")
    os.makedirs(dir_ok, exist_ok=True)
    os.makedirs(dir_manual, exist_ok=True)

    # Lister les PDFs
    pdfs = [f for f in os.listdir(source_dir)
            if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(source_dir, f))]

    if not pdfs:
        log_callback("Aucun fichier PDF trouvé dans le dossier.")
        return {"ok": 0, "manual": 0, "error": 0}

    log_callback(f"📂 {len(pdfs)} PDF(s) trouvé(s) dans '{source_dir}'\n")

    stats = {"ok": 0, "manual": 0, "error": 0}

    for filename in sorted(pdfs):
        filepath = os.path.join(source_dir, filename)
        result = has_no_homonyme(filepath)

        if result is True:
            shutil.move(filepath, os.path.join(dir_ok, filename))
            log_callback(f"✅ {filename} → Pas_d_homonyme/")
            stats["ok"] += 1
        elif result is False:
            shutil.move(filepath, os.path.join(dir_manual, filename))
            log_callback(f"🔶 {filename} → Homonymes_detectes/")
            stats["manual"] += 1
        else:
            shutil.move(filepath, os.path.join(dir_manual, filename))
            log_callback(f"⚠️  {filename} → Homonymes_detectes/ (erreur lecture)")
            stats["error"] += 1

    log_callback(f"\n{'='*50}")
    log_callback(f"📊 Résultat :")
    log_callback(f"   ✅ Pas d'homonyme     : {stats['ok']}")
    log_callback(f"   🔶 Homonymes détectés : {stats['manual']}")
    log_callback(f"   ⚠️  Erreurs            : {stats['error']}")
    log_callback(f"{'='*50}")
    
    return stats
