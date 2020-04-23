WITH accepted_entry AS
    (
        SELECT text, timestamp, id, post_id FROM entry
        WHERE (SELECT COUNT(*) FROM vote WHERE
            upvote = true
            AND entry_id = entry.id) >= 2
        GROUP BY post_id
        ORDER BY timestamp DESC
    ), hashtagged_post AS
    (
        SELECT post_id as id, (SELECT parent_id FROM post WHERE post.id = post_id) as parent_id
        FROM accepted_entry
        WHERE (SELECT COUNT(*) FROM hashtag_link WHERE
            entry_id = accepted_entry.id
            AND hashtag_id = (SELECT hashtag.id
                              FROM hashtag
                              WHERE hashtag.text = :tag))
    ), hashtagged_parent AS
    (
        SELECT DISTINCT COALESCE(parent_id, id, parent_id) as id
        FROM hashtagged_post
    )
SELECT accepted_entry.text, accepted_entry.id, (SELECT account_id FROM post WHERE post.id = hashtagged_parent.id), hashtagged_parent.id
FROM hashtagged_parent INNER JOIN accepted_entry
ON accepted_entry.post_id = hashtagged_parent.id
ORDER BY accepted_entry.timestamp DESC
