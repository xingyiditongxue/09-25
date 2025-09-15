#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
import time
from typing import List, Dict
import requests


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, max_chars: int = 1500, overlap: int = 200) -> List[str]:
    """
    Découpe naïve par caractères avec recouvrement.
    max_chars: taille cible d'un chunk
    overlap: recouvrement entre chunks (pour le contexte)
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        # recule pour overlap
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def get_embedding_ollama(ollama_base: str, text: str, model: str = "nomic-embed-text:v1.5") -> List[float]:
    url = f"{ollama_base.rstrip('/')}/api/embed"
    payload = {"model": model, "prompt": text}
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Ollama error {r.status_code}: {r.text}")
    data = r.json()
    if "embedding" not in data:
        raise RuntimeError(f"Ollama response missing 'embedding': {data}")
    return data["embedding"]


def qdrant_create_collection(qdrant_base: str, collection: str, size: int, distance: str = "Cosine") -> None:
    """
    Tente de créer la collection; si elle existe déjà, on ignore l'erreur.
    """
    url = f"{qdrant_base.rstrip('/')}/collections/{collection}"
    headers = {"Content-Type": "application/json"}
    payload = {"vectors": {"size": size, "distance": distance}}
    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
    # Qdrant renvoie 200 si créé, 409 si existe souvent avec un message d’erreur; on ne bloque pas.
    if r.status_code not in (200, 202):
        # Si la collection existe déjà, l’API peut répondre 409; on tolère.
        try:
            msg = r.json()
        except Exception:
            msg = r.text
        if r.status_code != 409:
            raise RuntimeError(f"Qdrant create collection error {r.status_code}: {msg}")


def qdrant_upsert_points(qdrant_base: str, collection: str, points: List[Dict]) -> None:
    url = f"{qdrant_base.rstrip('/')}/collections/{collection}/points"
    headers = {"Content-Type": "application/json"}
    payload = {"points": points}
    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=120)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Qdrant upsert error {r.status_code}: {r.text}")


def main():
    ap = argparse.ArgumentParser(description="Ingest .txt -> chunks -> Ollama embeddings -> Qdrant")
    ap.add_argument("txt_path", help="Chemin vers le fichier .txt")
    ap.add_argument("--collection", default="docs", help="Nom de la collection Qdrant (défaut: docs)")
    ap.add_argument("--qdrant", default="http://localhost:6333", help="Base URL Qdrant (défaut: http://localhost:6333)")
    ap.add_argument("--ollama", default="http://localhost:11434", help="Base URL Ollama (défaut: http://localhost:11434)")
    ap.add_argument("--model", default="nomic-embed-text:v1.5", help="Modèle embeddings Ollama (défaut: nomic-embed-text:v1.5)")
    ap.add_argument("--chunk-chars", type=int, default=1500, help="Taille max d’un chunk (caractères) (défaut: 1500)")
    ap.add_argument("--overlap", type=int, default=200, help="Recouvrement entre chunks (caractères) (défaut: 200)")
    ap.add_argument("--start-id", type=int, default=1, help="ID de départ pour les points (défaut: 1)")
    ap.add_argument("--batch-size", type=int, default=64, help="Taille des lots à upserter (défaut: 64)")
    args = ap.parse_args()

    if not os.path.isfile(args.txt_path):
        print(f"Fichier introuvable: {args.txt_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Lecture: {args.txt_path}")
    text = read_txt(args.txt_path)
    chunks = chunk_text(text, max_chars=args.chunk_chars, overlap=args.overlap)
    if not chunks:
        print("Aucun texte/chunk à traiter.", file=sys.stderr)
        sys.exit(1)

    print(f"Découpage: {len(chunks)} chunks")
    # 1er embedding pour déduire la dimension
    print("Génération embedding #0 pour déterminer la dimension…")
    first_emb = get_embedding_ollama(args.ollama, chunks[0], model=args.model)
    dim = len(first_emb)
    print(f"Dimension détectée: {dim}")

    # Créer la collection (Cosine par défaut)
    print(f"Création/validation de la collection '{args.collection}' sur Qdrant…")
    qdrant_create_collection(args.qdrant, args.collection, size=dim, distance="Cosine")

    # Upsert par lots
    next_id = args.start_id
    batch = []
    inserted = 0
    filename = os.path.basename(args.txt_path)

    # Insère le premier chunk déjà calculé
    batch.append({
        "id": next_id,
        "vector": first_emb,
        "payload": {"text": chunks[0], "filename": filename, "chunk_id": 0},
    })
    next_id += 1
    inserted += 1

    # Boucle sur le reste
    for idx in range(1, len(chunks)):
        emb = get_embedding_ollama(args.ollama, chunks[idx], model=args.model)
        batch.append({
            "id": next_id,
            "vector": emb,
            "payload": {"text": chunks[idx], "filename": filename, "chunk_id": idx},
        })
        next_id += 1
        inserted += 1

        if len(batch) >= args.batch_size:
            qdrant_upsert_points(args.qdrant, args.collection, batch)
            print(f"Upsert {len(batch)} points (total: {inserted})")
            batch.clear()
            # petit throttle doux
            time.sleep(0.05)

    # Envoi du dernier lot
    if batch:
        qdrant_upsert_points(args.qdrant, args.collection, batch)
        print(f"Upsert final {len(batch)} points (total: {inserted})")

    print("Terminé ✅")


if __name__ == "__main__":
    main()
