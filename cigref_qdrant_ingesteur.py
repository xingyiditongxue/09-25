Voici ce que fait ton script — en clair, c’est un **ingesteur RAG** : il lit un texte (ou un PDF), le découpe en morceaux, génère des **embeddings via Ollama**, puis **upsert** ces vecteurs dans **Qdrant** avec des métadonnées.

# En résumé

* **Entrée** : soit une **chaîne de texte**, soit un **fichier .txt/.pdf**.
* **Découpage** : split naïf en **chunks de 1500 caractères** avec **200 de chevauchement** (paramétrables).
* **Embeddings** : appel HTTP à **Ollama** (`/api/embeddings`) avec le modèle `nomic-embed-text:v1.5` (modifiable).
* **Qdrant** :

  * Détecte **la dimension** des vecteurs à partir du **premier chunk**.
  * **Crée la collection** si elle n’existe pas (distance **COSINE**).
  * Crée un **index de payload** sur `doc_id` (keyword) si possible.
  * **Vérifie si le doc existe** déjà (via `count`/`scroll`), et **s’arrête** si `--fail-if-exists` (ou, dans ton code actuel, s’arrête **toujours** quand il détecte l’existence).
  * Calcule le **prochain `chunk_id`** pour reprendre un doc partiellement ingéré.
  * Envoie les points par **lots** (`--batch-size`, pause `--sleep-ms`).

# Métadonnées stockées par chunk

Chaque point contient :

* `id` : **UUID v5** déterministe sur `"{doc_id}:{chunk_id}"` (pratique pour idempotence).
* `vector` : l’embedding du chunk.
* `payload` : `{ "text": <chunk>, "doc_id": <doc_id>, "chunk_id": <int> }`.

# Comment est déterminé `doc_id`

* Si `--doc` est fourni → utilisé tel quel.
* Si l’entrée est un **fichier** → nom de fichier **sans extension**.
* Si l’entrée est **du texte brut** → `text-<hash>` où `<hash>` = SHA-1 des arguments (stable).

# Comportement « existence »

* `doc_exists()` cherche **au moins un point** avec `doc_id` donné.
* Si trouvé, le script **termine immédiatement** (code `0`) après t’avertir :

  > ⚠️ Le document 'X' existe déjà…
  > *(Note : tu as un flag `--fail-if-exists` dans l’aide, mais ton code actuel s’arrête même sans ce flag. Si tu veux autoriser l’**append** quand le doc existe, enlève le `sys.exit(0)` et repose-toi sur `get_next_chunk_id`.)*

# Paramètres importants (avec défauts)

* `--ollama` : `http://localhost:11434/api/embeddings`
* `--model` : `nomic-embed-text:v1.5`
* `--qhost` / `--qport` : `localhost:6333`
* `--collection` : `docFruits`
* `--chunk-chars` : `1500`
* `--overlap` : `200`
* `--batch-size` : `32`
* `--sleep-ms` : `50`

# Exemples d’usage

1. **Ingestion d’un PDF** (collection par défaut)

```bash
python3 ingest.py ./docs/guide.pdf
```

2. **Ingestion d’un .txt** avec doc_id explicite, collection custom

```bash
python3 ingest.py notes.txt --doc projet-notes --collection myKB
```

3. **Texte brut** passé en argument

```bash
python3 ingest.py "Voici un texte à vectoriser dans Qdrant."
```

4. **Changer le modèle et l’URL d’Ollama**

```bash
python3 ingest.py rapport.pdf --model nomic-embed-text:v1.5 --ollama http://127.0.0.1:11434/api/embeddings
```

# Sortie / logs typiques

* Nombre de chunks, `doc_id`, dimension détectée, création/validation de la collection, progression des **upserts par lot**.
* À la fin, un **JSON récapitulatif** :

```json
{
  "status": "ok",
  "collection": "docFruits",
  "doc_id": "guide",
  "chunks_added": 42,
  "first_chunk_id": 0,
  "last_chunk_id": 41
}
```

# Ce que le script **ne** fait pas

* Pas de **nettoyage avancé** du texte PDF (mise en page, colonnes, tableaux).
* Pas de **détection de langue** ni de **normalisation** (lowercasing, strip accents, etc.).
* Pas de **gestion d’embeddings ratés** par retry/backoff (si Ollama renvoie une erreur, il lève).
* Pas de **réindexation**/mise à jour si un chunk change (IDs déterministes aident, mais pas de diff).

# Idées d’amélioration (si tu veux aller plus loin)

* Rendre `--fail-if-exists` effectif : ne `sys.exit(0)` que si le flag est présent ; sinon, **append** via `get_next_chunk_id`.
* Ajouter un **retry** exponentiel sur l’appel embeddings et les upserts Qdrant.
* Supporter un **pré-traitement PDF** (ex. `pypdf` + `pdfminer.six`, ou `unstructured`/`textract`) pour extraire plus proprement.
* Tracer un **hash de chunk** dans le payload (`chunk_sha1`) pour éviter les doublons exacts.
* Permettre `--distance` (COSINE, DOT, EUCLIDEAN) et **vérifier** la compatibilité de taille/distance si la collection existe.

Si tu veux, je peux te proposer un mini correctif pour que `--fail-if-exists` se comporte comme attendu (existence → exit **seulement** si le flag est fourni) et que l’append fonctionne autrement.
