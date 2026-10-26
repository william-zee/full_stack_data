CREATE EXTENSION IF NOT EXISTS btree_gist;


CREATE TABLE IF NOT EXISTS tags (
    id SERIAL,
    libelle VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_tags PRIMARY KEY (id),
    CONSTRAINT uq_tags_libelle UNIQUE (libelle),
    CONSTRAINT ck_tags_libelle_lower CHECK (libelle = lower(libelle))
);


CREATE TABLE IF NOT EXISTS item_tags (
    item_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_item_tags PRIMARY KEY (item_id, tag_id),
    CONSTRAINT fk_item_tags_item FOREIGN KEY (item_id) 
        REFERENCES items(id) ON DELETE CASCADE,
    CONSTRAINT fk_item_tags_tag FOREIGN KEY (tag_id) 
        REFERENCES tags(id) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_item_tags_tag_id ON item_tags(tag_id);


CREATE TABLE IF NOT EXISTS avis (
    id SERIAL,
    reservation_id INTEGER NOT NULL,
    note SMALLINT NOT NULL,
    commentaire TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_avis PRIMARY KEY (id),
    CONSTRAINT uq_avis_reservation UNIQUE (reservation_id),
    CONSTRAINT fk_avis_reservation FOREIGN KEY (reservation_id) 
        REFERENCES reservations(id) ON DELETE CASCADE,
    CONSTRAINT ck_avis_note CHECK (note BETWEEN 1 AND 5)
);

CREATE INDEX IF NOT EXISTS idx_avis_reservation_id ON avis(reservation_id);


ALTER TABLE reservations
    DROP CONSTRAINT IF EXISTS exclude_reservations_chevauchement;

ALTER TABLE reservations
    ADD CONSTRAINT exclude_reservations_chevauchement
    EXCLUDE USING gist (
        item_id WITH =,
        daterange(date_debut, date_fin, '[]') WITH &&
    )
    WHERE (statut = 'active');