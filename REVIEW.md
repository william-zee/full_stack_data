# Revue d'implémentation — Ressource Reservations

## Tableau de contrôle

| Point de contrôle | OK / KO | Ce que j'ai vérifié / corrigé |
| :--- | :---: | :--- |
| **Les codes de statut correspondent à la spec (201, 404, 409)** | **OK** | Vérifié : `POST ""` renvoie explicitement `status.HTTP_201_CREATED`. L'annulation (`/annuler`) gère le 404 sur ID inexistant et lève un `HTTP_409_CONFLICT` si le statut est déjà `"annulee"`. |
| **`response_model` présent sur les 4 routes** | **OK** | Vérifié : chaque route dispose de son filtre de sortie (`ReservationRead` ou `list[ReservationRead]`). Aucune fuite de données internes. |
| **La validation `date_fin > date_debut` est bien dans le schéma Pydantic** | **OK** | Contrôlé : l'agent a utilisé le décorateur `@model_validator(mode="after")` (syntaxe Pydantic v2) plutôt qu'un vieux validateur v1 `@validator` ou un `if` manuel dans le routeur. L'erreur `ValueError` est automatiquement interceptée par FastAPI en statut 422. |
| **Le router n'accède pas au stockage de `items`** | **OK** | Vérifié : `RESERVATIONS` est un dictionnaire dédié et indépendant dans `reservations.py`. Aucun import de `FAKE_DB` depuis `items.py`. |
| **Pas d'`async def` sans `await`** | **OK** | **Point de vigilance :** Les agents ont souvent le réflexe de typer les endpoints en `async def`. Vérifié que toutes les routes utilisent `def` synchrone classique, évitant ainsi de bloquer l'event loop asyncio pour des opérations en mémoire. |
| **Aucune dépendance ajoutée dans requirements.txt** | **OK** | Aucun package superflu n'a été installé. Tout repose sur `datetime`, `typing` (bibliothèque standard) et les versions existantes de `pydantic` et `fastapi`. |
| **Les routes littérales sont déclarées avant les routes paramétrées** | **OK** | Contrôlé : `POST ""` et `GET ""` sont déclarées en tête de fichier avant les routes paramétrées par `/{reservation_id}` pour éliminer tout risque d'ambiguïté de capture de chemin. |
| **Réponse cohérente pour `POST /reservations/999/annuler`** | **OK** | Testé : l'absence de l'ID 999 déclenche bien une `HTTPException(404)` et ne provoque ni crash serveur (`KeyError`) ni conflit 409 prématuré. |

## Notes sur l'intégration
* L'agent Copilot n'avait pas modifié `app/main.py`. L'import et l'enregistrement du routeur (`app.include_router(reservations.router)`) ont été réalisés manuellement pour éviter l'erreur `NameError: name 'reservations' is not defined`.


## Notes sur gearshare
Pour GearShare, supprimer un compte ne doit jamais effacer l'historique des réservations (prêts reçus ou consentis) afin de préserver la traçabilité légale et comptable en cas de litige. Nous retenons donc l'interdiction de suppression physique (`RESTRICT`) en présence de réservations liées, au profit d'une suppression logique (*soft delete* / anonymisation) qui désactive le compte et retire le matériel du catalogue tout en conservant l'intégrité des contrats passés. 



# Mesures de performances et indexation (PostgreSQL)

## 1. Recherche exacte : `titre = 'Item de test 123456'`

* **Sans index :**
  * Type de nœud : `Seq Scan`
  * Temps d'exécution : ~22.4 ms
* **Avec index (`idx_items_titre`) :**
  * Type de nœud : `Index Scan`
  * Temps d'exécution : ~0.06 ms
* **Facteur d'accélération :** ~370x plus rapide.

---

## 2. Cas subtils

### (a) Recherche avec joker en tête (`titre LIKE '%123456'`)
* **Type de nœud :** `Seq Scan`
* **Explication :** Un index B-tree ordonne les données de gauche à droite ; sans préfixe fixe de départ, le moteur ne peut pas naviguer dans l'arbre et doit scanner séquentiellement toute la table.

### (b) Filtre sur colonne booléenne (`disponible`)
* **Filtre `disponible = TRUE` :** `Seq Scan`. L'index est ignoré car la condition ramène quasiment 100 % des lignes de la table ; un parcours séquentiel est alors moins coûteux en E/S.
* **Filtre `disponible = FALSE` :** `Bitmap Index Scan` / `Index Scan`. La condition est très sélective (très peu de lignes), l'index devient donc optimal pour cibler immédiatement les bons enregistrements.

---

## 3. Bonus : Joker en fin de chaîne (`titre LIKE 'Item de test 12345%'`)
* **Type de nœud :** `Index Scan` (ou `Bitmap Index Scan`).
* **Explication :** Le préfixe étant constant, le B-tree peut cibler directement le début de l'intervalle et parcourir les clés jusqu'à la fin de la plage sans lire toute la table.