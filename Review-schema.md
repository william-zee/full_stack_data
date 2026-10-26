# Revue du Schéma v2 (GearShare)

| Point de contrôle | OK / KO | Ce que j'ai corrigé / Choix de conception |
|---|:---:|---|
| Chaque table a une clé primaire | **OK** | `pk_tags`, `pk_avis` (sur `id`) et `pk_item_tags` (composite `item_id, tag_id`). |
| Les clés étrangères sont déclarées avec REFERENCES | **OK** | Toutes déclarées avec `REFERENCES` explicites vers `items`, `tags` ou `reservations`. |
| Les ON DELETE sont explicites et cohérents avec le métier | **OK** | `ON DELETE CASCADE` choisi : supprimer un item supprime ses associations de tags et ses avis liés. |
| La règle « un seul avis par réservation » est garantie par une contrainte UNIQUE | **OK** | Garanti par `CONSTRAINT uq_avis_reservation UNIQUE (reservation_id)`. |
| La note est bornée par un CHECK (note BETWEEN 1 AND 5) | **OK** | Garanti par `CONSTRAINT ck_avis_note CHECK (note BETWEEN 1 AND 5)`. |
| La table de liaison item/tag a une clé primaire composite | **OK** | `CONSTRAINT pk_item_tags PRIMARY KEY (item_id, tag_id)`. |
| Le libellé de tag est UNIQUE | **OK** | `CONSTRAINT uq_tags_libelle UNIQUE (libelle)` + `ck_tags_libelle_lower` pour forcer les minuscules. |
| Les contraintes sont nommées | **OK** | Préfixes normalisés : `pk_`, `fk_`, `uq_`, `ck_`, `exclude_`. |
| Des index existent sur les clés étrangères | **OK** | `idx_item_tags_tag_id` créé explicitement ; `idx_avis_reservation_id` créé. |
| Le non-chevauchement est réellement garanti (contrainte) ou explicitement laissé à l'applicatif | **OK** | Garanti au niveau du SGBD avec l'extension `btree_gist` et une contrainte `EXCLUDE USING gist (item_id WITH =, daterange(date_debut, date_fin, '[]') WITH &&) WHERE (statut = 'active')`. |
| Aucun type flottant pour un montant, aucun TIMESTAMP sans fuseau | **OK** | `TIMESTAMPTZ` utilisé partout pour l'horodatage (`created_at`). |

### Précisions sur les règles mixtes base / applicatif :
* **Condition d'avis (statut 'terminee' et auteur = emprunteur) :** Une contrainte SQL pure (`CHECK`) ne peut pas faire de jointure pour inspecter le `statut` ou le `borrower_id` de la table `reservations`. Cette validation est donc confiée à la couche de service applicative (FastAPI / SQLAlchemy).