# clm/ocr_utils.py
"""
Utilitaires pour l'extraction de texte depuis des PDFs.
Stratégie :
  1. Essayer d'abord PyMuPDF (extraction directe, rapide)
  2. Si le texte extrait est trop court → le PDF est probablement scanné
  3. Passer à Tesseract OCR (convertit les pages en images puis lit le texte)
"""

import fitz          # PyMuPDF
import pytesseract
from PIL import Image
from django.conf import settings
import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Extrait le texte d'un PDF (bytes).
    
    Retourne un dict :
    {
        'text': str,           # Texte complet extrait
        'method': str,         # 'native' ou 'ocr'
        'pages': int,          # Nombre de pages
        'success': bool,
        'error': str | None
    }
    """
    result = {
        'text': '',
        'method': None,
        'pages': 0,
        'success': False,
        'error': None
    }

    try:
        # ── Étape 1 : Ouvrir le PDF avec PyMuPDF ──────────────────────────
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')
        result['pages'] = len(doc)
        
        # ── Étape 2 : Essayer l'extraction native ─────────────────────────
        native_text = ''
        for page in doc:
            native_text += page.get_text()
        
        # Heuristique : si on a plus de 100 caractères par page → c'est un PDF texte
        avg_chars_per_page = len(native_text.strip()) / max(result['pages'], 1)
        
        if avg_chars_per_page > 100:
            result['text'] = native_text.strip()
            result['method'] = 'native'
            result['success'] = True
            logger.info(f'[OCR] Extraction native réussie : {len(native_text)} caractères')
            return result
        
        # ── Étape 3 : PDF scanné → utiliser Tesseract OCR ─────────────────
        logger.info('[OCR] PDF scanné détecté → OCR Tesseract')
        
        # Configurer le chemin Tesseract si défini dans settings
        if getattr(settings, 'TESSERACT_CMD', None):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        
        lang = getattr(settings, 'TESSERACT_LANG', 'fra+eng')
        dpi  = getattr(settings, 'PDF_OCR_DPI', 300)
        
        ocr_text = ''
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Convertir la page PDF en image (matrice de pixels)
            mat = fitz.Matrix(dpi / 72, dpi / 72)   # 72 = DPI de base PDF
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convertir en image PIL
            img_bytes = pix.tobytes('png')
            img = Image.open(io.BytesIO(img_bytes))
            
            # OCR sur l'image
            page_text = pytesseract.image_to_string(img, lang=lang)
            ocr_text += f'\n--- Page {page_num + 1} ---\n{page_text}'
            
            logger.info(f'[OCR] Page {page_num + 1}/{len(doc)} traitée')
        
        result['text'] = ocr_text.strip()
        result['method'] = 'ocr'
        result['success'] = True
        logger.info(f'[OCR] OCR terminé : {len(ocr_text)} caractères')
        return result

    except Exception as e:
        logger.error(f'[OCR] Erreur extraction : {str(e)}')
        result['error'] = str(e)
        result['success'] = False
        return result