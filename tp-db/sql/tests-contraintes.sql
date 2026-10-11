INSERT INTO avis (reservation_id, note, commentaire)
VALUES (1, 6, 'Incroyable matériel');

-- Test 2 : Deux avis sur la même réservation (doit violer uq_avis_reservation)
-- On insère un premier avis valide, puis on tente un doublon
INSERT INTO avis (reservation_id, note, commentaire)
VALUES (1, 5, 'Premier avis parfait');

-- Attendu : ERROR: duplicate key value violates unique constraint "uq_avis_reservation"
INSERT INTO avis (reservation_id, note, commentaire)
VALUES (1, 4, 'Deuxième avis interdit');

-- Test 3 : Deux tags avec le même libellé (doit violer uq_tags_libelle)
INSERT INTO tags (libelle) VALUES ('bricolage');

-- Attendu : ERROR: duplicate key value violates unique constraint "uq_tags_libelle"
INSERT INTO tags (libelle) VALUES ('bricolage');

-- Test 4 : Avis sur une réservation inexistante (doit violer fk_avis_reservation)
-- Attendu : ERROR: insert or update on table "avis" violates foreign key constraint "fk_avis_reservation"
INSERT INTO avis (reservation_id, note, commentaire)
VALUES (999999, 3, 'Réservation fantôme');

-- Test 5 (Bonus) : Deux réservations actives qui se chevauchent sur le même item
-- (doit violer exclude_reservations_chevauchement)
INSERT INTO reservations (item_id, borrower_id, date_debut, date_fin, statut)
VALUES (1, 1, '2026-12-01', '2026-12-10', 'active');

-- Attendu : ERROR: conflicting key value violates exclusion constraint "exclude_reservations_chevauchement"
INSERT INTO reservations (item_id, borrower_id, date_debut, date_fin, statut)
VALUES (1, 2, '2026-12-05', '2026-12-15', 'active');