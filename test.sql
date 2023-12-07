
-- liste des utilisateur qui on des cartes que je cherche
SELECT uid FROM binder WHERE uid != 443471145149399069 AND searching = false AND card IN (
    SELECT card FROM binder WHERE uid = 443471145149399069 AND searching = True
    )
-- parmis ces utilisateurs les utilisateurs qui cherche des cartes que je possede 

 



 -- liste des utilisateurs qui ont des cartes que je cherche
SELECT uid
FROM binder
WHERE uid != 443471145149399069
  AND searching = 0
  AND card IN (
      SELECT card
      FROM binder
      WHERE uid = 443471145149399069
        AND searching = 1
  )

-- parmi ces utilisateurs, les utilisateurs qui cherchent des cartes que je possède
AND uid IN (
    SELECT uid
    FROM binder
    WHERE searching = 1 AND card IN (
        SELECT card
        FROM binder
        WHERE uid = 443471145149399069
          AND searching = 0
    )
);

-- les carte que le mec cherche que je possede
SELECT card FROM binder WHERE uid = his_id 
AND searching = 1 
AND card IN(SELECT card FROM binder WHERE uid = my_id AND searching = 0
);