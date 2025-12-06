 import streamlit as st
 import google.generativeai as genai
 import time
 import re
+import asyncio
+import io
+
+import edge_tts
 from gtts import gTTS
 from streamlit_mic_recorder import mic_recorder
-import io
 
 # --- IMPORTATION DES DONNÉES ---
 try:
     from prompts import SCENARIOS
     from glossaire_data import GLOSSAIRE
 except ImportError:
     st.error("🚨 Erreur critique : Les fichiers 'prompts.py' ou 'glossaire_data.py' sont manquants.")
     st.stop()
 
 # --- CONFIGURATION DE LA PAGE ---
 st.set_page_config(
     page_title="Campus Relation Client",
     layout="wide",
     page_icon="🎧",
     initial_sidebar_state="expanded",
     menu_items={
         'About': "Simulateur pédagogique CRCD - @croquison 2025"
     }
 )
 
 # --- CSS / DESIGN & ACCESSIBILITÉ ---
 st.markdown("""
 <style>
     /* TYPOGRAPHIE & LISIBILITÉ */
     html, body, [class*="css"] {
@@ -115,57 +118,77 @@ def afficher_barometre(score):
     col_jauge, col_verdict = st.columns([3, 1])
     with col_jauge:
         st.progress(score / 100)
         # CORRECTION ICI : Ajout des accolades fermantes manquantes
         if score < 50: 
             st.error(f"🔴 {score}/100 - Insuffisant")
         elif score < 80: 
             st.warning(f"🟠 {score}/100 - En acquisition")
         else: 
             st.success(f"🟢 {score}/100 - Maîtrisé")
     with col_verdict:
         st.markdown(f"<div class='big-score'>{score}</div>", unsafe_allow_html=True)
 
 def transcrire_audio(audio_bytes):
     try:
         model = genai.GenerativeModel('gemini-2.0-flash')
         config = genai.types.GenerationConfig(temperature=0.0)
         response = model.generate_content(
             ["Transcris exactement en français. Si silence, réponds '...'", {"mime_type": "audio/webm", "data": audio_bytes}], 
             generation_config=config
         )
         t = response.text.strip()
         return None if t in ["...", ""] else t
     except: return None
 
+async def _parler_async(texte, voix):
+    communicate = edge_tts.Communicate(texte, voice=voix)
+    fp = io.BytesIO()
+    async for chunk in communicate.stream():
+        if chunk["type"] == "audio":
+            fp.write(chunk["data"])
+    fp.seek(0)
+    return fp
+
+
 def parler(texte, langue='fr'):
+    voix = "fr-FR-DeniseNeural" if langue.startswith('fr') else "en-US-JennyNeural"
     try:
-        tts = gTTS(text=texte, lang=langue, slow=False)
-        fp = io.BytesIO()
-        tts.write_to_fp(fp)
+        loop = asyncio.new_event_loop()
+        asyncio.set_event_loop(loop)
+        fp = loop.run_until_complete(_parler_async(texte, voix))
+        loop.close()
         return fp
-    except: return None
+    except:
+        try:
+            tts = gTTS(text=texte, lang=langue, slow=False)
+            fp = io.BytesIO()
+            tts.write_to_fp(fp)
+            fp.seek(0)
+            return fp
+        except:
+            return None
 
 def obtenir_reponse_gemini(msg, hist, prompt):
     try:
         model = genai.GenerativeModel('gemini-2.0-flash')
         h = [{"role": "user", "parts": [prompt]}, {"role": "model", "parts": ["Compris."]}]
         for m in hist:
             if m["role"]!="system": h.append({"role":("user" if m["role"]=="user" else "model"), "parts":[m["content"]]})
         return model.start_chat(history=h).send_message(msg).text
     except Exception as e: return f"Erreur : {e}"
 
 def analyse_coach(txt, prompt):
     try:
         model = genai.GenerativeModel('gemini-2.0-flash')
         return model.generate_content(prompt + "\n\nTRANSCRIPTION:\n" + txt).text
     except: return "Erreur analyse."
 
 def afficher_footer():
     st.markdown('<div class="footer">@croquison Création pédagogique 2025 - Tous droits réservés</div>', unsafe_allow_html=True)
 
 @st.dialog("❓ Guide Rapide")
 def afficher_notice():
     st.markdown("### 🎧 Comment s'entraîner ?\n1. **Choisissez un client**.\n2. **Cliquez sur 'Décrocher'**.\n3. **Parlez au client**.\n4. **Analysez** vos résultats.")
 
 # --- NAVIGATION ---
 if "page" not in st.session_state: st.session_state.page = "home"
