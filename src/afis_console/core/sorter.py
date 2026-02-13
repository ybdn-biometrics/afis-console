import os
import shutil
import fitz  # PyMuPDF
import re
import unicodedata
from datetime import datetime

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

def _normalize_name(name: str) -> str:
    """
    Normalise un nom pour comparaison :
    - Supprime accents, tirets, apostrophes
    - Passe en majuscule
    - Supprime les espaces multiples
    """
    # Décomposer les caractères Unicode et supprimer les diacritiques
    nfkd = unicodedata.normalize('NFKD', name)
    without_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Supprimer tirets, apostrophes, caractères spéciaux
    cleaned = re.sub(r"[\-''`]", ' ', without_accents)
    # Majuscule, supprimer espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().upper()
    return cleaned

def extract_main_identity(pdf_path: str) -> str | None:
    """
    Extrait l'identité principale de la page 1 du PDF.
    C'est le nom affiché après 'Recherches dactyloscopiques concernant :'.
    Retourne le nom (str) ou None si non trouvé.
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return None
        page = doc[0]
        text = page.get_text()
        doc.close()

        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'recherches dactyloscopiques concernant' in line.lower():
                if i + 1 < len(lines):
                    name = lines[i + 1].strip()
                    if name and len(name) > 1:
                        return name
        return None
    except Exception:
        return None

def extract_alias_names(pdf_path: str) -> list[str]:
    """
    Extrait les noms d'alias listés dans la SECTION / Identités,
    après la phrase 'est connu(e) sous les identités suivantes :'.
    Retourne une liste de noms (str).
    """
    try:
        doc = fitz.open(pdf_path)
        text = ''
        for p in doc:
            text += p.get_text()
        doc.close()

        lines = text.split('\n')
        aliases = []
        in_alias_section = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Début de la zone d'alias
            if 'est connu(e) sous les identités suivantes' in stripped.lower():
                in_alias_section = True
                continue

            # Fin de la zone d'alias
            if in_alias_section and 'section / signalisations' in stripped.lower():
                break
            if in_alias_section and stripped.lower().startswith('nombre d') and 'homonymes' in stripped.lower():
                # Ligne finale de résumé (hors alias individuels)
                if 'indique' in text.split('\n')[min(i+1, len(lines)-1)].lower():
                    break

            if not in_alias_section:
                continue

            # Détecter les noms d'alias :
            # - Tout en majuscule, pas de chiffres, pas un label technique
            if (stripped
                and stripped == stripped.upper()
                and not any(c.isdigit() for c in stripped)
                and len(stripped) > 2
                and 'nombre' not in stripped.lower()
                and 'signalisation' not in stripped.lower()
                and 'section' not in stripped.lower()
                and 'homonyme' not in stripped.lower()
                and 'né(e)' not in stripped.lower()
                and 'reproduction' not in stripped.lower()
                and 'sae' not in stripped.lower()
                and 'pays' not in stripped.lower()):
                aliases.append(stripped)

        return aliases
    except Exception:
        return []

def check_identity_mismatch(pdf_path: str) -> dict:
    """
    Compare l'identité de la page 1 avec les alias de la section identités.
    Retourne un dict:
        {
            'main_identity': str | None,
            'aliases': list[str],
            'has_mismatch': bool,      # True si l'identité n'est PAS dans les alias
            'has_identity_section': bool
        }
    """
    main_id = extract_main_identity(pdf_path)
    aliases = extract_alias_names(pdf_path)

    if not main_id or not aliases:
        return {
            'main_identity': main_id,
            'aliases': aliases,
            'has_mismatch': False,  # Pas de section = pas d'erreur état civil
            'has_identity_section': len(aliases) > 0
        }

    main_norm = _normalize_name(main_id)
    alias_norms = [_normalize_name(a) for a in aliases]

    has_mismatch = main_norm not in alias_norms

    return {
        'main_identity': main_id,
        'aliases': aliases,
        'has_mismatch': has_mismatch,
        'has_identity_section': True
    }

def extract_identities_details(pdf_path: str) -> list:
    """
    Extrait les détails des identités/alias et leur nombre d'homonymes.
    Retourne une liste de dicts: [{'alias': 'NOM PRENOM', 'count': 0}, ...]
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        text_lower = text.lower()
        
        # Regex pour capturer la valeur après "nombre d'homonymes"
        pattern_count = r"nombre\s+d[’']homonymes\s*[:\s]\s*(\d+)"
        matches = list(re.finditer(pattern_count, text_lower))
        
        identities = []
        last_pos = 0
        
        for m in matches:
            count = int(m.group(1))
            start_pos = m.start()
            
            # Chercher "né(e) le" avant cette occurrence pour délimiter le bloc
            subtext = text_lower[last_pos:start_pos]
            ne_le_matches = list(re.finditer(r"né\(e\)\s+le", subtext))
            
            alias_name = "Non identifié"
            if ne_le_matches:
                block_start_rel = ne_le_matches[-1].start()
                block_start_abs = last_pos + block_start_rel
                
                # Extraire le morceau de texte entre "né(e) le" et le compteur
                chunk = text[block_start_abs:start_pos]
                lines_in_chunk = chunk.split('\n')
                # Nettoyage des lignes vides
                lines_in_chunk = [l.strip() for l in lines_in_chunk if l.strip()]
                
                # Heuristique : Ligne 0 = "Né(e) le ...", Ligne 1 = NOM PRENOM
                if len(lines_in_chunk) > 1:
                    possible_name = lines_in_chunk[1]
                    # Petit filtre pour éviter de prendre des labels techniques
                    if "signalisation" not in possible_name.lower() and len(possible_name) > 2:
                         alias_name = possible_name
            
            identities.append({
                'alias': alias_name,
                'count': count
            })
            
            last_pos = start_pos + len(m.group(0))

        return identities
    except Exception as e:
        print(f"  ⚠ Erreur extraction identités {os.path.basename(pdf_path)}: {e}")
        return []

def check_homonym_counts(pdf_path: str) -> bool:
    """
    Retourne True si 'Section/identités' est présente ET qu'au moins 
    une ligne 'nombre d'homonymes' > 0.
    Utilise extract_identities_details en interne.
    """
    identities = extract_identities_details(pdf_path)
    # On vérifie aussi la présence de la section textuelle pour être cohérent avec l'ancienne logique
    # Mais ici, si on a trouvé des identités avec un count > 0, c'est qu'il y a homonyme.
    for identity in identities:
        if identity['count'] > 0:
            return True
    return False

def generate_html_report(destination_dir, stats, file_details):
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    
    html_content = f"""
    <html>
    <head>
        <title>Recherche d'homonymes - Rapport</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .metadata {{ color: #7f8c8d; font-style: italic; margin-bottom: 20px; }}
            .summary-box {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
            th {{ background-color: #34495e; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .status-ok {{ color: green; font-weight: bold; }}
            .status-warning {{ color: orange; font-weight: bold; }}
            .status-error {{ color: red; font-weight: bold; }}
            .status-identity {{ color: #8e44ad; font-weight: bold; }}
            .alias-list {{ margin: 0; padding-left: 20px; font-size: 0.9em; }}
            .badge-homonym {{ background-color: #e74c3c; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }}
            .badge-clean {{ background-color: #27ae60; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }}
            .badge-mismatch {{ background-color: #8e44ad; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <h1>Recherche d'homonymes</h1>
        <div class="metadata">
            <strong>DFAED - Rapports de signalisation</strong><br>
            Traitement effectué le {timestamp}
        </div>

        <h2>1. Rapport général du traitement</h2>
        <div class="summary-box">
            <p><strong>Total analysé :</strong> {stats['ok'] + stats['manual'] + stats['error'] + stats['identity_error']}</p>
            <p><span class="status-ok">✔ Pas d'homonyme :</span> {stats['ok']}</p>
            <p><span class="status-warning">⚠ Homonymes détectés :</span> {stats['manual']}</p>
            <p><span class="status-identity">🔴 Erreur état civil :</span> {stats['identity_error']}</p>
            <p><span class="status-error">✖ Erreurs de lecture :</span> {stats['error']}</p>
        </div>

        <h2>2. Détails par fichier analysé</h2>
        <table>
            <thead>
                <tr>
                    <th>Fichier</th>
                    <th>Page 1 (Homonyme)</th>
                    <th>Identité / Alias</th>
                    <th>Détails des Alias (Section Identités)</th>
                    <th>Statut Final</th>
                </tr>
            </thead>
            <tbody>
    """

    for detail in file_details:
        filename = detail['filename']
        # Statut Page 1
        p1_status = ""
        if detail['p1_clean'] is None: p1_status = "Erreur"
        elif detail['p1_clean'] is True: p1_status = "Non (Clean)"
        else: p1_status = "OUI (Detecté)"

        # Liste alias
        alias_html = "<ul class='alias-list'>"
        has_alias_homonym = False
        if not detail['identities']:
             alias_html += "<li><em>Aucune section identité détectée</em></li>"
        else:
            for identity in detail['identities']:
                count = identity['count']
                badge = ""
                if count > 0:
                    badge = f"<span class='badge-homonym'>{count} homonyme(s)</span>"
                    has_alias_homonym = True
                else:
                    badge = "<span class='badge-clean'>0</span>"
                
                alias_html += f"<li>{identity['alias']} : {badge}</li>"
        alias_html += "</ul>"

        # Colonne Identité / Alias
        identity_html = ""
        id_info = detail.get('identity_check', {})
        main_id = id_info.get('main_identity', None)
        if main_id:
            identity_html += f"<strong>Page 1 :</strong> {main_id}<br>"
            if id_info.get('has_mismatch', False):
                identity_html += "<span class='badge-mismatch'>⚠ Non trouvé dans les alias</span>"
            elif id_info.get('has_identity_section', False):
                identity_html += "<span class='badge-clean'>✔ Présent dans les alias</span>"
        else:
            identity_html = "<em>N/A</em>"
        
        # Statut Final
        final_class = ""
        final_text = ""
        if detail.get('is_identity_error', False):
             final_class = "status-identity"
             final_text = "Erreur état civil"
        elif detail['is_manual']:
             final_class = "status-warning"
             final_text = "À vérifier"
        elif detail['p1_clean'] is None:
             final_class = "status-error"
             final_text = "Erreur"
        else:
             final_class = "status-ok"
             final_text = "OK"

        html_content += f"""
            <tr>
                <td>{filename}</td>
                <td>{p1_status}</td>
                <td>{identity_html}</td>
                <td>{alias_html}</td>
                <td class="{final_class}">{final_text}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    timestamp_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"rapport_traitement_{timestamp_filename}.html"
    report_path = os.path.join(destination_dir, report_filename)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return report_path
    except Exception as e:
        print(f"Erreur écriture rapport HTML: {e}")
        return None

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
    dir_identity_error = os.path.join(base_dest, "Erreur_Etat_civil")
    os.makedirs(dir_ok, exist_ok=True)
    os.makedirs(dir_manual, exist_ok=True)
    os.makedirs(dir_identity_error, exist_ok=True)

    # Lister les PDFs
    pdfs = [f for f in os.listdir(source_dir)
            if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(source_dir, f))]

    if not pdfs:
        log_callback("Aucun fichier PDF trouvé dans le dossier source.")
        return {"ok": 0, "manual": 0, "error": 0}

    log_callback(f"📂 {len(pdfs)} PDF(s) trouvé(s) dans '{source_dir}'\n")
    if destination_dir:
        log_callback(f"↪️  Destination : '{destination_dir}'\n")

    stats = {"ok": 0, "manual": 0, "error": 0, "identity_error": 0}
    file_details = []

    for filename in sorted(pdfs):
        filepath = os.path.join(source_dir, filename)
        
        # Logique 1 : Page 1 "Homonymes ... non"
        res_p1 = has_no_homonyme(filepath)
        
        # Extraction détaillée pour le rapport et Logique 2
        identities = extract_identities_details(filepath)
        
        # Logique 2 : Y a-t-il un homonyme dans les identités ?
        homonym_in_identities = any(i['count'] > 0 for i in identities)

        # Logique 3 : Vérification identité page 1 vs alias
        identity_check = check_identity_mismatch(filepath)

        destination_dir_final = dir_manual
        message = ""
        is_manual = False
        is_identity_error = False

        if res_p1 is None:
            # Erreur technique sur la lecture page 1
            destination_dir_final = dir_manual
            message = "⚠️  (erreur lecture)"
            stats["error"] += 1
            is_manual = True 
        elif identity_check['has_mismatch']:
            # Identité page 1 absente des alias → erreur état civil
            destination_dir_final = dir_identity_error
            message = "🔴 (erreur état civil)"
            stats["identity_error"] += 1
            is_identity_error = True
        elif res_p1 is False: # Page 1 dit "Homonyme" (ou pas "non")
            destination_dir_final = dir_manual
            message = "🔶 (detecté par page 1)"
            stats["manual"] += 1
            is_manual = True
        elif homonym_in_identities:
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

        # Store details for report
        file_details.append({
            'filename': filename,
            'p1_clean': res_p1, # True if "Non", False if homonym detected
            'identities': identities,
            'is_manual': is_manual,
            'is_identity_error': is_identity_error,
            'identity_check': identity_check
        })

        try:
            shutil.move(filepath, os.path.join(destination_dir_final, filename))
            log_callback(f"{message} {filename} → {os.path.basename(destination_dir_final)}/")
        except Exception as e:
            log_callback(f"❌ Erreur déplacement {filename}: {e}")

    # Generate HTML Report
    report_file = generate_html_report(base_dest, stats, file_details)
    if report_file:
         log_callback(f"\n📄 Rapport HTML généré : {os.path.basename(report_file)}")

    log_callback(f"\n{'='*50}")
    log_callback(f"📊 Résultat :")
    log_callback(f"   ✅ Pas d'homonyme     : {stats['ok']}")
    log_callback(f"   🔶 Homonymes détectés : {stats['manual']}")
    log_callback(f"   🔴 Erreur état civil  : {stats['identity_error']}")
    log_callback(f"   ⚠️  Erreurs            : {stats['error']}")
    log_callback(f"{'='*50}")
    
    return stats
