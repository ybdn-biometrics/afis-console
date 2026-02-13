import os
import shutil
import fitz  # PyMuPDF
import re

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

def check_homonym_counts(pdf_path: str) -> bool:
    """
    Retourne True si le document contient "Section/identités" ET qu'au moins
    une ligne "- nombre d'homonymes" contient une valeur > 0.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        # Normalisation pour verification
        lower_text = full_text.lower()

        # Si pas de section identités, on ignore cette vérification (donc pas de détection d'homonyme par cette méthode)
        if "section / identités" not in lower_text and "section/identités" not in lower_text:
            return False

        # Regex pour capturer la valeur après "nombre d'homonymes"
        # Supporte :
        # - nombre d'homonymes : 0
        # - nombre d'homonymes :\n0
        # - nombre d'homonymes 0
        pattern = r"nombre\s+d[’']homonymes\s*[:\s]\s*(\d+)"
        matches = re.finditer(pattern, lower_text)

        for match in matches:
            try:
                val = int(match.group(1))
                if val > 0:
                    return True
            except ValueError:
                continue
        
        return False
    except Exception as e:
        print(f"  ⚠ Erreur lecture (check identités) {os.path.basename(pdf_path)}: {e}")
        return False

def process_folder(source_dir: str, log_callback=None, destination_dir: str = None):
    """
    Traite le dossier source.
    log_callback(msg: str) : fonction pour remonter les logs.
    destination_dir: Dossier de destination optionnel.
    Retourne un dict stats ou None si erreur critique.
    """
    if not log_callback:
        log_callback = print

    if not os.path.isdir(source_dir):
        log_callback(f"Erreur : '{source_dir}' n'est pas un dossier valide.")
        return None

    # Determine destination base
    base_dest = destination_dir if destination_dir else source_dir
    if not os.path.isdir(base_dest):
         try:
             os.makedirs(base_dest, exist_ok=True)
         except Exception as e:
             log_callback(f"Erreur création dossier destination : {e}")
             return None

    # Créer les dossiers de destination
    dir_ok = os.path.join(base_dest, "Pas_d_homonyme")
    dir_manual = os.path.join(base_dest, "Homonymes_detectes")
    os.makedirs(dir_ok, exist_ok=True)
    os.makedirs(dir_manual, exist_ok=True)

    # Lister les PDFs
    pdfs = [f for f in os.listdir(source_dir)
            if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(source_dir, f))]

    if not pdfs:
        log_callback("Aucun fichier PDF trouvé dans le dossier source.")
        return {"ok": 0, "manual": 0, "error": 0}

    log_callback(f"📂 {len(pdfs)} PDF(s) trouvé(s) dans '{source_dir}'\n")
    if destination_dir:
        log_callback(f"↪️  Destination : '{destination_dir}'\n")

    stats = {"ok": 0, "manual": 0, "error": 0}

    for filename in sorted(pdfs):
        filepath = os.path.join(source_dir, filename)
        
        # Logique 1 : Page 1 "Homonymes ... non"
        res_p1 = has_no_homonyme(filepath)
        
        # Logique 2 : Section identités, count > 0
        res_ident = check_homonym_counts(filepath)

        destination_dir_final = dir_manual
        message = ""
        is_manual = False

        if res_p1 is None:
            # Erreur technique sur la lecture page 1
            destination_dir_final = dir_manual
            message = "⚠️  (erreur lecture)"
            stats["error"] += 1
            is_manual = True # On considère erreur comme manuel pour le déplacement
        elif res_p1 is False:
            # Detecté par logique 1
            destination_dir_final = dir_manual
            message = "🔶 (detecté par page 1)"
            stats["manual"] += 1
            is_manual = True
        elif res_ident is True:
            # Detecté par logique 2 (valeur > 0 dans section identités)
            destination_dir_final = dir_manual
            message = "🔶 (detecté par section identités)"
            stats["manual"] += 1
            is_manual = True
        else:
            # Tout est clean
            destination_dir_final = dir_ok
            message = "✅"
            stats["ok"] += 1
            is_manual = False

        try:
            shutil.move(filepath, os.path.join(destination_dir_final, filename))
            log_callback(f"{message} {filename} → {os.path.basename(destination_dir_final)}/")
        except Exception as e:
            log_callback(f"❌ Erreur déplacement {filename}: {e}")

    log_callback(f"\n{'='*50}")
    log_callback(f"📊 Résultat :")
    log_callback(f"   ✅ Pas d'homonyme     : {stats['ok']}")
    log_callback(f"   🔶 Homonymes détectés : {stats['manual']}")
    log_callback(f"   ⚠️  Erreurs            : {stats['error']}")
    log_callback(f"{'='*50}")
    
    return stats
