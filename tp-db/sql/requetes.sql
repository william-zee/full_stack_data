
SELECT 
    items.id,
    items.titre,
    items.tarif_jour,
    users.display_name AS proprietaire
FROM items
JOIN users ON items.owner_id = users.id
WHERE items.disponible = TRUE
ORDER BY items.id ASC;

/* Résultat obtenu :
 id |     titre      | tarif_jour | proprietaire 
----+----------------+------------+--------------
  1 | Vélo           |       5.00 | Alice
  2 | Perceuse       |       8.00 | Alice
  3 | Tente          |      12.00 | Bob
  4 | Appareil photo |      25.00 | Bob
(4 rows)
*/


SELECT 
    id,
    titre,
    tarif_jour,
    disponible
FROM items
WHERE titre ILIKE '%vélo%';

/* Résultat obtenu :
 id | titre | tarif_jour | disponible 
----+-------+------------+------------
  1 | Vélo  |       5.00 | t
(1 row)
*/



SELECT 
    items.id,
    items.titre,
    items.tarif_jour
FROM items
LEFT JOIN reservations ON items.id = reservations.item_id
WHERE reservations.id IS NULL;

/* Résultat obtenu :
 id |  titre   | tarif_jour 
----+----------+------------
  2 | Perceuse |       8.00
(1 row)
*/



SELECT 
    items.id,
    items.titre,
    COUNT(reservations.id) AS nb_reservations
FROM items
LEFT JOIN reservations ON items.id = reservations.item_id
GROUP BY items.id, items.titre
ORDER BY items.id ASC;

/* Résultat obtenu :
 id |     titre      | nb_reservations 
----+----------------+-----------------
  1 | Vélo           |               1
  2 | Perceuse       |               0
  3 | Tente          |               1
  4 | Appareil photo |               1
(4 rows)
*/



SELECT 
    users.display_name AS utilisateur,
    COUNT(items.id) AS nb_items_publies,
    ROUND(AVG(items.tarif_jour), 2) AS tarif_moyen
FROM users
JOIN items ON users.id = items.owner_id
GROUP BY users.id, users.display_name
ORDER BY nb_items_publies DESC, tarif_moyen DESC;

/* Résultat obtenu :
 utilisateur | nb_items_publies | tarif_moyen 
-------------+------------------+-------------
 Bob         |                2 |       18.50
 Alice       |                2 |        6.50
(2 rows)
*/



SELECT 
    reservations.id AS reservation_id,
    items.titre AS materiel,
    users.display_name AS emprunteur,
    reservations.date_debut,
    reservations.statut
FROM reservations
JOIN items ON reservations.item_id = items.id
JOIN users ON reservations.borrower_id = users.id
WHERE reservations.statut = 'active'
  AND reservations.date_debut > '2026-09-01'
ORDER BY reservations.date_debut ASC;

/* Résultat obtenu :
 reservation_id | materiel | emprunteur | date_debut | statut 
----------------+----------+------------+------------+--------
              3 | Tente    | Alice      | 2026-09-15 | active
(1 row)
*/



SELECT 
    id,
    titre,
    tarif_jour
FROM items
ORDER BY tarif_jour DESC
LIMIT 2 OFFSET 1;

/* Résultat obtenu :
 id |  titre   | tarif_jour 
----+----------+------------
  3 | Tente    |      12.00
  2 | Perceuse |       8.00
(2 rows)
*/



SELECT 
    reservations.id AS reservation_id,
    items.titre,
    items.tarif_jour,
    (reservations.date_fin - reservations.date_debut) AS nb_jours,
    ((reservations.date_fin - reservations.date_debut) * items.tarif_jour) AS ca_potentiel
FROM reservations
JOIN items ON reservations.item_id = items.id
WHERE reservations.statut = 'active'
ORDER BY reservations.id ASC;

/* Résultat obtenu :
 reservation_id | titre | tarif_jour | nb_jours | ca_potentiel 
----------------+-------+------------+----------+--------------
              3 | Tente |      12.00 |        5 |        60.00
(1 row)
*/